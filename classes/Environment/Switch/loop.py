if self._destroyed:
    return
if not self.reusable and self.used:
    _update_interact_prompt(self, False, 'exit')
    return
colliding = get_collision(self, 'PlayerHitbox')
if self.activation == 'interact':
    isTarget = colliding and is_interact_target(self)
    _update_interact_prompt(self, isTarget, 'exit')
    activated = isTarget and _control_was_pressed('interact')
else:
    activated = colliding and not self.touching
self.touching = colliding
if activated:
    if self.reusable:
        set_global(self.setsGlobal, not get_global(self.setsGlobal))
    else:
        set_global(self.setsGlobal, True)
        self.used = True
        _mark_persisted('usedSwitches', self.persistentId)
    _play_sound('switch')

on = get_global(self.setsGlobal)
_apply_pose(self, self.onSprite if on else self.offSprite)
self.scaleX = getattr(self, 'artFacing', 1)
