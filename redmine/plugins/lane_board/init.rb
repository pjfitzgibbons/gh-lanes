Redmine::Plugin.register :lane_board do
  name 'Lane board'
  version '1.0.0'
  project_module :lane_board do
    permission :view_lane_board, { lane_board: [:index] }, read: true
  end
  menu :project_menu, :lane_board, { controller: 'lane_board', action: 'index' },
       caption: 'Lanes', param: :project_id
end
