poses = PLAYER_CONFIG['poses']
self.runPose = _load_pose(_resolve_pose(poses, 'run'))
self.idlePose = _load_pose(_resolve_pose(poses, 'idle'))
self.jumpUpPose = _load_pose(_resolve_pose(poses, 'jumpUp'))
self.jumpDownPose = _load_pose(_resolve_pose(poses, 'jumpDown'))
self.attackPose = _load_pose(_resolve_pose(poses, 'attack'))
self.climbPose = _load_pose(_resolve_pose(poses, 'climb'))
# Holding still on a ladder shows the climb art without animating.
self.climbStillPose = _load_pose(_resolve_pose(poses, 'climb'), fps=0)
# Frozen copy of idle, used for the finished-game freeze.
self.frozenPose = _load_pose(_resolve_pose(poses, 'idle'), fps=0)
_apply_pose(self, self.idlePose)
# Above Exit's z (5) so the player draws in front of exits.
self.z = 6
self.hitbox = PlayerHitbox()
self.hitbox.z = self.z + 1
# Sized from the actual idle sprite, not a hardcoded pixel count, so any
# character swap keeps working.
self.hitbox.scaleX = get_width(self) * PLAYER_CONFIG['hitboxWidthPercent'] / 100 / get_width(self.hitbox)
self.hitbox.scaleY = get_height(self) * PLAYER_CONFIG['hitboxHeightPercent'] / 100 / get_height(self.hitbox)
# Negative because world Y increases upward.
self.hitboxOffsetY = -(get_height(self) - get_height(self.hitbox)) / 2

self.accel = PLAYER_CONFIG['accel']
self.decel = PLAYER_CONFIG['decel']
self.maxSpeed = PLAYER_CONFIG['maxSpeed']
self.jumpSpeed = PLAYER_CONFIG['jumpSpeed']
self.fallMult = PLAYER_CONFIG['fallMult']
self.gravity = PLAYER_CONFIG['gravity']
self.jumpCut = PLAYER_CONFIG['jumpCut']

self.coyoteMax = PLAYER_CONFIG['coyoteMax']
self.bufferMax = PLAYER_CONFIG['bufferMax']
self.invulnerableFrames = PLAYER_CONFIG['invulnerableFrames']
self.damageFlashFrames = PLAYER_CONFIG['damageFlashFrames']
self.blinkCycleFrames = PLAYER_CONFIG['blinkCycleFrames']
self.knockbackX = PLAYER_CONFIG['knockbackX']
self.knockbackY = PLAYER_CONFIG['knockbackY']
self.landingSquashX = PLAYER_CONFIG['landingSquashX']
self.landingSquashY = PLAYER_CONFIG['landingSquashY']
self.jumpSquashX = PLAYER_CONFIG['jumpSquashX']
self.jumpSquashY = PLAYER_CONFIG['jumpSquashY']
self.squashEaseRate = PLAYER_CONFIG['squashEaseRate']
self.stompBounce = PLAYER_CONFIG['stompBounce']
self.stompDamage = PLAYER_CONFIG['stompDamage']
self.fallMargin = PLAYER_CONFIG['fallMargin']

# Collision-safety clamp, not a feel setting - keeps fast falls from
# tunneling through thin platforms.
self.terminalVel = PLAYER_CONFIG['terminalVel']
self.coyoteTimer = 0
self.jumped = False
self.bufferTimer = 0

self.dx = 0
self.dy = 0
self.onGround = False
# Where a fall puts the player back: the last still, hazard-free ground stood on.
self.safeGround = None
self.moveLocked = False
# Runtime horizontal direction; art orientation comes from the active pose.
self.facing = 1
self.health = _max_health()
self.invulnerable = 0
self.damageFilterId = None
self.damageFlashTimer = 0
self.frozen = False
self.projectile = PLAYER_CONFIG.get('projectile')
self.dashing = False
self.dashX = 1
self.dashY = 0
self.dashFramesLeft = 0
self.dashCooldownTimer = 0
self.dashCharges = ABILITIES_CONFIG['dash']['charges']
self.dashFilterId = None
self.airJumpMax = ABILITIES_CONFIG['airJump']['count']
self.airJumps = self.airJumpMax if ABILITIES_CONFIG['airJump']['refill'] == 'landing' else 0
# Wall jump: the side of the wall last touched (-1 left, 1 right), frames left to still jump off
# it, and frames the push away from it still overrides left/right.
self.wallSide = 0
self.wallTimer = 0
self.wallKickTimer = 0
# Climbing: on a ladder now, the ladder top stood on, frames before up grabs again, and
# whether this frame's jump let go of a ladder.
self.climbing = False
self.climbableBelow = None
self.climbRegrabTimer = 0
self.climbJumped = False
self.shootCooldown = 0
self.ammo = COMBAT_CONFIG['maxAmmo']
self.ammoTimer = 0
self.healTimer = 0
self.healFilterId = None
self.attackTimer = 0
self.strike = None
game.hitStop = 0
self.sqX = 1.0
self.sqY = 1.0
self.squashOffsetY = 0
self.squashDrawnY = None
self.scaleX = getattr(self, 'artFacing', 1) * self.facing
