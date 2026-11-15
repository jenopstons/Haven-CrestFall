if self._destroyed:
    return
self.x = camera_x()
self.y = camera_y()
self.alpha -= 0.01
if self.alpha <= 0:
    destroy(self)
