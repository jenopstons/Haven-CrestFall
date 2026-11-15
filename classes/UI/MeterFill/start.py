# The filled part of the meter bar, which MeterBar sizes each frame.
self.sprite = sprite('pixel.png')
self.baseWidth = get_width(self)
self.baseHeight = get_height(self)
self.z = 100
self.visible = False
add_filter(self, new_adjustment_filter({ 'saturation': 0, 'brightness': 1.4 }))
