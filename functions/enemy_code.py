def _studio_enemy_start_0(self):
    pass
    self.timer = 120

def _studio_enemy_loop_0(self):
    pass
    self.timer -= 1
    bloodied = self.health <= self.maxHealth / 2
    if wall_ahead(self) or not ground_ahead(self):
        self.dir = -self.dir
    self.x += self.dir * self.speed
    if self.timer <= 0:
        enemy_shoot()
        if bloodied: self.timer = 30
        else: self.timer = 120
    #if bloodied:

ENEMY_SCRIPTS = {
    "character_4": {'label': "Hooded One", 'start': _studio_enemy_start_0, 'loop': _studio_enemy_loop_0},
}