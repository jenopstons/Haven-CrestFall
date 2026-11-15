if self._destroyed:
    return
# Text objects have no parent/child transform, so the label and backdrop
# are repositioned every frame along with self.
counterLayout = UI_CONFIG['counter']
self.x = camera_x() + counterLayout['x']
self.y = camera_y() + counterLayout['y']
self.label.x = self.x + get_width(self) / 2 + counterLayout['gap']
self.label.y = self.y + counterLayout['labelOffsetY']
counter = getattr(game, 'counter', 0)
if counter != self.shownCount:
    self.shownCount = counter
    self.label.text = str(counter)
padding = 12
left = self.x - get_width(self) / 2 - padding
right = self.label.x + get_width(self.label) + padding
self.backdrop.x = (left + right) / 2
self.backdrop.y = self.y
self.backdrop.scaleX = (right - left) / self.backdrop.baseWidth
self.backdrop.scaleY = (get_height(self) + padding) / self.backdrop.baseHeight
