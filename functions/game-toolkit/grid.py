# LEGEND-grid scanning and dispatch - turns a map's grid + 'objects' list
# into real object instances, dispatching into every other objects/ file's
# own add_*()/_new_*() factories.


def _add_boundary_wall(x, y, width, height):
    # An invisible solid wall used to contain a bounded room's left/right edges.
    wall = EdgeWall()
    _apply_pose(wall, _load_pose('pixel.png'))
    wall.visible = False
    wall.scaleX = width
    wall.scaleY = height
    wall.x = x
    wall.y = y
    return wall


def _place(category, type, x, y):
    # Legend-token dispatch for the simple, argument-free categories only -
    # anything needing extra fields (key/barrier/switch/sign/npc/an exit
    # with a destination or requires) is declared through 'objects' instead, never a bare
    # legend token.
    at = world(x, y)
    if category == 'platform':
        return add_platform(at=at, type=type)
    if category == 'hazard':
        return add_hazard(at=at, type=type)
    if category == 'collectible':
        return add_collectible(at=at, type=type)
    if category == 'decor':
        return add_decor(at=at, type=type)
    if category == 'climbable':
        return add_climbable(at=at, type=type)
    if category == 'enemy':
        return add_enemy(at=at, type=type)
    if category == 'exit':
        return add_exit(at=at, type=type)
    raise ValueError(
        f"Unknown placement category {category!r} - expected one of "
        "'platform', 'hazard', 'collectible', 'decor', 'climbable', 'enemy', 'exit'."
    )


# Every declarative category's allowed keys - kept in lockstep with the
# factory it dispatches to, so a field the factory accepts can't silently
# vanish here, and a typo'd/unsupported field is caught instead of being
# dropped on the floor. The category-to-factory mapping is literal, per the
# implementation spec: platform, wall, collectible, decor, climbable, key, barrier,
# switch, hazard, enemy, npc, sign, exit.
OBJECT_SPEC_KEYS = {
    'platform': {'category', 'at', 'type', 'launch_speed'},
    'wall': {'category', 'at', 'type'},
    'collectible': {'category', 'at', 'type', 'sets_global', 'id', 'remember_as'},
    'decor': {'category', 'at', 'type', 'id'},
    'climbable': {'category', 'at', 'type', 'id'},
    'key': {'category', 'at', 'type', 'sets_global', 'id', 'remember_as'},
    'barrier': {'category', 'at', 'type', 'requires', 'id', 'remember_as'},
    'switch': {'category', 'at', 'type', 'sets_global', 'id', 'remember_as', 'reusable', 'activation'},
    'hazard': {'category', 'at', 'type', 'id'},
    'enemy': {'category', 'at', 'type', 'id', 'patrol_range', 'facing', 'anchor', 'shoot_interval'},
    'npc': {'category', 'at', 'type', 'lines', 'id', 'anchor'},
    'sign': {'category', 'at', 'type', 'lines', 'id'},
    'exit': {'category', 'at', 'type', 'destination', 'activation', 'requires', 'success_text', 'fail_text', 'id'},
}
# 'layer' is data-only rendering provenance (which source layer a
# converter-generated placement came from), never a factory gameplay
# argument - allowed on every category alongside its own keys, per the
# implementation spec's converter-ownership rules.
# 'appears_when' / 'disappears_when' name declared boolean global(s): the
# placement exists only while they are all true / not all true (see
# _update_appearing). Every category takes them.
PRESENCE_KEYS = ('appears_when', 'disappears_when')
for _keys in OBJECT_SPEC_KEYS.values():
    _keys.add('layer')
    _keys.update(PRESENCE_KEYS)

OBJECT_SPEC_REQUIRED = {
    'platform': ('at', 'type'), 'wall': ('at', 'type'),
    'collectible': ('at', 'type'), 'decor': ('at', 'type'), 'climbable': ('at', 'type'),
    'key': ('at', 'type', 'sets_global'), 'barrier': ('at', 'type', 'requires'),
    'switch': ('at', 'type', 'sets_global'), 'hazard': ('at', 'type'),
    'enemy': ('at', 'type'), 'npc': ('at', 'type', 'lines'),
    'sign': ('at', 'type', 'lines'), 'exit': ('at', 'type'),
}


def _validate_object_spec_shape(spec):
    # Schema-level preflight only (category/keys/required fields) - run over
    # every declaration before any of them is constructed, so a malformed
    # last declaration can't leave earlier ones half-built.
    if not isinstance(spec, dict) or 'category' not in spec:
        raise ValueError("Map option 'objects' needs dictionaries with a category.")
    category = spec['category']
    allowed = OBJECT_SPEC_KEYS.get(category)
    if allowed is None:
        raise ValueError(f"Unknown map object category {category!r}.")
    unsupported = spec.keys() - allowed
    if unsupported:
        raise ValueError(
            f"Map object of category {category!r} has unsupported field(s) "
            f"{sorted(unsupported)!r}."
        )
    for key in OBJECT_SPEC_REQUIRED[category]:
        if key not in spec:
            raise ValueError(f"Map object of category {category!r} needs {key!r}.")


def _resolve_object_layer(layer, layer_names, layer_count):
    # 'layer' names rendering provenance, not identity - a string is
    # resolved against the room's current layer_names (robust to layer
    # reordering across reconversions); an int indexes the current layers
    # list directly.
    if isinstance(layer, str):
        if not layer_names or layer not in layer_names:
            raise ValueError(f"Map object references unknown layer {layer!r}.")
        return layer_names.index(layer)
    if isinstance(layer, int) and not isinstance(layer, bool):
        if layer < 0 or layer >= layer_count:
            raise ValueError(f"Map object layer index {layer} is out of range for {layer_count} layer(s).")
        return layer
    raise ValueError("Map object 'layer' must be a layer name (str) or index (int).")


def _dispatch_object(spec):
    category = spec['category']
    at = spec['at']
    type_ = spec['type']
    if category == 'platform':
        return add_platform(at=at, type=type_, launch_speed=spec.get('launch_speed'))
    if category == 'wall':
        return add_wall(at=at, type=type_)
    if category == 'collectible':
        return add_collectible(at=at, type=type_, sets_global=spec.get('sets_global'),
                                id=spec.get('id'), remember_as=spec.get('remember_as'))
    if category == 'decor':
        return add_decor(at=at, type=type_, id=spec.get('id'))
    if category == 'climbable':
        return add_climbable(at=at, type=type_, id=spec.get('id'))
    if category == 'key':
        return add_key(at=at, type=type_, sets_global=spec['sets_global'],
                        id=spec.get('id'), remember_as=spec.get('remember_as'))
    if category == 'barrier':
        return add_barrier(at=at, type=type_, requires=spec['requires'],
                            id=spec.get('id'), remember_as=spec.get('remember_as'))
    if category == 'switch':
        return add_switch(at=at, type=type_, sets_global=spec['sets_global'],
                           id=spec.get('id'), remember_as=spec.get('remember_as'),
                           reusable=spec.get('reusable', False), activation=spec.get('activation', 'touch'))
    if category == 'hazard':
        return add_hazard(at=at, type=type_, id=spec.get('id'))
    if category == 'enemy':
        return add_enemy(at=at, type=type_, id=spec.get('id'),
                          patrol_range=spec.get('patrol_range'), facing=spec.get('facing', 1),
                          anchor=spec.get('anchor', 'center'), shoot_interval=spec.get('shoot_interval'))
    if category == 'npc':
        return add_npc(at=at, type=type_, lines=spec['lines'],
                        id=spec.get('id'), anchor=spec.get('anchor', 'center'))
    if category == 'sign':
        return add_sign(at=at, type=type_, lines=spec['lines'], id=spec.get('id'))
    return add_exit(at=at, type=type_, destination=spec.get('destination'),
                    activation=spec.get('activation', 'touch'), requires=spec.get('requires'),
                    fail_text=spec.get('fail_text'), success_text=spec.get('success_text'),
                    id=spec.get('id'))


def _apply_object_layer(obj, spec, layer):
    if 'layer' not in spec:
        return
    layer_idx = _resolve_object_layer(spec['layer'], layer['names'], layer['count'])
    obj.alpha = layer['alpha'](layer_idx)
    _apply_map_layer_z(obj, layer_idx, layer['names'], layer['preserve_z_order'], layer['count'])


def _create_appearing(entry):
    # build_tilemap reserved the placement's names for the whole visit; this
    # entry owns them, so it releases them before building the placement again.
    spec = entry['spec']
    for store, key in ((game.reservedIds, 'id'), (game.reservedRememberAs, 'remember_as')):
        if spec.get(key) is not None:
            store.discard(spec[key])
    obj = _dispatch_object(spec)
    if obj is None:
        # Already resolved (a remembered pickup or opened barrier).
        entry['done'] = True
        return
    _apply_object_layer(obj, spec, entry['layer'])
    entry['obj'] = obj


def _present(entry):
    appears, disappears = entry['appears_when'], entry['disappears_when']
    if appears is not None and not _requires_met(appears):
        return False
    return disappears is None or not _requires_met(disappears)


def _update_appearing():
    # A placement with appears_when exists while its globals are all true; one
    # with disappears_when is removed while its globals are all true. Removal
    # destroys it and it is built fresh when it returns. One that was
    # collected, defeated or opened stays gone for the rest of the visit.
    for entry in game.appearing:
        if entry['done']:
            continue
        obj = entry['obj']
        if obj is not None and obj._destroyed:
            entry['done'] = True
            continue
        met = _present(entry)
        if met and obj is None:
            _create_appearing(entry)
        elif not met and obj is not None:
            entry['obj'] = None
            destroy_object(obj)


def _resolve_room_locations(locations, rows, cols, origin_x, origin_y, has_grid):
    # World positions are already final coordinates and are never shifted by
    # grid origin. A cell() location needs grid metadata to resolve; a
    # world-authored room (no grid) can only declare world() locations.
    resolved = {}
    for name, pos in locations.items():
        if pos['_posKind'] == 'world':
            resolved[name] = (pos['x'], pos['y'])
            continue
        if not has_grid:
            raise ValueError(f"Map location {name!r} uses cell(...), but this room has no grid (layers=[]).")
        row, col = pos['row'], pos['col']
        if row >= rows or col >= cols:
            raise ValueError(f"Map location {name!r} needs a whole cell inside this map.")
        x, y = _cell_center(row, col, rows)
        resolved[name] = (x - origin_x, y - origin_y)
    return resolved


def _apply_map_layer_z(obj, layer_idx, layer_names, preserve_z_order, layer_count):
    if not preserve_z_order:
        return
    layer_bump = (layer_count - layer_idx) / (layer_count + 1)
    if layer_names and layer_names[layer_idx].strip().lower() == 'background':
        # Background-start.py uses z=-10. Keep named background art above that
        # full-screen sprite, but below platforms and other world objects.
        obj.z = -10 + layer_bump
        return
    obj.z += layer_bump


def _build_terrain(terrain_cells, rows, origin_x, origin_y, layer_alpha, layer_names, preserve_z_order, layer_count):
    game.suppressGroundTracking = True
    tile_size = None
    for (row, col), type_name, layer_idx in terrain_cells:
        x, y = _cell_center(row, col, rows)
        x -= origin_x
        y -= origin_y
        obj = _place('platform', type_name, x, y)
        assert obj is not None
        obj.alpha = layer_alpha(layer_idx)
        _apply_map_layer_z(obj, layer_idx, layer_names, preserve_z_order, layer_count)
        measured = (get_width(obj), get_height(obj))
        if tile_size is None:
            tile_size = measured
        elif measured != tile_size:
            raise ValueError(
                f"All terrain tiles in one map must be the same size - "
                f"found {tile_size} and {measured} (type {type_name!r})."
            )
        if measured[0] != CELL or measured[1] != CELL:
            raise ValueError(
                f"Terrain tile {type_name!r} measures {measured}, expected "
                f"{CELL}x{CELL} - check CELL and the tile art."
            )
    game.suppressGroundTracking = False
    _track_ground_extent(-origin_y - CELL / 2)


def _build_entities(entity_cells, rows, origin_x, origin_y, layer_alpha, layer_names, preserve_z_order, layer_count):
    for (row, col), category, type_name, layer_idx in entity_cells:
        x, y = _cell_center(row, col, rows)
        x -= origin_x
        y -= origin_y
        obj = _place(category, type_name, x, y)
        # A legend-dispatched collectible never passes remember_as, so it
        # can never come back as an absent (None) pickup - unlike an
        # authored 'objects'/direct-call collectible, which can.
        assert obj is not None
        obj.alpha = layer_alpha(layer_idx)
        _apply_map_layer_z(obj, layer_idx, layer_names, preserve_z_order, layer_count)


def _layer_alpha_fn(layer_names, layer_opacity, layer_count):
    if layer_names and len(layer_names) != layer_count:
        raise ValueError("Map option 'layer_names' must name every layer, in order.")

    def layer_alpha(index):
        name = layer_names[index] if layer_names else index
        alpha = layer_opacity.get(name, 1)
        if not isinstance(alpha, (int, float)) or alpha < 0 or alpha > 1:
            raise ValueError(f"Layer opacity for {name!r} must be a number from 0 to 1.")
        return alpha
    return layer_alpha


def _apply_camera_and_boundary(camera, boundary, left, right, bottom, top):
    # 'camera' controls only the view: whether it's clamped to the extent or
    # free to scroll anywhere. 'boundary' controls only physical edges:
    # whether invisible walls stop the player at the extent's left/right
    # edges. The two are independent.
    game.cameraBounds = (left, right, bottom, top) if camera != 'free' else None
    if boundary:
        # No top/bottom walls: the bottom is the kill plane on purpose.
        mid_y = (bottom + top) / 2
        thickness = CELL
        height = max((top - bottom) + 2 * CELL, ENGINE_DEFAULTS['viewport']['height'] * 4)
        _add_boundary_wall(left - thickness / 2, mid_y, thickness, height)
        _add_boundary_wall(right + thickness / 2, mid_y, thickness, height)


def build_tilemap():
    # Builds the current room (MAPS[game.room]) exactly once per visit -
    # calling it twice raises without duplication. Returns None -
    # of_type()/get_object() read what this built off `game`.
    global CELL
    if getattr(game, 'tilemapBuilt', False):
        raise ValueError('build_tilemap() was already called this visit - it only runs once per room entry.')
    if game.room not in MAPS:
        raise ValueError(
            f"No map registered for room {game.room!r} in MAPS - add MAPS[{game.room!r}] = ... in maps.py."
        )
    normalized = _normalize_room(MAPS[game.room])
    has_grid = normalized['has_grid']
    map_tile_size = normalized['tile_size'] if normalized['tile_size'] is not None else ENGINE_DEFAULTS['tilemap']['defaultCell']
    CELL = map_tile_size

    # 0, not None, when there's no grid - only ever read inside a
    # `has_grid` branch below, but keeping them plain ints (rather than
    # Optional) avoids static-checker noise at every arithmetic use.
    rows = cols = 0
    terrain_cells = entity_cells = []
    origin_x, origin_y = 0, 0
    if has_grid:
        rows, cols, terrain_cells, entity_cells = _parse_layers(normalized['layers'], normalized['legend'])
        game.mapRows = rows
        game.mapCols = cols
        origin = normalized['origin']
        if origin is not None:
            row, col = origin['row'], origin['col']
            if row >= rows or col >= cols:
                raise ValueError("Map option 'origin' must be a whole cell inside the grid.")
            origin_x, origin_y = _cell_center(row, col, rows)
    game.originX = origin_x
    game.originY = origin_y

    game.locations = _resolve_room_locations(normalized['locations'], rows, cols, origin_x, origin_y, has_grid)

    layer_count = len(normalized['layers']) if has_grid else 0
    layer_alpha = _layer_alpha_fn(normalized['layer_names'], normalized['layer_opacity'], layer_count)

    if has_grid:
        _build_terrain(terrain_cells, rows, origin_x, origin_y, layer_alpha, normalized['layer_names'], normalized['preserve_z_order'], layer_count)
        _build_entities(entity_cells, rows, origin_x, origin_y, layer_alpha, normalized['layer_names'], normalized['preserve_z_order'], layer_count)

    # Preflight every declarative object before constructing any of them, so
    # a malformed last declaration can't leave earlier declarations alive.
    object_specs = normalized['objects']
    for spec in object_specs:
        _validate_object_spec_shape(spec)
        if 'layer' in spec:
            _resolve_object_layer(spec['layer'], normalized['layer_names'], layer_count)
        for key in PRESENCE_KEYS:
            if key in spec:
                if spec[key] is None:
                    raise ValueError(f"Map object {key!r} needs a global name or a list of names.")
                _validate_requires(spec[key], f"Map object {key!r}")
    layer = {'names': normalized['layer_names'], 'count': layer_count, 'alpha': layer_alpha,
             'preserve_z_order': normalized['preserve_z_order']}
    game.appearing = []
    for spec in object_specs:
        if any(key in spec for key in PRESENCE_KEYS):
            _reserve_id(spec.get('id'))
            _reserve_remember_as(spec.get('remember_as'))
            game.appearing.append({
                'spec': {key: value for key, value in spec.items() if key not in PRESENCE_KEYS},
                'appears_when': spec.get('appears_when'), 'disappears_when': spec.get('disappears_when'),
                'layer': layer, 'obj': None, 'done': False,
            })
            continue
        obj = _dispatch_object(spec)
        if obj is not None:
            _apply_object_layer(obj, spec, layer)
    _update_appearing()

    fall_margin = normalized['fall_margin']
    game.fallMarginOverride = fall_margin * CELL if fall_margin is not None else None
    game.mapBackground = normalized['background']

    if has_grid:
        left = -origin_x - CELL / 2
        right = (cols - 1) * CELL - origin_x + CELL / 2
        bottom = -origin_y - CELL / 2
        top = (rows - 1) * CELL - origin_y + CELL / 2
    elif normalized['bounds'] is not None:
        b = normalized['bounds']
        left, right, bottom, top = b['left'], b['right'], b['bottom'], b['top']
    else:
        left = right = bottom = top = None

    if left is not None:
        _apply_camera_and_boundary(normalized['camera'], normalized['boundary'], left, right, bottom, top)
        if not has_grid:
            # Grid rooms already tracked their own extent bottom in
            # _build_terrain; a world room's explicit bounds establishes the
            # same baseline here - later add_platform/add_wall calls in the
            # room-start script can still lower it further.
            _track_ground_extent(bottom)
    else:
        game.cameraBounds = None

    game.tilemapBuilt = True
    return None