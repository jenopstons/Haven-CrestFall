# One-shot camera jitter. Uses a shared game.shakeX/shakeY offset, added
# by Player's own loop, instead of calling set_camera() here directly -
# Player already calls it every frame to follow the player, so a second
# call here would just race it.
self.timer = CAMERA_SHAKE_CONFIG['timer']
self.distance = CAMERA_SHAKE_CONFIG['distance']
game.shakeX = 0
game.shakeY = 0
self.visible = False
