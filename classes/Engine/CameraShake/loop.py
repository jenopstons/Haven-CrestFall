if self._destroyed:
    return
if self.timer % 3 == 0:
    game.shakeX = random.randint(-self.distance, self.distance)
    game.shakeY = random.randint(-self.distance, self.distance)
self.timer -= 1
if self.timer <= 0:
    game.shakeX = 0
    game.shakeY = 0
    destroy(self)
