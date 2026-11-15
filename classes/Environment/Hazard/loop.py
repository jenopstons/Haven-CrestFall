if self._destroyed:
    return
touching = get_collision(self, 'PlayerHitbox')
if touching and (self.hitbox is None or _hitbox_touches(self, self.hitbox, touching)):
    _damage_player(self.damage, self)
