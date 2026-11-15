# Fades from opaque black to transparent, masking the pop when a room's
# objects are recreated on entry.
_apply_pose(self, _load_pose(UI_CONFIG['fadeOverlay']))
self.scaleX = 13
self.scaleY = 8
self.x = camera_x()
self.y = camera_y()
self.z = 1000
