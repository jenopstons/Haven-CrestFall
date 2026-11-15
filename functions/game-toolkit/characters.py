# Enemies and NPCs - placement plus the patrol-behavior helpers Enemy's
# own loop uses.


# PixelPad trims 1 px off each side of a collision box, so floor tiles have 2 px gaps between them.
ENEMY_SENSOR_MIN_WIDTH = 6


def _ground_ahead(enemy, direction, foot_y, reach=None):
    # Probes `reach` (default: one step) ahead of a ground-based enemy, at
    # foot height, for solid ground.
    lead = abs(get_width(enemy)) / 2 + (enemy.senseAhead if reach is None else reach)
    widened = abs(get_width(enemy.sensor)) - ENEMY_DEFAULTS['sensorSize']
    enemy.sensor.x = enemy.x + direction * (lead + widened / 2)
    enemy.sensor.y = foot_y - abs(get_height(enemy)) / 2 - enemy.senseDown
    return _live_solid_at(enemy.sensor)


def _solid_kinds(edges):
    # Platforms and barriers block movement; the room's invisible edge walls do too when edges is True.
    return ('Platform', 'Barrier', 'EdgeWall') if edges else ('Platform', 'Barrier')


def _solids_touching(obj, edges=False):
    # Every solid obj overlaps, including ones destroyed this frame, like an opened barrier.
    return [solid for kind in _solid_kinds(edges) for solid in get_collision_list(obj, kind)]


def _live_solids(obj, edges=False):
    return [solid for solid in _solids_touching(obj, edges) if not solid._destroyed]


def _live_solid_at(sensor, edges=False):
    # True when the sensor touches a solid that hasn't just been destroyed.
    for kind in _solid_kinds(edges):
        hit = get_collision(sensor, kind)
        if hit and (not hit._destroyed or any(not solid._destroyed for solid in get_collision_list(sensor, kind))):
            return True
    return False


def _wall_ahead(enemy, middle_y=None):
    # Probes just ahead of an enemy, at the height of its middle, for a wall or barrier.
    enemy.sensor.x = enemy.x + enemy.dir * (abs(get_width(enemy)) / 2 + enemy.senseAhead)
    enemy.sensor.y = enemy.y if middle_y is None else middle_y
    return _live_solid_at(enemy.sensor, edges=True)


def _hop_reach(enemy):
    # How far one hop carries a jumper sideways: its speed times its time in the air.
    return enemy.speed * 2 * enemy.jumpSpeed / -enemy.hopGravity


def _choose_patrol_direction(enemy, foot_y, reach=None, walls=True):
    # Past patrolRange it heads back to its start, turning at edges and walls; cut off from its start, it patrols where it is.
    outside = abs(enemy.x - enemy.spawnX) > enemy.patrolRange
    if outside:
        enemy.dir = 1 if enemy.x < enemy.spawnX else -1
    if not _ground_ahead(enemy, enemy.dir, foot_y, reach) or (walls and _wall_ahead(enemy)):
        if outside:
            enemy.spawnX = enemy.x - enemy.dir * enemy.patrolRange
        enemy.dir = -enemy.dir


def _patrol_step(enemy, foot_y):
    # Horizontal movement for 'patrol': turn around at a real edge, a wall
    # or patrolRange, whichever comes first.
    _choose_patrol_direction(enemy, foot_y)
    enemy.x += enemy.dir * enemy.speed
    enemy.scaleX = getattr(enemy, 'artFacing', 1) * enemy.dir


ENEMY_HIT_FLASH_FRAMES = 8
ENEMY_HIT_INVULNERABLE_FRAMES = 30
ENEMY_BLINK_CYCLE_FRAMES = 4


def _hurt_enemy(enemy, amount, blink=True):
    # A melee hit doesn't blink: each swing can hit an enemy only once anyway.
    if (blink and enemy.invulnerable > 0) or enemy.dying or enemy.invincible:
        return False
    enemy.health -= amount
    _play_sound('enemyhit')
    if enemy.hitFilterId is not None:
        remove_filter(enemy, enemy.hitFilterId)
    enemy.hitFilterId = add_filter(enemy, new_adjustment_filter({ 'contrast': 0, 'brightness': 5 }))
    enemy.hitFlashTimer = ENEMY_HIT_FLASH_FRAMES
    if enemy.health <= 0:
        _defeat_enemy(enemy)
    elif blink:
        enemy.invulnerable = ENEMY_HIT_INVULNERABLE_FRAMES
    return True


def _defeat_enemy(enemy):
    # An enemy beaten in the air drops its pickup once it lands.
    enemy.dying = True
    if (enemy.airborne or enemy.flying) and enemy.behavior in GROUND_BEHAVIORS:
        enemy.dropPending = True
    else:
        _drop_pickup(enemy)
    if enemy.beatenSetsGlobal is not None:
        set_global(enemy.beatenSetsGlobal, True)
    _dispatch('enemyDefeated', enemy)


def _drop_pickup(enemy):
    if enemy.drop is None or random.random() * 100 >= enemy.dropChance:
        return
    pickup = _build_collectible(enemy.x, enemy.y, enemy.drop, enemy.dropSetsGlobal)
    pickup.persistentId = None
    _register_instance('collectible', enemy.drop, pickup)


def _update_enemy_hit_effects(enemy):
    if enemy.invulnerable > 0:
        enemy.invulnerable -= 1
        enemy.visible = enemy.invulnerable % ENEMY_BLINK_CYCLE_FRAMES < ENEMY_BLINK_CYCLE_FRAMES // 2
    enemy.hitFlashTimer -= 1
    if enemy.hitFilterId is not None and enemy.hitFlashTimer <= 0:
        remove_filter(enemy, enemy.hitFilterId)
        enemy.hitFilterId = None


def _handle_enemy_contact(enemy, player, contactFeet):
    # Feet above the enemy's middle stomp it unless still rising; lower contact hurts.
    if getattr(enemy, '_destroyed', False) or enemy.dying:
        return None
    if contactFeet < enemy.hitbox.y or COMBAT_CONFIG['stomp'] != 1:
        if not _dash_protects(player):
            _damage_player(enemy.contactDamage, enemy)
        return None
    if player.dy > 0:
        return None
    _end_dash(player)
    player.dy = player.jumpSpeed * player.stompBounce
    _refill_abilities(player)
    _hurt_enemy(enemy, player.stompDamage)
    return enemy.hitbox.y + get_height(enemy.hitbox) / 2


def _solid_top(solid):
    return solid.y + get_height(solid) / 2


def _floor_below(enemy, previous_bottom, tolerance=None):
    # The solid with the highest top the enemy's hitbox now overlaps that was no more than `tolerance` above its feet.
    reach = ENEMY_GROUND_PROBE if tolerance is None else tolerance
    floors = [solid for solid in _live_solids(enemy.hitbox) if _solid_top(solid) <= previous_bottom + reach]
    return max(floors, key=_solid_top) if floors else None


def _still_on(enemy, solid, bottom):
    # True while the enemy's feet rest on top of the same solid it stood on last frame.
    if solid is None or solid._destroyed or abs(_solid_top(solid) - bottom) > 0.001:
        return False
    return abs(solid.x - enemy.hitbox.x) < (abs(get_width(solid)) + abs(get_width(enemy.hitbox))) / 2 - 2


def _ceiling_above(enemy, previous_top):
    bottoms = [solid.y - get_height(solid) / 2 for solid in _live_solids(enemy.hitbox)]
    bottoms = [bottom for bottom in bottoms if bottom >= previous_top - ENEMY_GROUND_PROBE]
    return min(bottoms) if bottoms else None


# Collision boxes lose 1 px a side, so a standing enemy probes this far into the floor, and a solid this far above its feet is floor.
ENEMY_GROUND_PROBE = 3
GROUND_BEHAVIORS = ('patrol', 'jumper', 'scripted')
KNOCKBACK_BEHAVIORS = GROUND_BEHAVIORS + ('flyer',)


def _stand_on(enemy, floor):
    enemy.y = _solid_top(floor) + abs(get_height(enemy.hitbox)) / 2 - enemy.hitboxOffsetY
    _sync_enemy_hitbox(enemy)


def _ride_ground(enemy):
    # A grounded enemy moves with the moving platform it stands on, and so does its patrol range.
    # A Scripted enemy's spawnX stays where it was placed, since its code may steer by it.
    ride = enemy.groundSolid
    if enemy.airborne or ride is None or ride._destroyed:
        return
    enemy.x += getattr(ride, 'dx', 0)
    if enemy.behavior != 'scripted':
        enemy.spawnX += getattr(ride, 'dx', 0)
    enemy.y += getattr(ride, 'dy', 0)


def _fall_to_last_ground(enemy, gravity):
    # In a room with no platforms, the height an enemy last stood at is its floor, so it can still hop.
    if not enemy.airborne and enemy.hopDy <= 0:
        return False
    enemy.hopDy = max(enemy.hopDy + gravity, enemy.maxFallSpeed)
    enemy.y += enemy.hopDy
    floor_y = enemy.lastGround[1]
    if enemy.y > floor_y:
        enemy.airborne = True
        _sync_enemy_hitbox(enemy)
        return False
    enemy.y = floor_y
    enemy.airborne = False
    enemy.hopDy = 0
    _sync_enemy_hitbox(enemy)
    return True


def _enemy_fall(enemy, gravity):
    # Gravity for an enemy that walks or hops, stopping at floors and ceilings; True on the frame it lands.
    if getattr(game, 'mapBottom', None) is None:
        return _fall_to_last_ground(enemy, gravity)
    _ride_ground(enemy)
    _sync_enemy_hitbox(enemy)
    half = abs(get_height(enemy.hitbox)) / 2
    previous_bottom = enemy.hitbox.y - half
    previous_top = enemy.hitbox.y + half
    if not enemy.airborne and enemy.hopDy <= 0 and _still_on(enemy, enemy.groundSolid, previous_bottom):
        enemy.lastGround = (enemy.x, enemy.y)
        enemy.fallsOut = 0
        return False
    if enemy.airborne or enemy.hopDy > 0:
        enemy.hopDy = max(enemy.hopDy + gravity, enemy.maxFallSpeed)
        step = enemy.hopDy
    else:
        step = -ENEMY_GROUND_PROBE
    enemy.y += step
    _sync_enemy_hitbox(enemy)
    if step <= 0:
        floor = _floor_below(enemy, previous_bottom)
        if floor is not None:
            _stand_on(enemy, floor)
            enemy.groundSolid = floor
            landed = enemy.airborne
            enemy.airborne = False
            enemy.hopDy = 0
            enemy.lastGround = (enemy.x, enemy.y)
            enemy.fallsOut = 0
            return landed
    else:
        ceiling = _ceiling_above(enemy, previous_top)
        if ceiling is not None:
            enemy.y = ceiling - half - enemy.hitboxOffsetY
            _sync_enemy_hitbox(enemy)
            enemy.hopDy = 0
    enemy.groundSolid = None
    enemy.airborne = True
    return False


def _enemy_gravity(enemy):
    return enemy.fallGravity if enemy.behavior == 'patrol' else enemy.hopGravity


def _unsquash_jumper(enemy):
    # Undo last frame's squash offset, so the hop works with the real position.
    enemy.scaleY = 1
    enemy.y += get_height(enemy) * (1 - enemy.sqY) / 2


def _squash_jumper(enemy):
    # Draw squashed with the feet where the hitbox's feet are.
    enemy.y -= get_height(enemy) * (1 - enemy.sqY) / 2
    enemy.scaleX = getattr(enemy, 'artFacing', 1) * enemy.dir * enemy.sqX
    enemy.scaleY = enemy.sqY


def _jumper_step(enemy):
    # Hop, land, pause, repeat - moves sideways only while in the air.
    if _enemy_fall(enemy, enemy.hopGravity):
        enemy.sqX = enemy.landingSquashX
        enemy.sqY = enemy.landingSquashY
    if enemy.airborne:
        if _wall_ahead(enemy):
            enemy.dir = -enemy.dir
        enemy.x += enemy.dir * enemy.speed
    elif enemy.hopPause > 0:
        enemy.hopPause -= 1
    else:
        _choose_patrol_direction(enemy, enemy.y, _hop_reach(enemy), False)
        enemy.hopDy = enemy.jumpSpeed
        enemy.airborne = True
        enemy.hopPause = enemy.hopPauseMax
        enemy.sqX = enemy.jumpSquashX
        enemy.sqY = enemy.jumpSquashY
    if enemy.hopDy > 0:
        _apply_pose(enemy, enemy.jumpUpPose)
    elif not enemy.airborne:
        _apply_pose(enemy, enemy.idlePose)
    else:
        _apply_pose(enemy, enemy.jumpDownPose)
    enemy.sqX += (1.0 - enemy.sqX) * enemy.squashEaseRate
    enemy.sqY += (1.0 - enemy.sqY) * enemy.squashEaseRate


def _fall_while_staggered(enemy):
    # A staggered or beaten enemy keeps falling, so a knockback can push it off a ledge; a flying one falls only once beaten.
    if enemy.behavior not in GROUND_BEHAVIORS or (enemy.flying and not enemy.dying):
        return
    _enemy_fall(enemy, _enemy_gravity(enemy))
    _fell_out_of_room(enemy)


def _settle_on_floor(enemy):
    # A ground enemy placed overlapping a floor stands on top of the one under its middle, not a step beside it.
    _sync_enemy_hitbox(enemy)
    floors = [solid for solid in _live_solids(enemy.hitbox)
              if _solid_top(solid) <= enemy.hitbox.y + ENEMY_GROUND_PROBE and abs(solid.x - enemy.hitbox.x) <= abs(get_width(solid)) / 2]
    if floors:
        _stand_on(enemy, max(floors, key=_solid_top))


def _fell_out_of_room(enemy):
    # Falling below the room beats an enemy, dropping its pickup where it last stood; a live Boss just returns there.
    mapBottom = getattr(game, 'mapBottom', None)
    margin = getattr(game, 'fallMarginOverride', None)
    if mapBottom is None or enemy.y >= mapBottom - (PLAYER_CONFIG['fallMargin'] if margin is None else margin):
        return False
    enemy.airborne = False
    enemy.hopDy = 0
    if enemy.isBoss and not enemy.dying and enemy.fallsOut < 2:
        # Falls in a row without landing: the first returns it to its last spot, the second to where it was placed, the third beats it.
        enemy.x, enemy.y = enemy.lastGround if enemy.fallsOut == 0 else enemy.home
        enemy.fallsOut += 1
        _sync_enemy_hitbox(enemy)
        return False
    enemy.x, enemy.y = enemy.lastGround
    if not enemy.dying:
        _defeat_enemy(enemy)
    # A flying enemy is left waiting to land before it drops its pickup; it never will now.
    if enemy.dropPending:
        enemy.dropPending = False
        _drop_pickup(enemy)
    destroy_object(enemy)
    return True


def _step_dying(enemy):
    # A beaten enemy flashes, falling until it lands; it is removed once it is on the ground and the flash is over.
    _fall_while_staggered(enemy)
    if enemy._destroyed or enemy.airborne:
        return
    if enemy.dropPending:
        enemy.dropPending = False
        _drop_pickup(enemy)
    if enemy.hitFlashTimer <= 0:
        destroy_object(enemy)


def _step_enemy(enemy):
    # One frame of a live or beaten enemy, with a jumper's squash already undone.
    if enemy.dying:
        _step_dying(enemy)
        return
    if _hit_stopped():
        return
    if _step_stagger(enemy):
        _fall_while_staggered(enemy)
        return
    _move_enemy(enemy)
    if enemy._destroyed or enemy.dying:
        return
    if enemy.behavior in GROUND_BEHAVIORS and _fell_out_of_room(enemy):
        return
    _sync_enemy_hitbox(enemy)
    if enemy.projectile is not None and enemy.behavior != 'scripted':
        enemy.fireTimer -= 1
        if enemy.fireTimer <= 0 and _player_in_range(enemy):
            _fire_projectile(enemy, enemy.projectile, enemy.dir, False)
            enemy.fireTimer = enemy.shootInterval


def _move_enemy(enemy):
    if enemy.behavior == 'patrol':
        # Turns around at an edge, a wall or patrolRange, whichever comes first.
        if not enemy.airborne:
            _patrol_step(enemy, enemy.y)
        _enemy_fall(enemy, enemy.fallGravity)
    elif enemy.behavior == 'flyer':
        _flyer_step(enemy)
    elif enemy.behavior == 'dropper':
        _dropper_step(enemy)
    elif enemy.behavior == 'scripted':
        _scripted_step(enemy)
    elif enemy.behavior == 'jumper':
        _jumper_step(enemy)


def _flyer_step(enemy):
    if _wall_ahead(enemy):
        enemy.dir = -enemy.dir
    enemy.x += enemy.dir * enemy.speed
    if enemy.x > enemy.spawnX + enemy.patrolRange:
        enemy.dir = -1
    elif enemy.x < enemy.spawnX - enemy.patrolRange:
        enemy.dir = 1
    enemy.scaleX = getattr(enemy, 'artFacing', 1) * enemy.dir


def _dropper_step(enemy):
    # Waits at its start, shakes when the player passes underneath, falls, rests on the floor, then rises back.
    if enemy.dropState == 'wait':
        _apply_pose(enemy, enemy.idlePose)
        if enemy.dropPause > 0:
            enemy.dropPause -= 1
            return
        player = getattr(game, 'player', None)
        if player is not None and not player._destroyed and player.y < enemy.y and abs(player.x - enemy.hitbox.x) <= abs(get_width(enemy.hitbox)) / 2 + enemy.senseWidth:
            enemy.dropState = 'warn'
            enemy.dropPause = enemy.warnFrames
            _apply_pose(enemy, enemy.droppingPose)
    elif enemy.dropState == 'warn':
        # Shakes in place before falling.
        enemy.dropPause -= 1
        enemy.x = enemy.spawnX + (enemy.warnShake if enemy.dropPause % 4 < 2 else -enemy.warnShake)
        if enemy.dropPause <= 0:
            enemy.x = enemy.spawnX
            enemy.dropState = 'fall'
            enemy.dropDy = 0
    elif enemy.dropState == 'fall':
        previous_bottom = enemy.hitbox.y - abs(get_height(enemy.hitbox)) / 2
        enemy.dropDy = max(enemy.dropDy + enemy.fallGravity, enemy.maxFallSpeed)
        enemy.y += enemy.dropDy
        _sync_enemy_hitbox(enemy)
        floor = _floor_below(enemy, previous_bottom)
        if floor is not None:
            _stand_on(enemy, floor)
            enemy.dropState = 'landed'
            enemy.dropPause = enemy.landedPauseMax
            if _on_screen(enemy):
                _add_camera_shake()
                _play_sound('dropper')
        elif enemy.y < enemy.spawnY - enemy.maxFall:
            enemy.dropState = 'rise'
    elif enemy.dropState == 'landed':
        enemy.dropPause -= 1
        if enemy.dropPause <= 0:
            enemy.dropState = 'rise'
    else:
        _apply_pose(enemy, enemy.idlePose)
        enemy.y = min(enemy.y + enemy.riseSpeed, enemy.spawnY)
        if enemy.y >= enemy.spawnY:
            enemy.dropState = 'wait'
            enemy.dropPause = enemy.topPauseMax


def _freeze_for_win(obj):
    # Once the level is won: show the still pose once, facing the same way.
    if obj.winFrozen:
        return
    obj.winFrozen = True
    facing = 1 if obj.scaleX * getattr(obj, 'artFacing', 1) >= 0 else -1
    _apply_pose(obj, _load_pose(obj.stillPose, fps=0))
    obj.scaleX = getattr(obj, 'artFacing', 1) * facing


def _fire_projectile(shooter, name, direction, from_player, shot=None):
    # shot can hold: 'aim', a unit (dx, dy) to fly along instead of straight ahead; 'size'; 'speed';
    # 'art', replacing the projectile's own art; and 'levelY', a height the shot heads for at 45 degrees
    # before flying straight ahead.
    shot = shot or {}
    aim = shot.get('aim')
    size = shot.get('size', 1)
    level_y = shot.get('levelY')
    p = Projectile()
    projectileSprite = shot.get('art') or PROJECTILE_TYPES[name]['sprite']
    _apply_pose(p, _load_pose(projectileSprite))
    p.stillPose = projectileSprite
    p.hitbox = _pose_hitbox(projectileSprite)
    p.vx, p.vy = (direction, 0) if aim is None else aim
    p.dir = direction
    p.scaleX = getattr(p, 'artFacing', 1) * direction * size
    p.scaleY = size
    p.x = shooter.hitbox.x + p.vx * abs(get_width(shooter.hitbox)) / 2
    p.y = (shooter.y if from_player else shooter.hitbox.y) + p.vy * abs(get_height(shooter.hitbox)) / 2
    p.speed = (PROJECTILE_CONFIG['playerSpeed'] if from_player else PROJECTILE_CONFIG['enemySpeed']) if shot.get('speed') is None else shot['speed']
    if level_y is not None and level_y != p.y:
        p.levelY = level_y
        p.vx = direction * 0.7071
        p.vy = 0.7071 if level_y > p.y else -0.7071
    p.angle = _travel_angle(p)
    p.damage = PROJECTILE_CONFIG['damage']
    p.maxDistance = PROJECTILE_CONFIG['maxDistance'] if from_player else shooter.bulletDistance
    p.fromPlayer = from_player
    p._visitToken = game.visitToken
    if from_player:
        _play_sound('shoot')
    return p


def _travel_angle(p):
    # The art points the way it flies; angle turns it counterclockwise after its left/right flip.
    import math
    return math.degrees(math.atan2(p.vy * p.dir, p.vx * p.dir))


def _projectile_touches(projectile, other):
    # Only the projectile's drawn pixels collide, when its art says where they are.
    return projectile.hitbox is None or _hitbox_touches(projectile, projectile.hitbox, other)


def _player_in_range(enemy):
    player = _live_player()
    if player is None:
        return False
    reach = enemy.noticeRange
    return abs(player.x - enemy.x) <= reach and abs(player.y - enemy.y) <= reach / 2


def _foot_inset(cfg, height):
    # Empty rows below the art: the space under the type's hitbox, if it has one.
    box = cfg.get('hitbox')
    return 0 if box is None else (1 - box['y'] - box['height']) * height


def _fit_enemy_hitbox(enemy, box):
    # box is fractions of the art frame from its unflipped top-left; None is the whole frame.
    if box is None:
        box = {'x': 0, 'y': 0, 'width': 1, 'height': 1}
    width = abs(get_width(enemy))
    height = abs(get_height(enemy))
    if enemy.hitboxBase is None:
        # get_width and get_height include scale, so a refit scales from the size measured before the first fit.
        enemy.hitboxBase = (get_width(enemy.hitbox), get_height(enemy.hitbox))
    enemy.hitbox.scaleX = width * box['width'] / enemy.hitboxBase[0]
    enemy.hitbox.scaleY = height * box['height'] / enemy.hitboxBase[1]
    enemy.hitboxOffsetX = (box['x'] + box['width'] / 2 - 0.5) * width
    enemy.hitboxOffsetY = (0.5 - box['y'] - box['height'] / 2) * height
    _sync_enemy_hitbox(enemy)


def _sync_enemy_hitbox(enemy):
    enemy.hitbox.x = enemy.x + (enemy.hitboxOffsetX if enemy.scaleX >= 0 else -enemy.hitboxOffsetX)
    enemy.hitbox.y = enemy.y + enemy.hitboxOffsetY


def _apply_anchor(y, anchor, height, what, footInset=0):
    # 'center' places the sprite center exactly at the resolved position
    # (the uniform default, for both factories and grid-dispatched
    # characters). 'cell_bottom' stands the visible art on the bottom of the
    # cell-height box around that position - footInset is the empty rows
    # below the type's hitbox - and does not search for floor geometry. It needs
    # grid metadata regardless of whether at= was cell(), world(), or a name.
    if anchor == 'center':
        return y
    if anchor == 'cell_bottom':
        if getattr(game, 'mapRows', None) is None:
            raise ValueError(f"{what}'s anchor='cell_bottom' needs a room with a nonempty grid.")
        return y - CELL / 2 + height / 2 - footInset
    raise ValueError(f"{what}'s anchor must be 'center' or 'cell_bottom'.")


def add_npc(*, at, lines=None, type=None, id=None, anchor='center'):
    # lines is a list whose elements are either a plain string or a
    # {'speaker': ..., 'text': ...} dict. Speaker labels belong to the
    # dialogue data, not to the character placement. Touch the NPC and press
    # 'e' to advance. type picks the visual from NPC_TYPES.
    x, y = _resolve_at(at)
    _reserve_id(id)
    if lines is None:
        raise ValueError('add_npc needs lines - the list of things they say.')
    if not isinstance(lines, list):
        raise ValueError('add_npc needs lines to be a list.')
    _validate_dialogue_lines(lines, 'add_npc')
    n = NPC()
    cfg = _require_type(NPC_TYPES, type, "add_npc's type")
    poses = cfg['poses']
    idlePose = _resolve_pose(poses, 'idle')
    _apply_pose(n, _load_pose(idlePose))
    n.stillPose = idlePose
    n.scaleX = getattr(n, 'artFacing', 1)
    n.lines = lines
    n.interactSeq = _next_interact_seq()
    n.x = x
    n.y = _apply_anchor(y, anchor, get_height(n), 'add_npc', _foot_inset(cfg, get_height(n)))
    _register_instance('npc', type, n, id=id)
    return n


def add_enemy(*, at, type=None, id=None, patrol_range=None, facing=1, anchor='center', shoot_interval=None):
    # type picks a whole enemy type - look, behavior, contactDamage,
    # maxHealth, and speed together, not independent choices.
    x, y = _resolve_at(at)
    _reserve_id(id)
    if facing not in (-1, 1):
        raise ValueError('add_enemy needs facing to be exactly -1 or 1.')
    explicit_patrol_range = patrol_range is not None
    if patrol_range is None:
        patrol_range = ENEMY_DEFAULTS['patrolRange']
    if isinstance(patrol_range, bool) or not isinstance(patrol_range, (int, float)) or patrol_range < 0:
        raise ValueError('add_enemy needs patrol_range to be a finite nonnegative number.')
    if shoot_interval is not None and (not _finite_number(shoot_interval) or shoot_interval <= 0):
        raise ValueError(f'add_enemy needs shoot_interval to be a number of frames above 0, not {shoot_interval!r}.')
    cfg = _require_type(ENEMY_TYPES, type, 'add_enemy')
    behavior = cfg['behavior']
    if behavior not in ENEMY_BEHAVIORS:
        raise ValueError(f"Enemy type {type!r} uses unknown behavior {behavior!r}.")
    poses = cfg['poses']
    e = Enemy()
    e.x = x
    e.y = y
    e.behavior = behavior
    e.patrolRange = patrol_range * UNIT if explicit_patrol_range else patrol_range
    e.speed = cfg.get('speed', 2 / 3 * UNIT)
    e.dir = facing
    e.contactDamage = cfg.get('contactDamage', 1)
    e.health = cfg.get('maxHealth', 1)
    e.projectile = cfg.get('projectile')
    e.bulletDistance = cfg.get('bulletDistance', PROJECTILE_CONFIG['maxDistance'])
    e.noticeRange = cfg.get('noticeRange', PROJECTILE_CONFIG['enemyRange'])
    e.drop = cfg.get('drop')
    e.dropChance = cfg.get('dropChance', 100)
    e.dropSetsGlobal = cfg.get('dropSetsGlobal')
    if e.dropSetsGlobal is not None:
        _validate_global(e.dropSetsGlobal, 'add_enemy')
        if _global_type(e.dropSetsGlobal) != 'bool':
            raise ValueError(f"Enemy type {type!r} drops a pickup that sets {e.dropSetsGlobal!r}, which is type {_global_type(e.dropSetsGlobal)!r}; it must be a boolean global.")
    e.typeName = type
    e.maxHealth = e.health
    e.poses = poses
    e.isBoss = cfg.get('boss', False) is True
    e.beatenSetsGlobal = cfg.get('beatenSetsGlobal')
    if e.beatenSetsGlobal is not None:
        _validate_global(e.beatenSetsGlobal, 'add_enemy')
        if _global_type(e.beatenSetsGlobal) != 'bool':
            raise ValueError(f"Enemy type {type!r} sets {e.beatenSetsGlobal!r} when beaten, which is type {_global_type(e.beatenSetsGlobal)!r}; it must be a boolean global.")
    e.shootInterval = PROJECTILE_CONFIG['enemyFireInterval'] if shoot_interval is None else shoot_interval
    e.fireTimer = e.shootInterval
    e.stillPose = _resolve_pose(poses, 'idle')
    for key, value in ENEMY_BEHAVIORS.get(behavior, {}).items():
        setattr(e, key, value)

    if behavior == 'dropper':
        e.invincible = True
        e.idlePose = _load_pose(_resolve_pose(poses, 'idle'))
        e.droppingPose = _load_pose(_resolve_pose(poses, 'dropping'))
        _apply_pose(e, e.idlePose)
    elif behavior == 'jumper':
        e.jumpUpPose = _load_pose(_resolve_pose(poses, 'jumpUp'))
        e.jumpDownPose = _load_pose(_resolve_pose(poses, 'jumpDown'))
        e.idlePose = _load_pose(_resolve_pose(poses, 'idle'))
        _apply_pose(e, e.jumpUpPose)
    elif behavior == 'patrol':
        _set_character_pose(e, poses, 'run')
    else:
        _set_character_pose(e, poses, 'idle')
    e.scaleX = getattr(e, 'artFacing', 1) * e.dir
    e.y = _apply_anchor(y, anchor, get_height(e), 'add_enemy', _foot_inset(cfg, get_height(e)))
    _fit_enemy_hitbox(e, cfg.get('hitbox'))
    if behavior in GROUND_BEHAVIORS:
        _settle_on_floor(e)
    e.spawnX = e.x
    e.spawnY = e.y
    e.lastGround = (e.x, e.y)
    _register_instance('enemy', type, e, id=id)
    if e.isBoss:
        _add_boss_bar(e)
    if behavior == 'scripted':
        e.poseName = 'idle'
        start = _enemy_script(e, 'start')
        e.loopScript = _enemy_script(e, 'loop')
        if start is not None:
            maxHealth = e.maxHealth
            start(e)
            if e._destroyed:
                return e
            _check_enemy_fields(e, 'Start')
            if e.maxHealth == maxHealth:
                e.maxHealth = e.health
            _face_enemy_art(e)
            _fit_enemy_hitbox(e, cfg.get('hitbox'))
            if not e.flying:
                _settle_on_floor(e)
            e.spawnX = e.x
            e.spawnY = e.y
            e.lastGround = (e.x, e.y)
    e.home = (e.x, e.y)
    return e


def _enemy_script(enemy, phase):
    scripts = ENEMY_SCRIPTS.get(enemy.typeName)
    return None if scripts is None else scripts[phase]


def _face_enemy_art(enemy):
    enemy.dir = -1 if enemy.dir < 0 else 1
    enemy.scaleX = getattr(enemy, 'artFacing', 1) * enemy.dir * (abs(enemy.scaleX) or 1)


def _check_enemy_fields(enemy, phase):
    # The message starts "In <label>'s <phase> code:", which Studio uses to point at that code.
    for name in ('x', 'y', 'dir', 'speed', 'health', 'maxHealth'):
        value = getattr(enemy, name)
        if not _finite_number(value):
            raise ValueError(f"In {ENEMY_SCRIPTS[enemy.typeName]['label']}'s {phase} code: self.{name} needs to be a number, not {value!r}.")
    if not isinstance(enemy.flying, bool):
        raise ValueError(f"In {ENEMY_SCRIPTS[enemy.typeName]['label']}'s {phase} code: self.flying needs to be True or False, not {enemy.flying!r}.")


def _scripted_step(enemy):
    loop = enemy.loopScript
    startX = enemy.x
    startY = enemy.y
    if loop is not None:
        loop(enemy)
    if enemy._destroyed:
        return
    if loop is not None:
        _check_enemy_fields(enemy, 'Loop')
    _stop_at_walls(enemy, startX)
    _stop_at_floor(enemy, startY)
    _stop_at_ceiling(enemy, startY)
    if enemy.flying:
        enemy.airborne = False
        enemy.hopDy = 0
        enemy.groundSolid = None
    else:
        _enemy_fall(enemy, enemy.hopGravity)
    _face_enemy_art(enemy)


def _stop_at_walls(enemy, startX):
    # Walls and the room's edge undo a Scripted enemy's sideways move, unless it started inside a wall.
    if enemy.x == startX:
        return
    _sync_enemy_hitbox(enemy)
    if not _in_wall(enemy):
        return
    movedX = enemy.x
    enemy.x = startX
    _sync_enemy_hitbox(enemy)
    if _in_wall(enemy):
        enemy.x = movedX
        _sync_enemy_hitbox(enemy)


def _stop_at_floor(enemy, startY):
    # A Scripted enemy's code that moves it down into a floor leaves it standing on that floor.
    if enemy.y >= startY:
        return
    _sync_enemy_hitbox(enemy)
    feet = enemy.hitbox.y - abs(get_height(enemy.hitbox)) / 2
    floor = _floor_below(enemy, feet + startY - enemy.y, 0)
    if floor is not None:
        _stand_on(enemy, floor)


def _stop_at_ceiling(enemy, startY):
    # A Scripted enemy's code that moves it up into a ceiling leaves it just under that ceiling.
    if enemy.y <= startY:
        return
    _sync_enemy_hitbox(enemy)
    half = abs(get_height(enemy.hitbox)) / 2
    ceiling = _ceiling_above(enemy, enemy.hitbox.y + half - (enemy.y - startY))
    if ceiling is not None:
        enemy.y = ceiling - half - enemy.hitboxOffsetY
        _sync_enemy_hitbox(enemy)


def _require_enemy(enemy, what):
    _require_live_handle(enemy, what)
    if not getattr(enemy, '_isEnemy', False):
        raise ValueError(f"{what} needs an enemy, such as self in an enemy's code.")


def _live_player():
    player = getattr(game, 'player', None)
    return None if player is None or player._destroyed else player


def face_player(enemy):
    _require_enemy(enemy, 'face_player')
    player = _live_player()
    if player is not None and player.x != enemy.x:
        enemy.dir = 1 if player.x > enemy.x else -1
        _face_enemy_art(enemy)


def player_distance(enemy):
    _require_enemy(enemy, 'player_distance')
    player = _live_player()
    if player is None:
        return None
    return (player.x - enemy.x, player.y - enemy.y)


MAX_SHOT_SIZE = 4
MAX_SHOT_SPEED = 20


def _shot_aim(enemy):
    # A unit (dx, dy) from the enemy toward the player's middle, or None with no player.
    player = _live_player()
    if player is None:
        return None
    target = getattr(player, 'hitbox', None) or player
    dx = target.x - enemy.hitbox.x
    dy = target.y - enemy.hitbox.y
    length = (dx * dx + dy * dy) ** 0.5
    return None if length == 0 else (dx / length, dy / length)


def _check_shot(at_player, size, speed, sprite, level_y):
    if level_y is not None and not _finite_number(level_y):
        raise ValueError(f'enemy_shoot needs level_y to be a height in the room, such as self.y - 20, not {level_y!r}.')
    if not isinstance(at_player, bool):
        raise ValueError(f'enemy_shoot needs at_player to be True or False, not {at_player!r}.')
    if level_y is not None and at_player:
        raise ValueError('enemy_shoot can aim at_player or head for level_y, not both.')
    if not _finite_number(size) or not 0 < size <= MAX_SHOT_SIZE:
        raise ValueError(f'enemy_shoot needs size to be a number above 0 and at most {MAX_SHOT_SIZE}, not {size!r}.')
    if speed is not None and (not _finite_number(speed) or not 0 < speed <= MAX_SHOT_SPEED):
        raise ValueError(f'enemy_shoot needs speed to be a number of pixels per frame above 0 and at most {MAX_SHOT_SPEED}, not {speed!r}.')
    if sprite is not None and (not isinstance(sprite, str) or not sprite):
        raise ValueError(f"enemy_shoot needs sprite to be an art name such as 'fireball.png', not {sprite!r}.")


def enemy_shoot(enemy, at_player=False, size=1, speed=None, sprite=None, level_y=None):
    _require_enemy(enemy, 'enemy_shoot')
    _check_shot(at_player, size, speed, sprite, level_y)
    if enemy.projectile is None and sprite is None:
        raise ValueError("enemy_shoot needs the enemy to have a projectile, or a sprite='art name'. Choose a projectile in Characters.")
    if enemy.dying:
        return None
    _face_enemy_art(enemy)
    _sync_enemy_hitbox(enemy)
    aim = _shot_aim(enemy) if at_player else None
    direction = enemy.dir if aim is None or aim[0] == 0 else (1 if aim[0] > 0 else -1)
    return _fire_projectile(enemy, enemy.projectile, direction, False, {'aim': aim, 'size': size, 'speed': None if speed is None else speed * UNIT, 'art': sprite, 'levelY': level_y})


def wall_ahead(enemy):
    _require_enemy(enemy, 'wall_ahead')
    return _wall_ahead(enemy)


def ground_ahead(enemy):
    _require_enemy(enemy, 'ground_ahead')
    return _ground_ahead(enemy, -1 if enemy.dir < 0 else 1, enemy.y)


def set_pose(enemy, name):
    _require_enemy(enemy, 'set_pose')
    if enemy.behavior != 'scripted':
        raise ValueError('set_pose only works for an enemy with the Scripted behaviour.')
    if name not in ENEMY_POSE_NAMES:
        names = ', '.join(repr(pose) for pose in ENEMY_POSE_NAMES)
        raise ValueError(f"set_pose needs one of {names}, not {name!r}.")
    if enemy.poseName == name or enemy.dying:
        return
    enemy.poseName = name
    _set_character_pose(enemy, enemy.poses, name)
    _face_enemy_art(enemy)


def jump(enemy, speed):
    _require_enemy(enemy, 'jump')
    if not _finite_number(speed) or speed <= 0:
        raise ValueError('jump needs a speed above 0, in pixels per frame.')
    if enemy.behavior != 'scripted':
        raise ValueError('jump only works for an enemy with the Scripted behaviour.')
    if enemy.airborne or enemy.flying:
        return
    enemy.airborne = True
    enemy.hopDy = speed * UNIT


def in_air(enemy):
    _require_enemy(enemy, 'in_air')
    return enemy.airborne


def _live_boss_bars():
    # Bars from an earlier room are not always marked destroyed, so a bar also has to belong to this visit.
    return [bar for bar in getattr(game, 'bossBars', []) if not bar._destroyed and bar.visit == game.visitToken]


def _add_boss_bar(enemy):
    bars = _live_boss_bars()
    bar = BossBar()
    bar.visit = game.visitToken
    bar.owner = enemy
    bar.label.text = _boss_name(enemy.typeName)
    bars.append(bar)
    game.bossBars = bars


def _boss_name(type_name):
    name = ENEMY_TYPES[type_name].get('name')
    return name if isinstance(name, str) and name else type_name.replace('_', ' ').title()