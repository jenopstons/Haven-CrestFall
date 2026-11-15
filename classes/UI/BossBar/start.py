# A boss's health bar at the top of the screen, with its name above it in the same dark panel.
self.z = 99
self.visible = False
self.owner = None
self.visit = None
self.border = _hud_rect('frame', 99)
self.panel = _hud_rect('panel', 100)
self.frame = _hud_rect('frame', 101)
self.track = _hud_rect('track', 102)
self.fill = _hud_rect('health', 103)
self.label = text('', 0, 0)
self.label.fontSize = UI_CONFIG['bossBar']['fontSize']
self.label.color = '#ffffff'
_apply_game_font(self.label)
self.label.halign = 'center'
self.label.valign = 'middle'
self.label.z = 104
