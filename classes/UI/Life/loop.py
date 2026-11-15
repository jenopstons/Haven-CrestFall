if self._destroyed:
    return
livesLayout = UI_CONFIG['lives']
self.x = camera_x() + livesLayout['x'] + self.index * (get_width(self) + livesLayout['gap'])
self.y = camera_y() + livesLayout['y']
player = getattr(game, 'player', None)
shouldFill = player is not None and self.index < player.health
if shouldFill != self.filled:
    self.filled = shouldFill
    pose = self.fullPose if shouldFill else self.emptyPose
    _apply_pose(self, pose)
    self.visible = pose is not None
