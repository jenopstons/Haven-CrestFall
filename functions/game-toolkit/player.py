# Player lifecycle - spawn (fresh start and mid-game respawn/entry),
# damage, and death/respawn.

def _follow_player_camera(x, y):
    target_x, target_y = _clamped_camera(x, y)
    camera_y = getattr(game, '_platformer_camera_y', target_y)
    camera_y += (target_y - camera_y) * 0.1
    _, camera_y = _clamped_camera(target_x, camera_y)
    game._platformer_camera_y = camera_y
    return target_x, camera_y


def _add_life_icon(index, x, y):
    livesLayout = UI_CONFIG['lives']
    life = Life()
    life.index = index
    life.x = x + livesLayout['x'] + index * (get_width(life) + livesLayout['gap'])
    life.y = y + livesLayout['y']
    game.hud_lives.append(life)


def _spawn_lives_hud(px, py):
    # One icon per health point, with a backdrop behind them.
    for i in range(min(_max_health(), UI_CONFIG['lives'].get('displayLimit', 10))):
        _add_life_icon(i, px, py)
    game.hud_lives_backdrop = LivesBackdrop()


def spawn_player(*, at=None):
    # An explicit position works exactly like every add_*() factory's at=
    # form. With no position at all, resolves to this room visit's
    # arrival_location(). Requires build_tilemap() to have already run this
    # visit, and can only be called once per visit. During a death respawn,
    # the checkpointed world coordinates take precedence over any at=
    # evaluated by the room script - at= is still validated (so a broken
    # room script errors even during respawn), just not used for position.
    if not getattr(game, 'tilemapBuilt', False):
        raise ValueError('spawn_player() needs build_tilemap() to run first.')
    if getattr(game, 'playerSpawnedThisVisit', False):
        raise ValueError('spawn_player() was already called once this room visit.')

    if at is not None:
        candidate = _resolve_at(at)
    else:
        candidate = None

    respawn = getattr(game, 'respawnCheckpoint', None)
    if respawn is not None and respawn['coords'] is not None:
        px, py = respawn['coords']
    elif candidate is not None:
        px, py = candidate
    else:
        name = game.arrivalLocation
        if name not in game.locations:
            raise ValueError(f"No location named {name!r} on this room - check 'locations' in maps.py.")
        px, py = game.locations[name]

    background_name = getattr(game, 'mapBackground', None)
    background_pose = None if background_name == '__studio_black__' else _require_type(
        BACKGROUND_TYPES, background_name, "this room's background"
    )

    p = Player()
    p._isPlayer = True
    p.x = px
    p.y = py
    # Set here directly so a same-frame collision check never reads a
    # stale hitbox position before the player's own loop first runs.
    p.hitbox.x = px
    p.hitbox.y = py + p.hitboxOffsetY
    game.player = p
    # Brief grace window so freshly-constructed enemies/hazards can't hit
    # the player before a real frame has passed.
    p.invulnerable = 10
    cx, cy = _clamped_camera(px, py)
    game._platformer_camera_y = cy
    set_camera(cx, cy)
    FadeIn()
    game.bg = Background()
    if background_pose is not None:
        _apply_pose(game.bg, _load_pose(background_pose))
        game.bg.visible = True
    game.hud_lives = []
    game.hud_lives_backdrop = None
    if UI_CONFIG['lives']['icon'] is not None:
        _spawn_lives_hud(px, py)
    _spawn_player_indicators(p)
    _spawn_combat_hud(p)
    if not hasattr(game, 'counter'):
        game.counter = 0
    if not hasattr(game, 'meter'):
        game.meter = 0
    if not hasattr(game, 'unlocked'):
        game.unlocked = []
    if not hasattr(game, 'persisted'):
        game.persisted = {}
    if not hasattr(game, 'globals'):
        game.globals = {}

    # A death respawn re-applies its pre-death checkpoint values once more
    # here, so any set_global/counter call a room-start script made during
    # reconstruction (discouraged - see the guide) can't accumulate or
    # redefine the checkpoint.
    if respawn is not None:
        game.counter = respawn['counter']
        game.meter = respawn['meter']
        game.persisted = {name: set(values) for name, values in respawn['persisted'].items()}
        game.globals = dict(respawn['globals'])
        game.respawnCheckpoint = None

    # Every room is a save point - death restores this checkpoint, not zero.
    game.counterCheckpoint = game.counter
    game.meterCheckpoint = game.meter
    game.persistedCheckpoint = {name: set(values) for name, values in game.persisted.items()}
    game.globalsCheckpoint = dict(game.globals)
    game.spawnCheckpoint = (px, py)
    game.arrivalCheckpoint = game.arrivalLocation
    if UI_CONFIG['counter']['icon'] is None:
        game.hud_counter = None
    else:
        game.hud_counter = Counter()
    fall_override = getattr(game, 'fallMarginOverride', None)
    if fall_override is not None:
        p.fallMargin = fall_override
    game.playerSpawnedThisVisit = True
    return p


def _flash_player_hurt(player):
    player.invulnerable = player.invulnerableFrames
    if player.damageFilterId is not None:
        remove_filter(player, player.damageFilterId)
    player.damageFilterId = add_filter(player, new_adjustment_filter({ 'contrast': 0, 'brightness': 5 }))
    player.damageFlashTimer = player.damageFlashFrames


def _stands_on_safe_ground(player, solids):
    # Safe ground is still Platform under both of the player's feet, away from
    # hazards: a barrier can open and a moving platform moves.
    if get_collision(player.hitbox, 'Hazard'):
        return False
    halfWidth = get_width(player.hitbox) / 2
    left = player.hitbox.x - halfWidth
    right = player.hitbox.x + halfWidth
    leftSupported = False
    rightSupported = False
    for solid in solids:
        if getattr(solid, 'moving', None) is not False or solid.y >= player.hitbox.y:
            continue
        solidHalfWidth = get_width(solid) / 2
        if solid.x - solidHalfWidth <= left <= solid.x + solidHalfWidth:
            leftSupported = True
        if solid.x - solidHalfWidth <= right <= solid.x + solidHalfWidth:
            rightSupported = True
    return leftSupported and rightSupported


def _fall_to_safe_ground(player):
    # A fall costs one heart and puts the player back on the last still,
    # hazard-free ground they stood on in this room. Falling with the last
    # heart, or before standing anywhere, restarts the room like any death.
    if player.health <= 1 or player.safeGround is None:
        _respawn_player()
        return
    player.health -= 1
    _end_dash(player)
    _cancel_heal(player)
    player.x, player.y = player.safeGround
    player.dx = 0
    player.dy = 0
    player.moveLocked = True
    _flash_player_hurt(player)
    _play_sound('hurt')
    _add_camera_shake()
    _dispatch('playerHit', player, 1)


def _damage_player(amount, source=None):
    # source, if given, is the enemy/hazard that hit the player - used to
    # point knockback away from it.
    player = game.player
    if player.invulnerable > 0 or player.frozen:
        return
    player.health -= amount
    _end_dash(player)
    # A hit knocks the player off a ladder.
    if player.climbing:
        player.climbing = False
        player.climbRegrabTimer = CLIMB_REGRAB_FRAMES
    _cancel_heal(player)
    _flash_player_hurt(player)
    if source is not None:
        direction = 1 if player.x >= source.x else -1
        player.x += direction * player.knockbackX
        player.dy = player.knockbackY
    if player.health > 0:
        _play_sound('hurt')
    _add_camera_shake()
    # A player_hit listener that raises must not leave health<=0 playable -
    # death cleanup runs in `finally`, before the exception re-raises, so a
    # callback bug can't skip checkpoint restore/fade cancellation.
    try:
        _dispatch('playerHit', player, amount)
    finally:
        if player.health <= 0:
            _respawn_player()


def _respawn_player():
    # Death is instant, not faded - a full room restart from scratch. Copies
    # the existing checkpoint, restores its gameplay values immediately (so
    # switches/collectibles rebuilt during reconstruction read the correct
    # restored globals), rebuilds the same room at the same arrival, and
    # supplies the checkpointed world coordinates to spawn_player. Any
    # pending room change this same hit triggered is cancelled - death wins.
    _play_sound('death')
    checkpoint = {
        'counter': getattr(game, 'counterCheckpoint', 0),
        'meter': getattr(game, 'meterCheckpoint', 0),
        'persisted': {name: set(values) for name, values in getattr(game, 'persistedCheckpoint', {}).items()},
        'globals': dict(getattr(game, 'globalsCheckpoint', {})),
        'coords': getattr(game, 'spawnCheckpoint', None),
        'arrival': getattr(game, 'arrivalCheckpoint', None),
    }
    game.counter = checkpoint['counter']
    game.meter = checkpoint['meter']
    game.persisted = {name: set(values) for name, values in checkpoint['persisted'].items()}
    game.globals = dict(checkpoint['globals'])
    game.respawnCheckpoint = checkpoint
    pending_fade = getattr(game, 'pendingFade', None)
    if pending_fade is not None and not pending_fade._destroyed:
        destroy(pending_fade)
    game.pendingFade = None
    game.pendingTransition = False
    _enter_room(game.room, checkpoint['arrival'], preserve_music=True)


# === Climbing ===
# Ladders, vines and ropes (add_climbable). Up or down grabs one the player
# overlaps; down also grabs from standing on the top one. While climbing,
# gravity is off and every direction moves at climbSpeed. Jump lets go.

# Frames after letting go before holding up grabs again, so a jump off a
# ladder isn't caught by the same ladder.
CLIMB_REGRAB_FRAMES = 12


def _live_climbables():
    found = []
    for key, objects in game.byCategoryType.items():
        if key[0] == 'climbable':
            found += [obj for obj in objects if not obj._destroyed]
    return found


def _climbable_top(climbable, climbables):
    # The top of a column: nothing climbable directly above it.
    width = get_width(climbable) / 2
    height = get_height(climbable)
    for other in climbables:
        if other is not climbable and abs(other.x - climbable.x) < width and 0 < other.y - climbable.y <= height * 1.01:
            return False
    return True


def _touching_climbable(player):
    return any(not obj._destroyed for obj in get_collision_list(player.hitbox, 'Climbable'))


def _feet(player):
    return player.y + player.hitboxOffsetY - get_height(player.hitbox) / 2


def _land_on_climbable_top(player, previousFeet):
    # The top of a ladder is a floor the player can drop through by climbing down.
    # Looks 3 px below the feet too, since collisions miss overlaps of 2 px or less.
    if player.climbing or player.dy > 0:
        return
    feet = _feet(player)
    halfWidth = get_width(player.hitbox) / 2
    climbables = _live_climbables()
    for climbable in climbables:
        top = climbable.y + get_height(climbable) / 2
        if abs(climbable.x - player.x) >= halfWidth + get_width(climbable) / 2 - 1:
            continue
        if previousFeet < top - 3 or feet > top or not _climbable_top(climbable, climbables):
            continue
        player.y += top - feet
        player.dy = 0
        player.onGround = True
        player.climbableBelow = climbable
        return


def _step_climbing(player):
    # Runs before gravity: starts, steers and ends a climb.
    player.climbJumped = False
    up = _control_is_pressed('aimUp')
    down = _control_is_pressed('aimDown')
    if player.climbRegrabTimer > 0:
        player.climbRegrabTimer -= 1
    if not player.climbing:
        standingOnTop = player.onGround and player.climbableBelow is not None and not player.climbableBelow._destroyed
        if down and standingOnTop:
            # Step into the ladder below so the climb overlaps it.
            player.y -= 4
            player.hitbox.y = player.y + player.hitboxOffsetY
        elif not ((up and player.climbRegrabTimer <= 0) or (down and not player.onGround)):
            return
        if not _touching_climbable(player):
            return
        _end_dash(player)
        player.climbing = True
        player.jumped = False
    elif not _touching_climbable(player):
        player.climbing = False
        player.dy = 0
        return
    if _control_was_pressed('jump'):
        player.climbing = False
        player.climbJumped = True
        player.climbRegrabTimer = CLIMB_REGRAB_FRAMES
        player.dy = 0 if down else player.jumpSpeed
        player.jumped = True
        player.bufferTimer = 0
        if not down:
            _play_sound('jump')
        return
    speed = PLAYER_CONFIG['climbSpeed']
    player.dy = speed * ((1 if up else 0) - (1 if down else 0))
    player.dx = speed * ((1 if _control_is_pressed('moveRight') else 0) - (1 if _control_is_pressed('moveLeft') else 0))
    if player.dx != 0:
        player.facing = 1 if player.dx > 0 else -1