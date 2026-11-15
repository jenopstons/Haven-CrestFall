# Generic count HUD. Its icon is an independent UI binding, so the counter
# can display a project-specific resource without requiring a coin type.
_apply_pose(self, _load_pose(UI_CONFIG['counter']['icon']))
self.z = 100
self.label = text('0', 0, 0)
self.label.fontSize = UI_CONFIG['counter']['fontSize']
self.label.color = '#ffffff'
_apply_game_font(self.label)
self.label.halign = 'left'
self.label.valign = 'middle'
self.label.z = 101
self.backdrop = CounterBackdrop()
self.shownCount = -1
