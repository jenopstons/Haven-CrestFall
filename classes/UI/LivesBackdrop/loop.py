livesLayout = UI_CONFIG['lives']
lives = getattr(game, 'hud_lives', [])
if not lives:
    return
first = lives[0]
last = lives[-1]
left = first.x - get_width(first) / 2
right = last.x + get_width(last) / 2
self.x = (left + right) / 2
self.y = first.y
self.scaleX = (right - left) / self.baseWidth
self.scaleY = get_height(first) / self.baseHeight
