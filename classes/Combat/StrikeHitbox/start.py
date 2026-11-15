self.sprite = sprite('pixel.png')
self.visible = False
self.collisionProxy = True
self.scaleX = 1.0
self.scaleY = 1.0
# Unscaled size, so each frame's resize sets an absolute scale.
self.baseWidth = get_width(self)
self.baseHeight = get_height(self)
