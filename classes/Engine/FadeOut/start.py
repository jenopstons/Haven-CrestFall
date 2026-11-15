# Ramps from transparent to opaque black to cover the current room before
# a room switch; its own loop performs the switch once fully black, then
# the destination room creates a FadeIn to reveal it.
_apply_pose(self, _load_pose(UI_CONFIG['fadeOverlay']))
self.scaleX = 13
self.scaleY = 8
self.x = camera_x()
self.y = camera_y()
self.z = 1000
self.alpha = 0
self.nextRoom = None
self.nextLocation = None
