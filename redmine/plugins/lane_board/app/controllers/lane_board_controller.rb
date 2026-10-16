class LaneBoardController < ApplicationController
  before_action :find_project_by_project_id, :authorize

  # Reads only: nothing here writes an issue, a field or a relation.
  def index
    @lane_field = IssueCustomField.find_by(name: 'Lane')
    return if @lane_field.nil?

    @points_field = IssueCustomField.find_by(name: 'Points')
    @statuses = IssueStatus.sorted.to_a
    issues = Issue.visible.where(project_id: @project.self_and_descendants.ids)
                  .includes(:status, :project, :relations_to, :custom_values).to_a
    @lanes = issues.group_by { |i| i.custom_field_value(@lane_field).presence || '(no lane)' }.sort.to_h
  end

  helper_method :ready?, :points, :total

  # nil when the issue has no estimate, or there is no Points field.
  def points(issue)
    value = @points_field && issue.custom_field_value(@points_field)
    value.blank? ? nil : value.to_i
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
