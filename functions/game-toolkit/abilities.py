# Opt-in player abilities (ABILITIES_CONFIG): dash, air jump and wall jump. An ability does
# nothing unless it is enabled, its `requires` global (if it names one) is on, and, when it
# comes from a pickup, the player has one.


def _requirement_met(requires):
    return requires == '' or get_global(requires) is True


def _ability_active(name):
    ability = ABILITIES_CONFIG[name]
    return ability['enabled'] == 1 and _requirement_met(ability['requires']) and _unlocked(name)


def _dash_ready(player):
    if player.dashCooldownTimer > 0:
        return False
    return ABILITIES_CONFIG['dash']['style'] != 'eightWay' or player.dashCharges > 0


def _dash_direction(player):
    # Burst dashes the way the player faces. Eight-way dashes the way the player holds,
    # diagonals included, and the way they face when nothing is held.
    if ABILITIES_CONFIG['dash']['style'] != 'eightWay':
        return player.facing, 0
    x = (1 if _control_is_pressed('moveRight') else 0) - (1 if _control_is_pressed('moveLeft') else 0)
    y = (1 if _control_is_pressed('aimUp') else 0) - (1 if _control_is_pressed('aimDown') else 0)
    if x == 0 and y == 0:
        return player.facing, 0
    if x != 0 and y != 0:
        return x * 0.7071, y * 0.7071
    return x, y


def _start_dash(player):
    if not _ability_active('dash') or player.dashing or player.climbing or not _dash_ready(player):
        return
    if not _control_was_pressed('dash'):
        return
    dash = ABILITIES_CONFIG['dash']
    player.dashing = True
    player.dashX, player.dashY = _dash_direction(player)
    if player.dashX != 0:
        player.facing = 1 if player.dashX > 0 else -1
    player.dashFramesLeft = dash['frames']
    player.dashCooldownTimer = dash['cooldown']
    player.dashCharges = max(player.dashCharges - 1, 0)
    player.dy = 0
    if _ability_active('airJump') and ABILITIES_CONFIG['airJump']['refill'] == 'dash':
        player.airJumps = min(player.airJumps + 1, ABILITIES_CONFIG['airJump']['count'])
    _play_sound('dash')


def _end_dash(player):
    if not player.dashing:
        return
    player.dashing = False
    player.dx = max(-player.maxSpeed, min(player.maxSpeed, player.dx))
    if player.dy > 0:
        player.dy = min(player.dy, player.jumpSpeed * 0.5)


def _dash_dy(player):
    # The vertical speed while dashing: none for a sideways dash, so gravity is off.
    return ABILITIES_CONFIG['dash']['speed'] * player.dashY


def _refill_on_ground(player):
    if not player.onGround:
        return
    if ABILITIES_CONFIG['airJump']['refill'] == 'landing':
        player.airJumps = ABILITIES_CONFIG['airJump']['count']
    if not player.dashing:
        player.dashCharges = ABILITIES_CONFIG['dash']['charges']


def _refill_abilities(player):
    # A stomp or a melee bounce gives back every air jump and the dash.
    if _ability_active('airJump'):
        player.airJumps = ABILITIES_CONFIG['airJump']['count']
    player.dashCharges = ABILITIES_CONFIG['dash']['charges']
    player.dashCooldownTimer = 0


def _show_dash_ready(player):
    # The player turns grey while the dash can't be used.
    grey = _ability_active('dash') and not _dash_ready(player)
    if grey and player.dashFilterId is None:
        player.dashFilterId = add_filter(player, new_adjustment_filter({ 'saturation': 0, 'contrast': 1, 'gamma': 0.8, 'brightness': 0.85 }))
    elif not grey and player.dashFilterId is not None:
        remove_filter(player, player.dashFilterId)
        player.dashFilterId = None


def _step_abilities(player):
    # Runs once a frame after the vertical move, so onGround is this frame's.
    _refill_on_ground(player)
    if player.dashCooldownTimer > 0:
        player.dashCooldownTimer -= 1
    if player.dashing:
        player.dx = ABILITIES_CONFIG['dash']['speed'] * player.dashX
        player.dashFramesLeft -= 1
        if player.dashFramesLeft <= 0:
            _end_dash(player)
    _show_dash_ready(player)


def _dash_protects(player):
    # With Safe while dashing on, enemies and their shots can't hurt a dashing player.
    # Hazards and falls still do.
    return player.dashing and ABILITIES_CONFIG['dash']['safe'] == 1


def _try_air_jump(player):
    if not _ability_active('airJump') or player.onGround or player.airJumps <= 0:
        return False
    player.airJumps -= 1
    _end_dash(player)
    player.dy = player.jumpSpeed
    player.jumped = True
    player.coyoteTimer = 0
    player.bufferTimer = 0
    player.sqX = player.jumpSquashX
    player.sqY = player.jumpSquashY
    _play_sound('jump')
    return True


# Frames after leaving a wall that a jump still kicks off it.
WALL_JUMP_GRACE_FRAMES = 6


def _wall_side(player):
    # Which side a wall touches the player's hitbox on: -1 left, 1 right, 0 none. A floor or
    # ceiling tile beside the player doesn't count. The room's invisible edge walls are EdgeWalls, so they aren't checked.
    side_found = 0
    hitbox_height = get_height(player.hitbox)
    for side in (-1, 1):
        # get_collision_list misses overlaps of 2 px or less, so look 3 px out.
        player.hitbox.x = player.x + side * 3
        for solid in get_collision_list(player.hitbox, 'Platform') + get_collision_list(player.hitbox, 'Barrier'):
            if getattr(solid, '_destroyed', False):
                continue
            beside = (solid.x - player.x) * side > 0
            overlap = (hitbox_height + get_height(solid)) / 2 - abs(solid.y - player.hitbox.y)
            if beside and overlap > 3:
                side_found = side
    player.hitbox.x = player.x
    return side_found


def _step_wall_contact(player):
    # Runs after the sideways move, so the wall check sees where the player ended up.
    if player.onGround or not _ability_active('wallJump'):
        player.wallTimer = 0
        return
    side = _wall_side(player)
    if side != 0:
        player.wallSide = side
        player.wallTimer = WALL_JUMP_GRACE_FRAMES
    elif player.wallTimer > 0:
        player.wallTimer -= 1


def _try_wall_jump(player):
    if player.wallTimer <= 0 or player.onGround or not _ability_active('wallJump'):
        return False
    _end_dash(player)
    player.facing = -player.wallSide
    player.dx = player.facing * ABILITIES_CONFIG['wallJump']['speed']
    player.dy = player.jumpSpeed
    player.wallKickTimer = ABILITIES_CONFIG['wallJump']['frames']
    player.wallTimer = 0
    player.jumped = True
    player.coyoteTimer = 0
    player.bufferTimer = 0
    player.sqX = player.jumpSquashX
    player.sqY = player.jumpSquashY
    _play_sound('jump')
    return True


def _spawn_player_indicators(player):
    # Icons that float above the player and show a count, e.g. air jumps left. Each entry of
    # UI_CONFIG['playerIndicators'] names the player attribute to show and the one holding its maximum.
    if ABILITIES_CONFIG['airJump']['enabled'] != 1:
        return
    for spec in UI_CONFIG.get('playerIndicators', {}).values():
        total = int(getattr(player, spec['max']))
        for index in range(total):
            icon = PlayerIndicator()
            icon.spec = spec
            icon.index = index
            icon.total = total
            _apply_pose(icon, _load_pose(spec['icon']))