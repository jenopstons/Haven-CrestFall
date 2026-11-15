# Static and moving platform/wall placement - everything that becomes a
# Platform instance. Terrain factories deliberately take no id=/remember_as=
# in this slice - repeated terrain has no individual persisted identity.


def _track_ground_extent(bottom_y):
    # Tracks the lowest bottom edge among every platform/wall created so
    # far, as game.mapBottom - the player's own fall-off kill-plane check.
    if getattr(game, 'suppressGroundTracking', False):
        return
    current = getattr(game, 'mapBottom', None)
    if current is None or bottom_y < current:
        game.mapBottom = bottom_y


def _new_platform(x, y, type=None, launch_speed=None):
    plat = Platform()
    cfg = _require_type(PLATFORM_TYPES, type, 'add_platform/add_wall')
    _apply_pose(plat, _load_pose(cfg['sprite']))
    plat.scaleX = getattr(plat, 'artFacing', 1)
    plat.tileSprite = _tile_identity(cfg['sprite'])
    # A launcher (spring, trampoline, ...) is still a Platform - its launch
    # strength lives on its type. `isLauncher` is a declared flag any pack's
    # launcher-flavored type can set, not a name match on one skin.
    plat.launchSpeed = launch_speed * UNIT if launch_speed is not None else cfg.get('launchSpeed')
    if plat.launchSpeed is None and cfg.get('isLauncher'):
        plat.launchSpeed = PLAYER_CONFIG['jumpSpeed'] * PLAYER_CONFIG['launchJumpMultiplier']
    plat.springIdlePose = _load_pose(cfg['sprite'])
    plat.springPressedPose = _load_pose(cfg.get('pressedSprite', cfg['sprite']))
    plat.springFrames = cfg.get('pressFrames', 0)
    plat.x = x
    plat.y = y
    _track_ground_extent(plat.y - get_height(plat) / 2)
    _register_instance('platform', type, plat)
    return plat


def add_platform(*, at, type=None, launch_speed=None):
    x, y = _resolve_at(at)
    if launch_speed is not None and (isinstance(launch_speed, bool) or not isinstance(launch_speed, (int, float)) or launch_speed != launch_speed or launch_speed in (float('inf'), float('-inf')) or launch_speed <= 0):
        raise ValueError('add_platform launch_speed must be a positive finite number.')
    return _new_platform(x, y, type, launch_speed)


def add_platform_row(*, at, tiles=None, type=None):
    # Places `tiles` Platforms side by side, spaced by their real measured
    # width so they neither overlap nor gap. Repeated terrain - no id=.
    start_x, start_y = _resolve_at(at)
    if tiles is None:
        raise ValueError('add_platform_row needs tiles - how many tiles to place.')
    result = []
    width = None
    for i in range(tiles):
        plat = _new_platform(start_x, start_y, type)
        if width is None:
            width = get_width(plat)
        plat.x = start_x + i * width
        plat.tileOffset = i * width
        result.append(plat)
    return result


def _start_moving(plat, speed):
    plat.startX = plat.x
    plat.targetX = plat.x
    plat.startY = plat.y
    plat.targetY = plat.y
    plat.speed = speed * UNIT
    plat.moving = True
    return plat


def add_moving_platform(*, at, type=None, to=None, speed=0.5):
    # Single-axis travel only - to= must differ from the anchor on exactly
    # one axis, same convention as add_moving_platform_group's to=.
    x, y = _resolve_at(at)
    if to is None:
        raise ValueError('add_moving_platform needs to= - where it travels to.')
    to_x, to_y = _resolve_at(to)
    plat = _start_moving(_new_platform(x, y, type), speed)
    if to_x != x and to_y == y:
        plat.axis = 'x'
        plat.targetX = to_x
        plat.dir = 1 if to_x > x else -1
    elif to_y != y and to_x == x:
        plat.axis = 'y'
        plat.targetY = to_y
        plat.dir = 1 if to_y > y else -1
    else:
        raise ValueError("add_moving_platform's to= must differ from at on exactly one axis - single-axis travel only.")
    return plat


def add_moving_platform_row(*, at, tiles=None, to=None, speed=0.5, type=None):
    # Each tile's target reuses its own tileOffset from add_platform_row, so
    # the run keeps its real measured-width spacing at the target too.
    x, y = _resolve_at(at)
    if tiles is None:
        raise ValueError('add_moving_platform_row needs tiles - how many tiles to place.')
    if to is None:
        raise ValueError('add_moving_platform_row needs to= - where it travels to.')
    to_x, to_y = _resolve_at(to)
    if to_x != x and to_y == y:
        axis = 'x'
    elif to_y != y and to_x == x:
        axis = 'y'
    else:
        raise ValueError("add_moving_platform_row's to= must differ from at on exactly one axis - single-axis travel only.")
    tiles_list = add_platform_row(at=at, tiles=tiles, type=type)
    for plat in tiles_list:
        _start_moving(plat, speed)
        plat.axis = axis
        if axis == 'y':
            plat.targetY = to_y + (plat.y - tiles_list[0].y)
            plat.dir = 1 if to_y > plat.y else -1
        else:
            plat.targetX = to_x + plat.tileOffset
            plat.dir = 1 if plat.targetX > plat.x else -1
    return tiles_list


def add_moving_platform_group(*, at, parts=None, to=None, speed=0.5):
    # A group of (possibly differently-typed) tiles that move together as
    # one rigid unit - one movement specification for the whole group,
    # instead of patching each grid-placed tile's target independently.
    # parts is a list of {'row_offset', 'col_offset', 'type'} dicts, in CELL
    # units relative to the anchor part (row_offset=0, col_offset=0,
    # positioned at at=); to is where that anchor ends up, and every other
    # part keeps its own relative offset at the target too. Moving-group
    # offsets always use CELL, even in a world room with no grid - the
    # configured tile_size remains its explicit spacing unit.
    x, y = _resolve_at(at)
    if not parts:
        raise ValueError("add_moving_platform_group needs parts - a list of {'row_offset', 'col_offset', 'type'} dicts.")
    if to is None:
        raise ValueError('add_moving_platform_group needs to= - where the anchor part (row_offset=0, col_offset=0) ends up.')
    to_x, to_y = _resolve_at(to)
    if to_x != x and to_y == y:
        axis, target = 'x', to_x
    elif to_y != y and to_x == x:
        axis, target = 'y', to_y
    else:
        raise ValueError("add_moving_platform_group's to= must differ from at on exactly one axis - single-axis travel only.")
    seen_anchor = False
    for part in parts:
        if part.get('row_offset', 0) == 0 and part.get('col_offset', 0) == 0:
            seen_anchor = True
    if not seen_anchor:
        raise ValueError("add_moving_platform_group needs exactly one part at row_offset=0, col_offset=0.")
    plats = []
    for part in parts:
        px = x + part.get('col_offset', 0) * CELL
        py = y - part.get('row_offset', 0) * CELL
        plat = _start_moving(_new_platform(px, py, part.get('type')), speed)
        plat.axis = axis
        if axis == 'x':
            plat.targetX = target + (px - x)
            plat.dir = 1 if plat.targetX > px else -1
        else:
            plat.targetY = target + (py - y)
            plat.dir = 1 if plat.targetY > py else -1
        plats.append(plat)
    return plats


def _new_wall(x, y, type=None):
    # Same Platform class/collision tag as _new_platform - a wall is
    # mechanically identical to a floor, just oriented vertically.
    wall = Platform()
    cfg = _require_type(PLATFORM_TYPES, type, 'add_platform/add_wall')
    _apply_pose(wall, _load_pose(cfg['sprite']))
    wall.scaleX = getattr(wall, 'artFacing', 1)
    wall.tileSprite = _tile_identity(cfg['sprite'])
    wall.x = x
    wall.y = y
    # A wall is standable ground too - its top edge is a real place to land.
    _track_ground_extent(wall.y - get_height(wall) / 2)
    _register_instance('platform', type, wall)
    return wall


def add_wall(*, at, type=None):
    x, y = _resolve_at(at)
    return _new_wall(x, y, type)


def add_wall_column(*, at, tiles=None, type=None):
    # Repeated terrain - no id=. Wall columns extend +y.
    start_x, start_y = _resolve_at(at)
    if tiles is None:
        raise ValueError('add_wall_column needs tiles - how many tiles to place.')
    result = []
    height = None
    for i in range(tiles):
        wall = _new_wall(start_x, start_y, type)
        if height is None:
            height = get_height(wall)
        wall.y = start_y + i * height
        wall.tileOffset = i * height
        result.append(wall)
    return result