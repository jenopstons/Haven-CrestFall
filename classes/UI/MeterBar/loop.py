if self._destroyed:
    return
layout = UI_CONFIG['meter']
share = min(getattr(game, 'meter', 0) / COMBAT_CONFIG['meterMax'], 1)
_place_hud_bar(self, camera_x() + layout['x'], camera_y() + self.layoutY, layout['width'], layout['height'], share)
