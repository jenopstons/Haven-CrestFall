if self._destroyed:
    return
self.x = camera_x()
self.y = camera_y()
if self.alpha < 1:
    self.alpha += 0.02
elif self.nextRoom:
    _enter_room(self.nextRoom, self.nextLocation)
