if self._destroyed:
    return
if self.collected:
    return
if get_collision(self, 'PlayerHitbox'):
    self.collected = True
    _play_sound(self.sound)
    if self.setsGlobal:
        set_global(self.setsGlobal, True)
    if self.counter:
        game.counter = getattr(game, 'counter', 0) + 1
    # Recorded before the destroy/dispatch below, so a pickup's immediate
    # effect (like a key unlocking its barrier) never depends on this
    # bookkeeping running first.
    _mark_persisted('collectedMapItems', getattr(self, 'persistentId', None))
    _apply_pickup_effect(self)
    destroy_object(self)
    _dispatch('collect', self)
