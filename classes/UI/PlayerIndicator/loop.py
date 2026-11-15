if self._destroyed or self.spec is None:
    return
player = getattr(game, 'player', None)
if player is None or player._destroyed:
    self.visible = False
    return
self.visible = self.index < getattr(player, self.spec['value'], 0)
slot = self.index - (self.total - 1) / 2
self.x = player.x + slot * (get_width(self) + self.spec['gap'])
self.y = player.y + self.spec['offsetY']
