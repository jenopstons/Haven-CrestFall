# Invisible collision proxy for Player, sized independently of whichever
# sprite Player is animating. Player.start() resizes this to match its
# own grounded sprite.
self.sprite = sprite('pixel.png')
self.visible = False
self.scaleX = 1.0
self.scaleY = 1.0
