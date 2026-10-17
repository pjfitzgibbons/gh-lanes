class LaneBoardController < ApplicationController
  before_action :find_project_by_project_id, :authorize

  # Reads only: nothing here writes an issue, a field or a relation.
  def index
    @lane_field = IssueCustomField.find_by(name: 'Lane')
    return if @lane_field.nil?

    @points_field = IssueCustomField.find_by(name: 'Points')
    # Icebox is visible but unscheduled (F1): no column, and nothing in a lane's points.
    @statuses = IssueStatus.sorted.where.not(name: 'Icebox').to_a
    issues = Issue.visible.where(project_id: @project.self_and_descendants.ids, status_id: @statuses.map(&:id))
                  .includes(:status, :project, :custom_values, relations_to: { issue_from: :status }).to_a
    @lanes = issues.group_by { |i| field_value(i, @lane_field).presence || '(no lane)' }.sort.to_h
  end

  helper_method :ready?, :points, :total

  # nil when the issue has no estimate, there is no Points field, or the user may not see it.
  def points(issue)
    value = field_value(issue, @points_field)
    value.blank? ? nil : value.to_i
  end

  # The field's value, or nil when the user may not see the field in the issue's project:
  # the check Issue#visible_custom_field_values makes, cached per field and project.
  def field_value(issue, field)
    return nil if field.nil?

    @field_visible ||= {}
    visible = @field_visible.fetch([field.id, issue.project_id]) do |key|
      @field_visible[key] = field.visible_by?(issue.project, User.current)
    end
    visible ? issue.custom_field_value(field) : nil
  end

  # Sum of the open leaves, so a parent never double-counts its children (A5).
  def total(issues)
    issues.reject(&:closed?).select(&:leaf?).sum { |i| points(i) || 0 }
  end

  # Ready: open, and every issue that blocks it is closed.
  def ready?(issue)
    !issue.closed? &&
      issue.relations_to.select { |r| r.relation_type == 'blocks' }.all? { |r| r.issue_from.closed? }
  end
end
