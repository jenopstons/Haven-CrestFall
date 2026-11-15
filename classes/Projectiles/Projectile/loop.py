if self._destroyed:
    return
if getattr(game, 'finished', False):
    _freeze_for_win(self)
    return
if _hit_stopped():
    return
self.x += self.vx * self.speed
self.y += self.vy * self.speed
if self.levelY is not None and (self.y - self.levelY) * self.vy >= 0:
    self.y = self.levelY
    self.vx = self.dir
    self.vy = 0
    self.levelY = None
    self.angle = 0
self.travelled += self.speed
if self.travelled > self.maxDistance:
    destroy(self)
    return

if self.fromPlayer:
    for enemyHitbox in get_collision_list(self, 'EnemyHitbox'):
        enemy = enemyHitbox.owner
        if enemy._destroyed or enemy.dying or not _projectile_touches(self, enemyHitbox):
            continue
        _hurt_enemy(enemy, self.damage)
        destroy(self)
        return
else:
    for playerHitbox in get_collision_list(self, 'PlayerHitbox'):
        if _projectile_touches(self, playerHitbox) and not _dash_protects(game.player):
            _damage_player(self.damage, self)
            destroy(self)
            return

for solid in get_collision_list(self, 'Platform') + get_collision_list(self, 'Barrier') + get_collision_list(self, 'EdgeWall'):
    if not solid._destroyed and _projectile_touches(self, solid):
        destroy(self)
        return
