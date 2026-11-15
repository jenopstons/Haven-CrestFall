# Grid/legend/room-lifecycle machinery. Genre-neutral: this parses a level's
# layers/legend/locations (see maps.py, project-owned, for LEGEND/MAPS and
# the actual grids) and owns the room-visit lifecycle (enter/travel/events).
# build_tilemap itself (which dispatches legend/object-spec entries to real
# game object factories, including add_exit) is genre-specific and lives in
# the active pack instead (packs/platformer/python/functions/grid.py).

_ROOM_FIELDS = {
    'layers', 'legend', 'tile_size', 'locations', 'background', 'objects',
    'origin', 'bounds', 'camera', 'boundary', 'fall_margin',
    'layer_names', 'layer_opacity', 'preserve_z_order',
}

def _is_script_room(name):
    return name in globals().get('SCRIPT_ROOMS', [])

def _require_room(name):
    maps = globals().get('MAPS')
    if not isinstance(maps, dict) or name not in maps:
        raise ValueError(
            f"Cannot enter room {name!r} - no map registered for it in MAPS."
        )
    return maps[name]

def _require_destination(from_room, room, location):
    if _is_script_room(room):
        if location is not None:
            raise ValueError(f"Room {from_room!r} goes to script room {room!r}, which has no locations - leave the location out.")
        return
    if room not in MAPS:
        raise ValueError(f"Room {from_room!r} has an exit to unknown room {room!r}.")
    _require_valid_location(from_room, room, location)

def _global_legend():
    legend = globals().get('LEGEND')
    if legend is None:
        raise ValueError(
            "This map has no 'legend' and no global LEGEND is defined - "
            "every map needs a resolvable legend."
        )
    return legend

def _with_layout(layout, overlay):
    # Combines a converter-owned layout dict (legend/layers/tile_size/...,
    # regenerated whenever a map directory's source is reconverted) with an
    # authored overlay dict (objects/locations, plus any hand-added
    # 'locations' like a travel anchor). No Python dict-unpacking syntax
    # (Skulpt can't run `**dict` in a literal), so this is an ordinary
    # function. 'locations' is merged (union) since both the layout
    # (converter-generated names) and the overlay (hand-added names) can
    # contribute entries; 'objects' concatenates - generated layout objects
    # first, authored overlay objects after, per the converter-ownership
    # contract (generated pickups vs. authored ones). Every other key is a
    # plain overlay-wins override, since layout and overlay never otherwise
    # share a key.
    merged = dict(layout)
    merged.update(overlay)
    if 'locations' in layout or 'locations' in overlay:
        locations = dict(layout.get('locations', {}))
        locations.update(overlay.get('locations', {}))
        merged['locations'] = locations
    if 'objects' in layout or 'objects' in overlay:
        merged['objects'] = list(layout.get('objects', [])) + list(overlay.get('objects', []))
    return merged

def _finite_number(value):
    return not isinstance(value, bool) and isinstance(value, (int, float)) and value == value and value not in (float('inf'), float('-inf'))

def _normalize_room(level_data):
    # Full validation of one room's metadata dict against the canonical
    # shape - see the implementation spec's room-metadata field table. No
    # bare row-list/nested-layer-list shorthand, no entries/default_entry/
    # spawn/point-legend-marker fields: those are removed, not silently
    # ignored.
    if not isinstance(level_data, dict):
        raise ValueError("Map entries must be dictionaries - see the room-metadata contract.")
    unknown = level_data.keys() - _ROOM_FIELDS
    if unknown:
        raise ValueError(f"Map has unsupported field(s) {sorted(unknown)!r}.")
    if 'layers' not in level_data:
        raise ValueError("Map option 'layers' is required - [] means a world-authored room with no grid.")
    layers = level_data['layers']
    if not isinstance(layers, list):
        raise ValueError("Map option 'layers' must be a list of layers (each a list of row strings), or [].")
    has_grid = len(layers) > 0

    legend = None
    if has_grid:
        legend = level_data['legend'] if 'legend' in level_data else _global_legend()
    elif 'legend' in level_data:
        legend = level_data['legend']

    locations = level_data.get('locations', {})
    if not isinstance(locations, dict):
        raise ValueError("Map option 'locations' must be a dict of name to cell()/world().")
    for name, pos in locations.items():
        if not isinstance(name, str) or name == '':
            raise ValueError("Map 'locations' names must be non-empty strings.")
        if not _is_position(pos):
            raise ValueError(f"Map location {name!r} must be cell(row, col) or world(x, y).")

    background = level_data.get('background')
    if background is None:
        raise ValueError("Map option 'background' is required.")

    objects = level_data.get('objects', [])
    if not isinstance(objects, list):
        raise ValueError("Map option 'objects' must be a list.")

    origin = level_data.get('origin')
    if origin is not None:
        if not has_grid:
            raise ValueError("Map option 'origin' needs a nonempty grid.")
        if not _is_position(origin) or origin['_posKind'] != 'cell':
            raise ValueError("Map option 'origin' must be a cell(row, col) descriptor within the grid.")

    bounds = level_data.get('bounds')
    if bounds is not None:
        if has_grid:
            raise ValueError("Map option 'bounds' is only for layers=[] (world-authored) rooms.")
        if not isinstance(bounds, dict) or set(bounds.keys()) != {'left', 'right', 'bottom', 'top'}:
            raise ValueError("Map option 'bounds' needs exactly 'left', 'right', 'bottom', 'top'.")
        left, right, bottom, top = bounds['left'], bounds['right'], bounds['bottom'], bounds['top']
        if not all(_finite_number(v) for v in (left, right, bottom, top)):
            raise ValueError("Map option 'bounds' values must be finite numbers.")
        if left >= right or bottom >= top:
            raise ValueError("Map option 'bounds' must have left < right and bottom < top.")

    has_extent = has_grid or bounds is not None
    camera = level_data.get('camera', 'bounded' if has_extent else 'free')
    if camera not in ('bounded', 'free'):
        raise ValueError("Map option 'camera' must be 'bounded' or 'free'.")
    if camera == 'bounded' and not has_extent:
        raise ValueError("Map option 'camera'='bounded' needs a grid or explicit 'bounds'.")

    boundary = level_data.get('boundary', has_extent)
    if not isinstance(boundary, bool):
        raise ValueError("Map option 'boundary' must be a bool.")
    if boundary and not has_extent:
        raise ValueError("Map option 'boundary'=True needs a grid or explicit 'bounds'.")

    fall_margin = level_data.get('fall_margin')
    if fall_margin is not None and (isinstance(fall_margin, bool) or not _finite_number(fall_margin) or fall_margin < 0):
        raise ValueError("Map option 'fall_margin' must be a finite nonnegative number.")

    preserve_z_order = level_data.get('preserve_z_order', False)
    layer_names = level_data.get('layer_names', [])
    layer_opacity = level_data.get('layer_opacity', {})
    tile_size = level_data.get('tile_size')
    if tile_size is not None and (isinstance(tile_size, bool) or not _finite_number(tile_size) or tile_size <= 0):
        raise ValueError("Map option 'tile_size' must be a positive number.")

    return {
        'layers': layers, 'legend': legend, 'tile_size': tile_size,
        'locations': locations, 'background': background, 'objects': objects,
        'origin': origin, 'bounds': bounds, 'camera': camera, 'boundary': boundary,
        'fall_margin': fall_margin, 'layer_names': layer_names,
        'layer_opacity': layer_opacity, 'preserve_z_order': preserve_z_order,
        'has_grid': has_grid,
    }

def _parse_layers(layers, legend):
    # Validates every layer, then sorts each cell into terrain or entities.
    if not isinstance(layers[0], list) or not layers[0]:
        raise ValueError("A tilemap needs at least one non-empty row.")
    if any(not isinstance(row, str) for row in layers[0]):
        raise ValueError("Tilemap rows must be strings.")
    rows = len(layers[0])
    cols = len(layers[0][0])
    if cols == 0:
        raise ValueError("Tilemap rows must not be empty.")
    for layer in layers:
        if not isinstance(layer, list) or any(not isinstance(row, str) for row in layer):
            raise ValueError("Tilemap layers must contain string rows.")
        if len(layer) != rows or any(len(row) != cols for row in layer):
            raise ValueError("All layers within one map must have identical dimensions.")

    terrain_cells = []
    entity_cells = []
    for layer_idx, layer in enumerate(layers):
        for row_idx, row_str in enumerate(layer):
            for col_idx, token in enumerate(row_str):
                if token is None or token == '.':
                    continue
                if token not in legend:
                    raise ValueError(f"Unknown legend token {token!r} at row {row_idx}, col {col_idx}.")
                entry = legend[token]
                if entry is None:
                    continue
                category, type_name = entry
                cell_pos = (row_idx, col_idx)
                if category == 'platform':
                    terrain_cells.append((cell_pos, type_name, layer_idx))
                else:
                    entity_cells.append((cell_pos, category, type_name, layer_idx))
    return rows, cols, terrain_cells, entity_cells

def _cell_center(row, col, rows):
    # Row 0 is the top. A cell's centre is its world position, matching
    # every placement factory's own convention.
    return (col * CELL, (rows - 1 - row) * CELL)

def xy(row, col):
    # Converts a top-down map row/column into this room's world-space (x, y)
    # centre, right now - unlike cell(), which builds an inert reference
    # resolved later. Requires grid metadata (a nonempty grid built by
    # build_tilemap()); an advanced conversion, not a second placement form.
    rows = getattr(game, 'mapRows', None)
    cols = getattr(game, 'mapCols', None)
    if rows is None or cols is None:
        raise ValueError('xy() needs build_tilemap() to have run for a room with a nonempty grid.')
    if not isinstance(row, int) or not isinstance(col, int) or row < 0 or row >= rows or col < 0 or col >= cols:
        raise ValueError('xy(row, col) needs a whole cell inside this map.')
    x, y = _cell_center(row, col, rows)
    return (x - getattr(game, 'originX', 0), y - getattr(game, 'originY', 0))

def _room_locations(room):
    # A room's declared 'locations' names, without building it - used to
    # validate a travel/start destination before it's ever reached.
    normalized = _normalize_room(_require_room(room))
    return set(normalized['locations'].keys())

def _require_valid_location(from_room, to_room, location):
    if not isinstance(location, str) or location == '':
        raise ValueError(f"Room {from_room!r} needs a location name string, not {location!r}.")
    if location not in _room_locations(to_room):
        raise ValueError(
            f"Room {from_room!r} travels to {to_room!r} location {location!r}, "
            "not declared in that room's 'locations'."
        )

def _exit_destination(destination):
    # An exit's destination: None ends the game, a room name is a script
    # room, and (room, location) is a map room.
    if destination is None:
        return None, None
    if isinstance(destination, str):
        return destination, None
    if isinstance(destination, (tuple, list)) and len(destination) == 2:
        return destination[0], destination[1]
    raise ValueError("An exit's destination must be None, a script room name, or (room, location).")

def _validate_static_exit_destinations():
    # Every statically-declared ('objects' list) exit destination is
    # checked before any room runs, so a typo'd destination fails at boot.
    # A destination built at runtime is checked by add_exit itself.
    for room, level_data in MAPS.items():
        normalized = _normalize_room(level_data)
        for spec in normalized['objects']:
            if not isinstance(spec, dict) or spec.get('category') != 'exit':
                continue
            to_room, to_location = _exit_destination(spec.get('destination'))
            if to_room is not None:
                _require_destination(room, to_room, to_location)

def _validate_start(room, location):
    if not room:
        raise ValueError("Manifest needs a non-empty startRoom.")
    if _is_script_room(room):
        return
    if not location:
        raise ValueError("Manifest needs a non-empty startLocation.")
    if room not in MAPS:
        raise ValueError(f"Start room {room!r} is not registered in MAPS.")
    _require_valid_location('(start)', room, location)

def _validate_title(room):
    if not _is_script_room(room):
        raise ValueError(f"Title room {room!r} must be a script room.")

def _fresh_listeners():
    return {'collect': [], 'gameFinished': [], 'enemyDefeated': [], 'playerHit': []}

def _stop_room_music():
    current_music = getattr(game, '_studio_room_music', None)
    if current_music is not None:
        _cancel_sound_fades(current_music)
        stop_sound(current_music)
    game._studio_room_music = None
    game._studio_room_music_volume = 0

def _resume_room_music():
    current_music = getattr(game, '_studio_room_music', None)
    if current_music is None:
        return
    _cancel_sound_fades(current_music)
    set_volume(current_music, getattr(game, '_studio_room_music_volume', 0))

def _start_room_music(name, preserve_current=False):
    if preserve_current:
        _resume_room_music()
        return
    _stop_room_music()
    music = globals().get('ROOM_MUSIC', {}).get(name)
    if music is None:
        return
    game._studio_room_music = sound(music['file'])
    set_volume(game._studio_room_music, 0)
    loop_sound(game._studio_room_music)
    fade_sound(game._studio_room_music, 0, music['volume'], 30)
    game._studio_room_music_volume = music['volume']

def _enter_room(name, location, preserve_music=False):
    # The only caller of set_room() - every room change routes through here
    # so room-entry state resets exactly once before that room's start() runs.
    _require_destination('(travel)', name, location)
    game.room = name
    game.arrivalLocation = location
    game.visitToken = getattr(game, 'visitToken', 0) + 1
    game.byCategoryType = {}
    game.instances = {}
    game.reservedIds = set()
    game.reservedRememberAs = set()
    game.appearing = []
    game.locations = {}
    game.listeners = _fresh_listeners()
    game.interactSeq = 0
    game.interactFrame = None
    game.interactTarget = None
    game.mapSpawn = None
    game.dialogBox = None
    game.dialogOwner = None
    game.mapBottom = None
    game.fallMarginOverride = None
    game.cameraBounds = None
    game.tilemapBuilt = False
    game.playerSpawnedThisVisit = False
    game.hitStop = 0
    game.pendingTransition = False
    game.pendingFade = None
    game.finished = False
    game.player = None
    game.mapRows = None
    game.mapCols = None
    game.originX = 0
    game.originY = 0
    # Reset so a room that never calls build_tilemap doesn't inherit a
    # stale tile size from whichever room ran before it.
    global CELL
    CELL = ENGINE_DEFAULTS['tilemap']['defaultCell']
    viewport = ENGINE_DEFAULTS['viewport']
    set_camera_size(viewport['width'], viewport['height'])
    if _is_script_room(name):
        set_camera(0, 0)
    _start_room_music(name, preserve_current=preserve_music)
    set_room(name)

def arrival_location():
    # The named destination for the entire visit - not cleared by
    # spawn_player(); an explicit spawn_player(at=...) changes actual
    # position, not this name.
    return getattr(game, 'arrivalLocation', None)

def go_to_room(room, location=None):
    # Freezes the player and fades to black. A map room needs a location; a
    # script room takes none. Both names must resolve before a fade is
    # created; a second valid request while a fade is pending is ignored.
    _require_destination(game.room, room, location)
    if getattr(game, 'pendingTransition', False):
        return
    current_music = getattr(game, '_studio_room_music', None)
    if current_music is not None:
        _cancel_sound_fades(current_music)
        fade_sound(current_music, getattr(game, '_studio_room_music_volume', 0), 0, 30)
    game.pendingTransition = True
    if game.player is not None:
        game.player.frozen = True
    fade = FadeOut()
    fade.nextRoom = room
    fade.nextLocation = location
    game.pendingFade = fade

def start_game():
    # Goes to the game's start room and point, as go_to_room does: what a title screen calls to begin.
    go_to_room(game.startRoom, game.startLocation)

def on_collect(callback):
    return _on_event('collect', callback)

def on_game_finished(callback):
    return _on_event('gameFinished', callback)

def on_enemy_defeated(callback):
    return _on_event('enemyDefeated', callback)

def on_player_hit(callback):
    return _on_event('playerHit', callback)

def _on_event(name, callback):
    if not callable(callback):
        raise ValueError(f"on_{name} needs a callable.")
    listeners = game.listeners[name]
    for existing in listeners:
        if existing is callback:
            def _unsub_existing():
                if callback in listeners:
                    listeners.remove(callback)
            return _unsub_existing
    listeners.append(callback)
    def _unsub():
        if callback in listeners:
            listeners.remove(callback)
    return _unsub

def _dispatch(name, *args):
    # Dispatches a snapshot in registration order; adding/removing listeners
    # during dispatch affects only the next event. A room transition, death,
    # or an exception aborts the remaining snapshot immediately.
    token = game.visitToken
    for cb in list(game.listeners[name]):
        cb(*args)
        if game.visitToken != token or getattr(game, 'pendingTransition', False):
            return