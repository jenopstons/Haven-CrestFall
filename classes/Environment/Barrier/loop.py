if self._destroyed:
    return
if get_collision(self, 'PlayerHitbox'):
    _open_barrier(self)
