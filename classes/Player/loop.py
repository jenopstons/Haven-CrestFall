if self._destroyed:
    return
if self.frozen:
    _end_attack(self)
    _cancel_heal(self)
    game.hitStop = 0
    _apply_pose(self, self.frozenPose)
    self.scaleX = getattr(self, 'artFacing', 1) * self.facing * self.sqX
    self.scaleY = self.sqY
    cx, cy = _follow_player_camera(self.x, self.y)
    cx += getattr(game, 'shakeX', 0)
    cy += getattr(game, 'shakeY', 0)
    set_camera(cx, cy)
    game.bg.x = cx
    game.bg.y = cy
    return
if _step_hit_stop():
    return
_update_appearing()

# Squash only shifts the drawn sprite; code that moved the player since keeps its position.
if self.y == self.squashDrawnY:
    self.y -= self.squashOffsetY
self.scaleX = getattr(self, 'artFacing', 1) * self.facing
self.scaleY = 1

if self.invulnerable > 0:
    self.invulnerable -= 1
    self.visible = self.invulnerable % self.blinkCycleFrames < self.blinkCycleFrames // 2
else:
    self.visible = True

self.damageFlashTimer -= 1
if self.damageFilterId is not None and self.damageFlashTimer <= 0:
    remove_filter(self, self.damageFilterId)
    self.damageFilterId = None

# Two-pass axis-separated collision (Y then X). Solids are anything
# tagged 'Platform' or 'Barrier' (a locked Barrier blocks like a
# platform until opened); the X pass also stops at the room's EdgeWalls.

# === Y: gravity + move ===
_step_climbing(self)
previousFeet = _feet(self)
if self.climbing:
    pass
elif self.dashing:
    self.dy = _dash_dy(self)
elif self.dy < 0:
    self.dy += self.gravity * self.fallMult
else:
    self.dy += self.gravity
if self.dy < self.terminalVel:
    self.dy = self.terminalVel
self.y += self.dy

# === Y collision (closest solid wins) ===
wasOnGround = self.onGround
self.onGround = False
self.climbableBelow = None
self.hitbox.x = self.x
self.hitbox.y = self.y + self.hitboxOffsetY
solids = get_collision_list(self.hitbox, 'Platform') + get_collision_list(self.hitbox, 'Barrier')
best = None
for solid in solids:
    barrier = getattr(solid, 'barrier', solid if hasattr(solid, 'locked') else None)
    if barrier is not None:
        _open_barrier(barrier)
    if getattr(solid, '_destroyed', False):
        continue
    hh = get_height(self.hitbox) / 2 + get_height(solid) / 2
    isFloor = self.hitbox.y > solid.y
    candidateHitboxY = solid.y + hh if isFloor else solid.y - hh
    candidateY = candidateHitboxY - self.hitboxOffsetY
    delta = abs(candidateY - self.y)
    # Prefer a launcher (spring, trampoline, ...) over a same-distance neighbour tile.
    if best is None or delta < best[0] or (
        delta == best[0] and getattr(solid, 'launchSpeed', None) is not None
        and getattr(best[3], 'launchSpeed', None) is None
    ):
        best = (delta, candidateY, isFloor, solid)
if best is not None:
    self.y = best[1]
    if best[2]:
        self.onGround = True
        # Carry a moving platform's own per-frame delta.
        self.x += getattr(best[3], 'dx', 0)
        launchSpeed = getattr(best[3], 'launchSpeed', None)
        if launchSpeed is not None:
            self.onGround = False
            self.jumped = True
            self.coyoteTimer = 0
            self.bufferTimer = 0
            self.dy = launchSpeed
            best[3].springTimer = best[3].springFrames
            _apply_pose(best[3], best[3].springPressedPose)
            best[3].scaleX = getattr(best[3], 'artFacing', 1)
            _play_sound('spring')
        else:
            self.dy = -(abs(getattr(best[3], 'dy', 0)) + 2)
    else:
        self.dy = 0
if best is None or not best[2]:
    _land_on_climbable_top(self, previousFeet)
if self.climbing and self.onGround and self.dy <= 0:
    self.climbing = False

if self.onGround and not wasOnGround:
    self.sqX = self.landingSquashX
    self.sqY = self.landingSquashY

if self.onGround and _stands_on_safe_ground(self, solids):
    self.safeGround = (self.x, self.y)

# === Fall off the map ===
mapBottom = getattr(game, 'mapBottom', None)
if mapBottom is not None and self.y < mapBottom - self.fallMargin:
    _fall_to_safe_ground(self)
    return

# === X: accel/decel/turn ===
moving = False
target = 0
# After a fall, a direction still held is ignored until it's let go.
if self.moveLocked and not _control_is_pressed('moveLeft') and not _control_is_pressed('moveRight'):
    self.moveLocked = False
# A wall jump's push carries the player away from the wall for a few frames.
if self.onGround or self.climbing:
    self.wallKickTimer = 0
steering = not self.moveLocked and self.wallKickTimer <= 0 and not self.climbing
if steering and _control_is_pressed('moveLeft'):
    target -= self.maxSpeed
    self.facing = -1
    moving = True
if steering and _control_is_pressed('moveRight'):
    target += self.maxSpeed
    self.facing = 1
    moving = True
if self.climbing:
    moving = self.dx != 0 or self.dy != 0
elif self.wallKickTimer > 0:
    self.wallKickTimer -= 1
elif target != 0:
    self.dx = min(self.dx + self.accel, target) if target > self.dx else max(self.dx - self.accel, target)
elif self.dx > 0:
    self.dx = max(self.dx - self.decel, 0)
elif self.dx < 0:
    self.dx = min(self.dx + self.decel, 0)
_step_abilities(self)
self.x += self.dx

# === X collision ===
# get_collision_list misses overlaps of 2 px or less, so walls are found 2 px ahead.
self.hitbox.x = self.x + (2 if self.dx > 0 else -2 if self.dx < 0 else 0)
self.hitbox.y = self.y + self.hitboxOffsetY
solids = get_collision_list(self.hitbox, 'Platform') + get_collision_list(self.hitbox, 'Barrier') + get_collision_list(self.hitbox, 'EdgeWall')
best = None
for solid in solids:
    barrier = getattr(solid, 'barrier', solid if hasattr(solid, 'locked') else None)
    if barrier is not None:
        _open_barrier(barrier)
    if getattr(solid, '_destroyed', False):
        continue
    hw = get_width(self.hitbox) / 2 + get_width(solid) / 2
    candidateX = solid.x + hw if self.x > solid.x else solid.x - hw
    delta = abs(candidateX - self.x)
    if best is None or delta < best[0]:
        best = (delta, candidateX)
if best is not None:
    self.x = best[1]

self.hitbox.x = self.x
self.hitbox.y = self.y + self.hitboxOffsetY
_step_wall_contact(self)

# === Jump: coyote time + input buffer ===
if self.onGround:
    self.coyoteTimer = self.coyoteMax
    self.jumped = False
else:
    self.coyoteTimer -= 1
if _control_was_pressed('jump'):
    self.bufferTimer = self.bufferMax
else:
    self.bufferTimer -= 1
if _control_was_released('jump') and self.dy > 0:
    self.dy *= self.jumpCut
canJump = (self.onGround or self.coyoteTimer > 0) and not self.jumped
wantJump = (_control_was_pressed('jump') or self.bufferTimer > 0) and not self.climbing and not self.climbJumped
if wantJump and canJump:
    _end_dash(self)
    self.dy = self.jumpSpeed
    self.jumped = True
    self.coyoteTimer = 0
    self.bufferTimer = 0
    self.sqX = self.jumpSquashX
    self.sqY = self.jumpSquashY
    _play_sound('jump')
elif wantJump and not _try_wall_jump(self):
    _try_air_jump(self)
_start_dash(self)
_start_attack(self)
_step_attack(self)

_step_shooting(self)
_step_heal(self)

# === Animation ===
self.scaleX = getattr(self, 'artFacing', 1) * self.facing
if _attack_pose_showing(self):
    _apply_pose(self, self.attackPose)
elif self.climbing:
    _apply_pose(self, self.climbPose if moving else self.climbStillPose)
elif not self.onGround:
    _apply_pose(self, self.jumpUpPose if self.dy > 0 else self.jumpDownPose)
elif moving:
    _apply_pose(self, self.runPose)
else:
    _apply_pose(self, self.idlePose)

self.sqX += (1.0 - self.sqX) * self.squashEaseRate
self.sqY += (1.0 - self.sqY) * self.squashEaseRate

self.hitbox.x = self.x
self.hitbox.y = self.y + self.hitboxOffsetY
contactFeet = self.hitbox.y - get_height(self.hitbox) / 2
stompSurfaceY = None
for enemyHitbox in get_collision_list(self.hitbox, 'EnemyHitbox'):
    enemyTop = _handle_enemy_contact(enemyHitbox.owner, self, contactFeet)
    if enemyTop is not None and (stompSurfaceY is None or enemyTop > stompSurfaceY):
        stompSurfaceY = enemyTop
if self._destroyed:
    return
if stompSurfaceY is not None:
    self.hitbox.y = stompSurfaceY + get_height(self.hitbox) / 2
    self.y = self.hitbox.y - self.hitboxOffsetY

cx, cy = _follow_player_camera(self.x, self.y)
cx += getattr(game, 'shakeX', 0)
cy += getattr(game, 'shakeY', 0)
set_camera(cx, cy)
game.bg.x = cx
game.bg.y = cy

# Draw squashed or stretched with the feet where the hitbox's feet are.
self.squashOffsetY = -get_height(self) * (1 - self.sqY) / 2
self.scaleX = getattr(self, 'artFacing', 1) * self.facing * self.sqX
self.scaleY = self.sqY
self.y += self.squashOffsetY
self.squashDrawnY = self.y
