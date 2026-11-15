self.timer -= 1

if self.credit.y < 200:
    self.credit.y += 1

if self.timer <= 0:
    self.message.visible = False
