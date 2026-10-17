# Backfills, once, the history import.rb left out: each issue's commits, its merged pull requests
# and its status changes. Run in the container, from the gh-plan checkout:
#   { echo '{"gh-plan":'
#     gh pr list -R pjfitzgibbons/gh-plan --state merged --limit 200 \
#       --json number,title,url,mergedAt,headRefName
#     echo ',"tempotag":'
#     gh pr list -R pjfitzgibbons/tempotag --state merged --limit 200 \
#       --json number,title,url,mergedAt,headRefName,closingIssuesReferences
#     echo ',"tempotag-issues":'
#     gh issue list -R pjfitzgibbons/tempotag --state all --limit 100 --json number,createdAt
#     echo '}'; } > .tmp/backfill.json
#   docker compose -f redmine/compose.yml exec -T -u redmine redmine \
#     bin/rails runner /setup/backfill.rb [--dry-run] < .tmp/backfill.json
#
# - Commits. It fetches each repository's commits, then links each to the issue whose Old ID it
#   names: a pl-id in either repo, or #<n> in tempotag, which was its GitHub issue. Redmine's own
#   keyword scan is off for the fetch: the old messages number GitHub issues, so "Closes #3" would
#   close Redmine's #3.
# - Pull requests. A note on each issue a merged PR names, dated when it merged: in gh-plan by a
#   pl-id in its branch or title, in tempotag by the issues it closes or the number in its branch.
#   The issue's Pull requests field links them all, so they show at its top.
# - Status. A gh-plan issue's status changes are its item file's, one journal per commit on
#   origin/main that changed the file's status, dated by that commit. A tempotag issue closes on
#   its GitHub issue's closedAt. Each issue is backdated to its item's first commit (gh-plan) or
#   its GitHub issue's createdAt (tempotag). An issue whose item changed status after the import
#   takes the item's last status, and a closed issue with no start date gets one from its history.
#
# Every journal is peter's and carries a note naming its evidence; a journal whose note an issue
# already has is not made again, so a second run makes nothing. It runs in one transaction with
# mail off; --dry-run does the whole backfill, prints it and rolls it back. It reads no credential.

require 'json'
require 'open3'

REPOS = { 'gh-plan' => '/repos/gh-plan.git', 'tempotag' => '/repos/tempotag.git' }.freeze
REF = 'origin/main'.freeze
ZONE = ActiveSupport::TimeZone['America/Los_Angeles']
STATUSES = { 'Todo' => 'New', 'In Progress' => 'In Progress', 'Done' => 'Closed', 'Icebox' => 'Icebox' }.freeze
PL_ID = /\bpl-[a-z]{5}\b/

MODE = ARGV.first
abort "backfill: unknown argument #{MODE}; use --dry-run" unless [nil, '--dry-run'].include?(MODE)

def git(*args)
  out, status = Open3.capture2('git', "--git-dir=#{REPOS['gh-plan']}", *args)
  abort "backfill: git #{args.join(' ')} failed" unless status.success?
  out
end

def day(time) = time&.in_time_zone(ZONE)&.to_date

OLD_ID = IssueCustomField.find_by(name: 'Old ID') || abort('backfill: no Old ID field; run setup.rb')
ISSUES = Issue.joins(:custom_values).where(custom_values: { custom_field_id: OLD_ID.id })
              .where.not(custom_values: { value: [nil, ''] }).includes(:custom_values)
              .to_h { |issue| [issue.custom_field_value(OLD_ID), issue] }
PULL_REQUESTS = IssueCustomField.find_by(name: 'Pull requests') || abort('backfill: no Pull requests field; run setup.rb')
PETER = User.find_by(login: 'peter') || abort('backfill: no user peter')

# A journal on the issue, dated, with a note naming its evidence; nil when the note is there already.
def journal(issue, time, notes, status: nil)
  return if issue.journals.where(notes: notes).exists?

  record = Journal.new(journalized: issue, user: PETER, created_on: time, notes: notes)
  if status
    record.details << JournalDetail.new(property: 'attr', prop_key: 'status_id',
                                        old_value: status.first.id.to_s, value: status.last.id.to_s)
  end
  record.save!
  record
end

def link_commits
  Changeset.skip_callback(:create, :after, :scan_for_issues)
  made = 0
  REPOS.each_key do |project|
    repository = Project.find_by!(identifier: project).repository || abort("backfill: #{project} has no repository")
    repository.fetch_changesets
    puts "#{project}: #{repository.changesets.count} commits"
    repository.changesets.includes(:issues).each do |changeset|
      ids = changeset.comments.to_s.scan(PL_ID)
      ids += changeset.comments.to_s.scan(/#(\d+)\b/).flatten.map { |n| "tempotag##{n}" } if project == 'tempotag'
      ids.uniq.filter_map { |id| ISSUES[id] }.each do |issue|
        next if changeset.issues.include?(issue)

        changeset.issues << issue
        made += 1
        puts "linked #{changeset.scmid[0, 7]} to ##{issue.id} #{issue.custom_field_value(OLD_ID)}"
      end
    end
  end
  made
end

def pull_request_notes(input)
  made = 0
  links = Hash.new { |hash, issue| hash[issue] = [] }
  { 'gh-plan' => input.fetch('gh-plan'), 'tempotag' => input.fetch('tempotag') }.each do |project, prs|
    prs.each do |pr|
      ids = if project == 'gh-plan'
              "#{pr['headRefName']} #{pr['title']}".scan(PL_ID)
            else
              numbers = pr.fetch('closingIssuesReferences', []).map { |ref| ref['number'] }
              numbers << Regexp.last_match(1).to_i if pr['headRefName'] =~ %r{\A\w+/(\d+)-}
              numbers.map { |n| "tempotag##{n}" }
            end
      ids.uniq.filter_map { |id| ISSUES[id] }.each do |issue|
        links[issue] << [Time.iso8601(pr.fetch('mergedAt')), "[#{project}##{pr['number']}](#{pr['url']})"]
        notes = "Merged [#{project}##{pr['number']}](#{pr['url']}): #{pr['title']}"
        next unless journal(issue, Time.iso8601(pr.fetch('mergedAt')), notes)

        made += 1
        puts "noted #{project}##{pr['number']} on ##{issue.id} #{issue.custom_field_value(OLD_ID)}"
      end
    end
  end
  links.each { |issue, prs| made += pull_requests_field(issue, prs.sort.map(&:last).join(', ')) }
  made
end

# The Pull requests field holds each merged PR's link, oldest first. It is set without a journal:
# the notes already date each PR.
def pull_requests_field(issue, value)
  record = CustomValue.find_or_initialize_by(customized: issue, custom_field: PULL_REQUESTS)
  return 0 if record.value == value

  record.update!(value: value)
  puts "##{issue.id} Pull requests: #{value}"
  1
end

# Each commit on origin/main that changed the item's status, oldest first, as [sha, time, subject, status].
def status_commits(id)
  paths = [".tracker/items/#{id}.md", ".tracker/archive/#{id}.md"]
  git('log', REF, '--reverse', '--format=%H%x09%cI%x09%s', '--', *paths).lines(chomp: true).filter_map do |line|
    sha, time, subject = line.split("\t", 3)
    text = paths.lazy.map { |path| Open3.capture2('git', "--git-dir=#{REPOS['gh-plan']}", 'show', "#{sha}:#{path}", err: File::NULL) }
                .find { |_, status| status.success? }&.first
    next unless text

    status = text[/^status: *(.+)$/, 1]&.strip || 'Icebox'
    [sha, Time.iso8601(time), subject, IssueStatus.find_by!(name: STATUSES.fetch(status))]
  end
end

def gh_plan_history(issue, id)
  commits = status_commits(id)
  abort "backfill: #{id} has no commits on #{REF}" if commits.empty?

  backdate(issue, commits.first[1])
  made = 0
  commits.each_cons(2) do |(_, _, _, before), (sha, time, subject, after)|
    next if before == after

    next unless journal(issue, time, "From commit #{sha[0, 7]}: #{subject}", status: [before, after])

    made += 1
    puts "##{issue.id} #{id} #{before.name} -> #{after.name} #{day(time)} #{sha[0, 7]}"
  end
  # An item merged Done after the import: the issue takes the status its last journal gave it.
  sha, time, _, last = commits.last
  return made if last == issue.status

  issue.update_columns(status_id: last.id, closed_on: last.is_closed? ? time : nil)
  issue.update_columns(due_date: day(time)) if last.is_closed?
  puts "##{issue.id} #{id} is now #{last.name}, from #{sha[0, 7]}"
  made + 1
end

def tempotag_history(issue, github)
  backdate(issue, Time.iso8601(github.fetch('createdAt')))
  return 0 unless issue.closed? && issue.closed_on

  new = IssueStatus.find_by!(name: 'New')
  return 0 unless journal(issue, issue.closed_on, "Closed on GitHub as tempotag##{github['number']}", status: [new, issue.status])

  puts "##{issue.id} tempotag##{github['number']} New -> #{issue.status.name} #{day(issue.closed_on)}"
  1
end

def backdate(issue, time)
  return if issue.created_on <= time

  issue.update_columns(created_on: time)
end

# A closed issue with no start date gets one from its history: the day it went In Progress, or else
# the day it closed. A missing due date is the day it closed.
def date_closed(issue)
  return 0 unless issue.closed? && issue.closed_on && issue.start_date.nil?

  started = issue.journals.joins(:details).where(journal_details: { prop_key: 'status_id', value: '2' })
                 .minimum(:created_on)
  issue.update_columns(start_date: day(started) || day(issue.closed_on), due_date: issue.due_date || day(issue.closed_on))
  puts "dated ##{issue.id} #{issue.start_date}..#{issue.due_date}"
  1
end

def status_history(input)
  github = input.fetch('tempotag-issues').to_h { |i| ["tempotag##{i['number']}", i] }
  made = 0
  ISSUES.sort_by { |_, issue| issue.id }.each do |id, issue|
    made += if id.start_with?('pl-')
              gh_plan_history(issue, id)
            else
              tempotag_history(issue, github.fetch(id) { abort "backfill: #{id} is not in the GitHub issues on stdin" })
            end
    made += date_closed(issue.reload)
  end
  made
end

text = $stdin.read
abort 'backfill: no JSON on stdin; see the top of backfill.rb' if text.strip.empty?
input = JSON.parse(text)

User.current = PETER
# Mail goes out from jobs that run after the transaction, so it is off for the whole run.
ActionMailer::Base.perform_deliveries = false
made = nil
ActiveRecord::Base.transaction do
  made = link_commits + status_history(input) + pull_request_notes(input)
  raise ActiveRecord::Rollback if MODE == '--dry-run'
end
puts MODE == '--dry-run' ? "dry run: #{made} to make, nothing written" : "#{made} made"
