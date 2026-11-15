if self._destroyed:
    return
layout = UI_CONFIG['ammo']
self.x = camera_x() + layout['x'] + self.index * (abs(get_width(self)) + layout['gap'])
self.y = camera_y() + layout['y']
player = getattr(game, 'player', None)
self.alpha = 1 if player is not None and self.index < player.ammo else 0.3
self.visible = _unlocked('shoot')
