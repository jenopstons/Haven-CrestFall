# Invisible probe used to check for ground or walls ahead.
self.sprite = sprite('pixel.png')
self.visible = False
self.collisionProxy = True
self.scaleX = max(ENEMY_DEFAULTS['sensorSize'], ENEMY_SENSOR_MIN_WIDTH)
self.scaleY = ENEMY_DEFAULTS['sensorSize']
