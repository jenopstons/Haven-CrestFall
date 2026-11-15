# Melee attacks, hit-stop, stagger, shooting limits, the meter, healing, pickup effects and unlocks.
# Each reads COMBAT_CONFIG and changes nothing while its setting is off.


def _melee_on():
    return COMBAT_CONFIG['melee'] == 1


def _hit_stopped():
    return getattr(game, 'hitStop', 0) > 0


def _step_hit_stop():
    # The player counts the freeze down, so it runs exactly once per frame.
    if not _hit_stopped():
        return False
    game.hitStop -= 1
    return True


def _swing_frames():
    return COMBAT_CONFIG['windupFrames'] + COMBAT_CONFIG['activeFrames'] + COMBAT_CONFIG['recoveryFrames']


def _attack_direction(player):
    if not _unlocked('upDown'):
        return 'side'
    if COMBAT_CONFIG['upAttack'] == 1 and _control_is_pressed('aimUp'):
        return 'up'
    if COMBAT_CONFIG['downAttack'] == 1 and not player.onGround and _control_is_pressed('aimDown'):
        return 'down'
    return 'side'


def _start_attack(player):
    if not _melee_on() or not _unlocked('melee') or player.attackTimer > 0 or not _control_was_pressed('attack'):
        return
    strike = Strike()
    pose = _load_pose(PLAYER_CONFIG['poses'].get('strike'))
    strike.hasArt = pose is not None
    _apply_pose(strike, pose)
    strike.direction = _attack_direction(player)
    strike.facing = player.facing
    strike.visible = False
    strike.hitbox = StrikeHitbox()
    player.strike = strike
    player.attackTimer = _swing_frames()
    _place_strike(player, strike)


def _strike_size(player, strike):
    if strike.hasArt:
        return abs(get_width(strike)), abs(get_height(strike))
    return abs(get_width(player.hitbox)), abs(get_height(player.hitbox))


def _place_strike(player, strike):
    # Strike art points right; up and down attacks turn it, so its length runs along the attack.
    length, thickness = _strike_size(player, strike)
    halfWidth = abs(get_width(player.hitbox)) / 2
    halfHeight = abs(get_height(player.hitbox)) / 2
    if strike.direction == 'side':
        strike.x = player.hitbox.x + strike.facing * (halfWidth + length / 2)
        strike.y = player.hitbox.y
        strike.angle = 0
        strike.scaleX = getattr(strike, 'artFacing', 1) * strike.facing
        boxWidth, boxHeight = length, thickness
    else:
        sign = 1 if strike.direction == 'up' else -1
        strike.x = player.hitbox.x
        strike.y = player.hitbox.y + sign * (halfHeight + length / 2)
        strike.angle = 90 * sign
        strike.scaleX = getattr(strike, 'artFacing', 1)
        boxWidth, boxHeight = thickness, length
    box = strike.hitbox
    box.scaleX = boxWidth / box.baseWidth
    box.scaleY = boxHeight / box.baseHeight
    box.x = strike.x
    box.y = strike.y


def _end_attack(player):
    strike = getattr(player, 'strike', None)
    if strike is not None:
        for piece in (strike.hitbox, strike):
            if not piece._destroyed:
                destroy(piece)
    player.strike = None
    player.attackTimer = 0


def _step_attack(player):
    if player.attackTimer <= 0:
        return
    player.attackTimer -= 1
    strike = player.strike
    age = _swing_frames() - player.attackTimer
    windup = COMBAT_CONFIG['windupFrames']
    active = windup < age <= windup + COMBAT_CONFIG['activeFrames']
    _place_strike(player, strike)
    strike.visible = active and strike.hasArt
    if active:
        hit = _strike_hits(player, strike)
        if age == windup + 1 and not hit:
            _play_sound('swing')
    if player.attackTimer == 0:
        _end_attack(player)


def _attack_pose_showing(player):
    return player.attackTimer > COMBAT_CONFIG['recoveryFrames']


def _strike_hits(player, strike):
    hit = False
    for enemyHitbox in get_collision_list(strike.hitbox, 'EnemyHitbox'):
        enemy = enemyHitbox.owner
        if enemy._destroyed or enemy.dying or enemy in strike.hitTargets:
            continue
        strike.hitTargets.append(enemy)
        hit = True
        _pogo(player, strike)
        if _hurt_enemy(enemy, COMBAT_CONFIG['meleeDamage'], False):
            _gain_meter(COMBAT_CONFIG['meterPerHit'])
            _stagger_enemy(enemy, player)
    if strike.direction == 'down':
        for hazard in get_collision_list(strike.hitbox, 'Hazard'):
            if hazard.visible:
                _pogo(player, strike)
    return hit


def _pogo(player, strike):
    if strike.direction != 'down' or COMBAT_CONFIG['pogo'] != 1 or strike.pogoed:
        return
    strike.pogoed = True
    player.dy = player.jumpSpeed * player.stompBounce
    _refill_abilities(player)
    player.jumped = True
    player.coyoteTimer = 0


def _stagger_enemy(enemy, player):
    game.hitStop = COMBAT_CONFIG['hitStop']
    if enemy.dying:
        return
    enemy.staggerTimer = COMBAT_CONFIG['stagger']
    direction = 1 if enemy.x >= player.x else -1
    _knock_back_enemy(enemy, direction)


def _in_wall(enemy):
    # A solid reaching above the enemy's feet is a wall, as is the room's edge; the floor it stands on is not.
    feet = enemy.hitbox.y - abs(get_height(enemy.hitbox)) / 2
    return any(solid.y + abs(get_height(solid)) / 2 > feet + 1 for solid in _live_solids(enemy.hitbox, edges=True))


def _knock_back_fits(enemy, direction, distance):
    startX = enemy.x
    enemy.x += direction * distance
    _sync_enemy_hitbox(enemy)
    if _in_wall(enemy):
        enemy.x = startX
        _sync_enemy_hitbox(enemy)
        return False
    return True


def _knock_back_enemy(enemy, direction):
    # Enemies stop at a wall but not at a ledge, so they can fall off; stationary enemies and droppers stay put.
    distance = COMBAT_CONFIG['knockback']
    if distance <= 0 or enemy.behavior not in KNOCKBACK_BEHAVIORS:
        return
    if not _knock_back_fits(enemy, direction, distance):
        _knock_back_fits(enemy, direction, distance / 2)


def _step_stagger(enemy):
    if enemy.staggerTimer <= 0:
        return False
    enemy.staggerTimer -= 1
    _sync_enemy_hitbox(enemy)
    return True


def _meter_on():
    return COMBAT_CONFIG['meter'] == 1


def _gain_meter(amount):
    if _meter_on():
        game.meter = min(getattr(game, 'meter', 0) + amount, COMBAT_CONFIG['meterMax'])


def _can_shoot(player):
    ammo = COMBAT_CONFIG['ammo']
    if ammo == 'recharging':
        return player.ammo > 0
    if ammo == 'meter':
        return _meter_on() and getattr(game, 'meter', 0) >= COMBAT_CONFIG['shotCost']
    return True


def _spend_shot(player):
    ammo = COMBAT_CONFIG['ammo']
    if ammo == 'recharging':
        player.ammo -= 1
    elif ammo == 'meter':
        game.meter -= COMBAT_CONFIG['shotCost']


def _recharge_ammo(player):
    # One shot comes back every ammoRechargeFrames while any are spent.
    if COMBAT_CONFIG['ammo'] != 'recharging' or player.ammo >= COMBAT_CONFIG['maxAmmo']:
        player.ammoTimer = 0
        return
    player.ammoTimer += 1
    if player.ammoTimer >= COMBAT_CONFIG['ammoRechargeFrames']:
        player.ammo += 1
        player.ammoTimer = 0


def _step_shooting(player):
    _recharge_ammo(player)
    if player.shootCooldown > 0:
        player.shootCooldown -= 1
        return
    if player.projectile is None or not _unlocked('shoot') or not _control_is_pressed('shoot') or not _can_shoot(player):
        return
    _spend_shot(player)
    _fire_projectile(player, player.projectile, player.facing, True)
    player.shootCooldown = COMBAT_CONFIG['shootCooldown']


def _can_heal(player):
    return (COMBAT_CONFIG['heal'] == 1 and _meter_on() and player.health < _max_health()
            and getattr(game, 'meter', 0) >= COMBAT_CONFIG['healCost'])


def _show_healing(player, healing):
    # The player glows while healing.
    if healing and player.healFilterId is None:
        player.healFilterId = add_filter(player, new_adjustment_filter({ 'brightness': 1.6 }))
    elif not healing and player.healFilterId is not None:
        remove_filter(player, player.healFilterId)
        player.healFilterId = None


def _cancel_heal(player):
    player.healTimer = 0
    _show_healing(player, False)


def _step_heal(player):
    # Holding heal for healFrames spends healCost meter for one health. Letting go or a hit starts over.
    if not _control_is_pressed('heal') or not _can_heal(player):
        _cancel_heal(player)
        return
    player.healTimer += 1
    _show_healing(player, True)
    if player.healTimer >= COMBAT_CONFIG['healFrames']:
        game.meter -= COMBAT_CONFIG['healCost']
        player.health += 1
        player.healTimer = 0
        _play_sound('heal')


def _spawn_ammo_hud(player):
    # One pip per shot, drawn with the player's projectile art; a spent shot is faded.
    if COMBAT_CONFIG['ammo'] != 'recharging' or player.projectile is None:
        return
    layout = UI_CONFIG['ammo']
    pose = _load_pose(PROJECTILE_TYPES[player.projectile]['sprite'])
    for index in range(min(COMBAT_CONFIG['maxAmmo'], layout['displayLimit'])):
        pip = AmmoPip()
        _apply_pose(pip, pose)
        pip.index = index
        size = max(abs(get_width(pip)), abs(get_height(pip)))
        if size > layout['height']:
            pip.scaleX *= layout['height'] / size
            pip.scaleY *= layout['height'] / size
        game.hud_combat.append(pip)


# Adjustment filters that turn pixel.png (pure green) into each HUD colour: saturation 0 makes it a 0.715 grey,
# which red/green/blue and brightness then tint. A light frame and a dark panel show on any background.
HUD_COLOURS = {
    'frame': {'saturation': 0, 'brightness': 1.2},
    'panel': {'saturation': 0, 'brightness': 0.17},
    'track': {'saturation': 0, 'brightness': 0.47},
    'health': {'saturation': 0, 'brightness': 1.26, 'green': 0.22, 'blue': 0.22},
    'meter': {'saturation': 0, 'brightness': 1.4, 'green': 0.8, 'blue': 0.25},
}
HUD_FRAME = 1
# The boss panel's dark space around its bar and above its name, and the share of the font size its letters fill.
BOSS_PANEL_PADDING = 4
BOSS_PANEL_TOP = 2
BOSS_NAME_SHARE = 0.7


def _hud_rect(colour, z):
    rect = HudRect()
    rect.z = z
    add_filter(rect, new_adjustment_filter(HUD_COLOURS[colour]))
    return rect


def _place_hud_rect(rect, x, y, width, height):
    # x and y are the rectangle's centre; a rectangle with no width is hidden.
    rect.visible = width > 0
    rect.x = x
    rect.y = y
    rect.scaleX = max(width, 1) / rect.baseWidth
    rect.scaleY = height / rect.baseHeight


def _place_hud_bar(bar, left, y, layout, share):
    # A framed bar the size of layout's width and height: the dark track, and the fill growing from the left by share (0 to 1).
    width = layout['width']
    height = layout['height']
    _place_hud_rect(bar.frame, left + width / 2, y, width + 2 * HUD_FRAME, height + 2 * HUD_FRAME)
    _place_hud_rect(bar.track, left + width / 2, y, width, height)
    _place_hud_rect(bar.fill, left + width * share / 2, y, width * share, height)


def _spawn_meter_hud():
    # The meter bar sits under the ammo pips, or in their place when there are none.
    if not _meter_on():
        return
    bar = MeterBar()
    bar.layoutY = UI_CONFIG['meter']['y'] if game.hud_combat else UI_CONFIG['ammo']['y']
    game.hud_combat.append(bar)


def _spawn_combat_hud(player):
    game.hud_combat = []
    _spawn_ammo_hud(player)
    _spawn_meter_hud()


PICKUP_EFFECTS = ('none', 'heal', 'maxHealth', 'refill', 'unlock')
UNLOCKABLES = ('melee', 'upDown', 'shoot', 'dash', 'airJump', 'wallJump')


def _unlocked(name):
    # An ability that comes from a pickup is locked until collected; unlocks survive death.
    return COMBAT_CONFIG[name + 'FromPickup'] != 1 or name in getattr(game, 'unlocked', [])


def _max_health():
    return PLAYER_CONFIG['maxHealth'] + getattr(game, 'maxHealthBonus', 0)


def _keep_after_death(collectible):
    # Upgrades stay collected even when the player dies before leaving the room.
    persistentId = getattr(collectible, 'persistentId', None)
    if persistentId is not None:
        game.persistedCheckpoint.setdefault('collectedMapItems', set()).add(persistentId)


def _refill_combat(player):
    player.ammo = COMBAT_CONFIG['maxAmmo']
    if _meter_on():
        game.meter = COMBAT_CONFIG['meterMax']


def _raise_max_health(player):
    game.maxHealthBonus = getattr(game, 'maxHealthBonus', 0) + 1
    player.health += 1
    if UI_CONFIG['lives']['icon'] is not None and len(game.hud_lives) < UI_CONFIG['lives'].get('displayLimit', 10):
        _add_life_icon(len(game.hud_lives), camera_x(), camera_y())


def _unlock(name):
    if name not in game.unlocked:
        game.unlocked.append(name)


def _apply_pickup_effect(collectible):
    # What a collectible Type's Effect does to the player when picked up.
    player = getattr(game, 'player', None)
    if collectible.effect == 'none' or player is None or player._destroyed:
        return
    if collectible.effect == 'heal':
        player.health = min(player.health + collectible.healAmount, _max_health())
    elif collectible.effect == 'refill':
        _refill_combat(player)
    elif collectible.effect == 'maxHealth':
        _raise_max_health(player)
        _keep_after_death(collectible)
    elif collectible.effect == 'unlock':
        _unlock(collectible.unlocks)
        _keep_after_death(collectible)