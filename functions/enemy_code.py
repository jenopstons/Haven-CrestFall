def _studio_enemy_start_0(self):
    pass
    self.state = 'wait'
    self.timer = 0
    self.shots = 0
    self.bob = 1
    self.angry = False

def _studio_enemy_loop_0(self):
    pass
    tile = 18
    hover = self.spawnY + tile * 1.5
    gap = player_distance(self)

    if not self.angry and self.health <= self.maxHealth / 2:
        self.angry = True
        set_global('HoodedPhase2', True)

    if self.state == 'wait':
        set_pose(self, 'idle')
        if gap is not None and abs(gap[0]) < tile * 8:
            face_player(self)
            self.flying = True
            self.state = 'rise'

    elif self.state == 'rise':
        set_pose(self, 'jumpUp')
        self.y += 1.5
        if self.y >= hover:
            self.y = hover
            self.state = 'fight'
            self.timer = 60

    elif self.state == 'fight':
        face_player(self)
        set_pose(self, 'run')
        self.y += 0.25 * self.bob
        if abs(self.y - hover) > 4:
            self.bob = -self.bob
        if gap is not None and abs(gap[0]) > tile * 4:
            self.x += self.dir * self.speed
        self.timer -= 1
        if self.timer <= 0 and gap is not None:
            self.shots += 1
            # Most shots level out at the player's middle (jump them); every third at head height (stay down).
            high = self.shots % 3 == 0
            enemy_shoot(self, level_y=self.y + gap[1] + (14 if high else 0))
            self.timer = 45 if self.angry else 75
            if self.shots >= (4 if self.angry else 6):
                self.shots = 0
                self.state = 'climb'

    elif self.state == 'climb':
        set_pose(self, 'jumpUp')
        self.y += 2
        if self.y >= self.spawnY + tile * 4:
            self.state = 'aim'
            self.timer = 40

    elif self.state == 'aim':
        face_player(self)
        set_pose(self, 'attack')
        self.timer -= 1
        if self.timer <= 0:
            enemy_shoot(self, at_player=True, speed=3 if self.angry else 2.5, sprite='slash.png')
            self.state = 'dive'

    elif self.state == 'dive':
        set_pose(self, 'jumpDown')
        self.y -= 1.5
        if self.y <= hover:
            self.y = hover
            self.state = 'fight'
            self.timer = 60

ENEMY_SCRIPTS = {
    "character_5": {'label': "The Hooded One", 'start': _studio_enemy_start_0, 'loop': _studio_enemy_loop_0},
}