if self._destroyed:
    return
if getattr(game, 'finished', False) and not self.dying:
    if self.hitFilterId is not None:
        remove_filter(self, self.hitFilterId)
        self.hitFilterId = None
    self.visible = True
    _freeze_for_win(self)
    return
_update_enemy_hit_effects(self)
if self.behavior == 'jumper':
    _unsquash_jumper(self)
_step_enemy(self)
if self.behavior == 'jumper' and not self._destroyed:
    _squash_jumper(self)
