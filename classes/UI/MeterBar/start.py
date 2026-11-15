# The meter on the HUD: a framed dark bar with a fill that grows as the meter fills.
self.z = 99
self.visible = False
self.layoutY = UI_CONFIG['meter']['y']
self.frame = _hud_rect('frame', 99)
self.track = _hud_rect('track', 100)
self.fill = _hud_rect('meter', 101)
