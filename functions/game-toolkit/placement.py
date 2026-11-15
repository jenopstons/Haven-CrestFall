# Generic argument/type resolution shared by every placement factory,
# regardless of game genre.

def cell(row, col):
    # An inert grid-cell reference - only meaningful once resolved (via
    # at=) against the room build_tilemap() most recently ran for. Does
    # not depend on CELL or an active room itself, so it's safe to build
    # in maps.py at module-eval time, before any room has been entered.
    if not isinstance(row, int) or isinstance(row, bool) or row < 0:
        raise ValueError('cell(row, col) needs nonnegative whole numbers.')
    if not isinstance(col, int) or isinstance(col, bool) or col < 0:
        raise ValueError('cell(row, col) needs nonnegative whole numbers.')
    return {'_posKind': 'cell', 'row': row, 'col': col}

def world(x, y):
    # An inert world-space reference - the world-space counterpart to
    # cell(), resolved the same way via at=.
    for value in (x, y):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value != value or value in (float('inf'), float('-inf')):
            raise ValueError('world(x, y) needs finite numbers.')
    return {'_posKind': 'world', 'x': x, 'y': y}

def _is_position(value):
    return isinstance(value, dict) and value.get('_posKind') in ('cell', 'world')

def _resolve_at(at):
    # Resolves an at= argument to a world (x, y) pair: cell()/world(),
    # or a named location string from this room's 'locations'. Raises on
    # anything else, including a raw (x, y) tuple - at= is never
    # ambiguous about whether it's a cell or a world position.
    if isinstance(at, str):
        locations = getattr(game, 'locations', {})
        if at not in locations:
            raise ValueError(
                f"No location named {at!r} on this map - check 'locations' in "
                "maps.py, and make sure build_tilemap() ran first."
            )
        return locations[at]
    if not _is_position(at):
        raise ValueError(
            "at= needs cell(row, col), world(x, y), or a location name string."
        )
    if at['_posKind'] == 'world':
        return (at['x'], at['y'])
    return xy(at['row'], at['col'])

# --- id / remember_as: two independent names -------------------------------
#
# `id` names a live placement for scripts (get_object/find_object); it has no
# persistence effect. `remember_as` names a placement's resolved gameplay
# state across visits within one play run. Both are reserved for the whole
# room visit the instant they're supplied, even if the placement turns out to
# be absent (already resolved on an earlier visit) or is destroyed later -
# recreating one in the same visit needs a different name or no name.

def _reserve_name(store, name, what):
    if not isinstance(name, str) or name == '':
        raise ValueError(f"{what} must be a non-empty string.")
    if name in store:
        raise ValueError(
            f"Duplicate {what} {name!r} - names must be unique within a room for "
            "the whole visit, even if the earlier placement is absent or destroyed."
        )
    store.add(name)

def _reserve_id(id):
    if id is not None:
        _reserve_name(game.reservedIds, id, 'id')

def _reserve_remember_as(remember_as):
    if remember_as is not None:
        _reserve_name(game.reservedRememberAs, remember_as, 'remember_as')

def _register_instance(category, type, obj, id=None):
    # Indexes a live logical instance by (category, type) for of_type(), and
    # by id for get_object()/find_object() when the caller gave one. id
    # uniqueness itself was already enforced by _reserve_id before
    # construction - this just wires up the live lookup. Every registered
    # instance is stamped with the current visit token, so a handle kept
    # across a room change/death is recognizably stale (see
    # _require_live_handle) instead of silently mutating the new room.
    game.byCategoryType.setdefault((category, type), []).append(obj)
    obj._visitToken = game.visitToken
    if id is not None:
        game.instances[id] = obj
        obj.instanceId = id
    return obj

def _validate_global(name, what):
    # GLOBALS is project-authored (see the config block assembleGame emits) -
    # every sets_global/requires/appears_when/disappears_when name must be declared there (with
    # a type - see _global_type), so a typo fails loudly instead of
    # silently reading/writing a fresh default.
    declared = globals().get('GLOBALS')
    if declared is None:
        raise ValueError(
            "No GLOBALS declared for this project - declare every checkpointed "
            "global name and type it uses, e.g. "
            "GLOBALS = {'has_key': {'type': 'bool', 'default': False}}."
        )
    if name not in declared:
        raise ValueError(f"{what} names undeclared global {name!r} - add it to GLOBALS.")

def _global_type(name):
    return globals()['GLOBALS'][name]['type']

def _global_default(name):
    return globals()['GLOBALS'][name]['default']

def set_global(name, value):
    _validate_global(name, 'set_global')
    expected = _global_type(name)
    if expected == 'bool' and not isinstance(value, bool):
        raise ValueError(f"set_global({name!r}, ...) expected a bool, got {type(value).__name__}.")
    if expected == 'int' and (isinstance(value, bool) or not isinstance(value, int)):
        raise ValueError(f"set_global({name!r}, ...) expected an int, got {type(value).__name__}.")
    if expected == 'enum':
        allowed = globals()['GLOBALS'][name]['values']
        if value not in allowed:
            raise ValueError(f"set_global({name!r}, {value!r}) - expected one of {allowed}.")
    game.globals[name] = value

def get_global(name):
    _validate_global(name, 'get_global')
    return game.globals.get(name, _global_default(name))

def _persistent_id(remember_as):
    # Persistence is granted by an authored remember_as= alone, keyed by room
    # + remember_as - never by id, coordinates, art/type, or destroyed state.
    if remember_as is not None:
        return (game.room, remember_as)
    return None

def _is_persisted(name, persistent_id):
    # `name` is which persisted-identity set to check (e.g.
    # 'collectedMapItems', 'openedBarriers') - each kind of one-time effect
    # gets its own set within game.persisted so their identities never
    # collide. Checkpointed/restored wholesale by spawn_player/
    # _respawn_player (player.py) with no per-name code of its own.
    return persistent_id is not None and persistent_id in game.persisted.get(name, set())

def _mark_persisted(name, persistent_id):
    if persistent_id is not None:
        game.persisted.setdefault(name, set()).add(persistent_id)

# --- lookup ------------------------------------------------------------

def get_object(id):
    if not isinstance(id, str) or id == '':
        raise ValueError('get_object(id) needs a non-empty string.')
    obj = getattr(game, 'instances', {}).get(id)
    if obj is None or obj._destroyed:
        raise ValueError(f"No object with id {id!r} - check it was authored/created and still exists.")
    return obj

def find_object(id):
    if not isinstance(id, str) or id == '':
        raise ValueError('find_object(id) needs a non-empty string.')
    obj = getattr(game, 'instances', {}).get(id)
    if obj is None or obj._destroyed:
        return None
    return obj

# Every category of_type()/lookup exposes, and the type catalog each one
# validates its `type` argument against. 'wall' is not a real category - wall
# helpers register as 'platform' (see terrain.py) - so an of_type('wall', ...)
# query raises with that guidance instead of silently returning [].
_CATEGORY_CATALOGS = {
    'platform': 'PLATFORM_TYPES',
    'collectible': 'COLLECTIBLE_TYPES',
    'key': 'COLLECTIBLE_TYPES',
    'barrier': 'BARRIER_TYPES',
    'switch': 'SWITCH_TYPES',
    'hazard': 'HAZARD_TYPES',
    'decor': 'DECOR_TYPES',
    'climbable': 'CLIMBABLE_TYPES',
    'enemy': 'ENEMY_TYPES',
    'npc': 'NPC_TYPES',
    'sign': 'SIGN_TYPES',
    'exit': 'EXIT_TYPES',
}

def of_type(category, type):
    # Every live logical instance of this (category, type), regardless of
    # whether it came from the grid, an 'objects' declaration, or a
    # direct add_*() call - as long as that path registered it. A valid
    # category/type with no live instances returns [], not KeyError.
    if category == 'wall':
        raise ValueError("of_type has no 'wall' category - wall helpers register under 'platform'.")
    catalog_name = _CATEGORY_CATALOGS.get(category)
    if catalog_name is None:
        raise ValueError(f"Unknown of_type category {category!r} - expected one of {sorted(_CATEGORY_CATALOGS.keys())}.")
    catalog = globals().get(catalog_name, {})
    if type not in catalog:
        raise ValueError(f"Unknown type {type!r} for category {category!r} - expected one of {sorted(catalog.keys())}.")
    return [obj for obj in game.byCategoryType.get((category, type), []) if not obj._destroyed]

# --- whole-placement operations -----------------------------------------

def _is_stale(obj):
    return getattr(obj, '_visitToken', None) != game.visitToken

def _require_live_handle(obj, what):
    if obj is None or getattr(obj, '_destroyed', False) or _is_stale(obj):
        raise ValueError(f"{what} needs a live placement handle - this one is None, destroyed, or from a previous room.")

def _reject_player_handle(obj, what):
    if getattr(obj, '_isPlayer', False):
        raise ValueError(f"{what} does not accept the player handle - player position/lifecycle belongs to spawn_player/exits/death.")

def _composite_pieces(obj):
    # Every piece behind one placement - a barrier's extra parts, an
    # enemy's sensor and hitbox, or an exit's trigger sprites
    # (region['triggers'], obj included).
    pieces = list(getattr(obj, 'parts', None) or [])
    region = getattr(obj, 'region', None)
    if region is not None:
        pieces.extend(region['triggers'])
    for name in ('sensor', 'hitbox'):
        piece = getattr(obj, name, None)
        if piece is not None and not isinstance(piece, dict):
            pieces.append(piece)
    return pieces

def hide_object(obj):
    # Hides a placement and every composite piece behind it - collision,
    # requirements and activation are unaffected. Suppresses eligible
    # prompts (an exit's shared indicator lives on its region, not the
    # individual trigger piece, so the suppression flag goes there too).
    _require_live_handle(obj, 'hide_object')
    _reject_player_handle(obj, 'hide_object')
    obj.visible = False
    for piece in _composite_pieces(obj):
        piece.visible = False
    prompt = getattr(obj, 'prompt', None)
    if prompt is not None:
        prompt.visible = False
    region = getattr(obj, 'region', None)
    if region is not None:
        region['promptSuppressed'] = True
    obj.promptSuppressed = True

def show_object(obj):
    _require_live_handle(obj, 'show_object')
    _reject_player_handle(obj, 'show_object')
    obj.visible = True
    for piece in _composite_pieces(obj):
        piece.visible = not getattr(piece, 'collisionProxy', False)
    region = getattr(obj, 'region', None)
    if region is not None:
        region['promptSuppressed'] = False
    obj.promptSuppressed = False

def destroy_object(obj):
    # Destroys a placement and every composite piece behind it - plain
    # destroy() only removes obj itself, leaving the rest alive. Idempotent
    # for None/already-destroyed/stale handles.
    if obj is None or getattr(obj, '_destroyed', False) or _is_stale(obj):
        return
    _reject_player_handle(obj, 'destroy_object')
    for piece in _composite_pieces(obj):
        if piece is not obj and not piece._destroyed:
            destroy(piece)
    prompt = getattr(obj, 'prompt', None)
    if prompt is not None and not prompt._destroyed:
        destroy(prompt)
        obj.prompt = None
    region = getattr(obj, 'region', None)
    if region is not None:
        indicator = region.get('promptIndicator')
        if indicator is not None and not indicator._destroyed:
            destroy(indicator)
            region['promptIndicator'] = None
    destroy(obj)

def set_object_alpha(obj, alpha):
    _require_live_handle(obj, 'set_object_alpha')
    _reject_player_handle(obj, 'set_object_alpha')
    if isinstance(alpha, bool) or not isinstance(alpha, (int, float)) or alpha < 0 or alpha > 1 or alpha != alpha:
        raise ValueError('set_object_alpha needs a finite number from 0 to 1.')
    obj.alpha = alpha
    obj.promptAlpha = alpha
    for piece in _composite_pieces(obj):
        piece.alpha = alpha
    prompt = getattr(obj, 'prompt', None)
    if prompt is not None:
        prompt.alpha = alpha
    region = getattr(obj, 'region', None)
    if region is not None:
        region['promptAlpha'] = alpha

def move_object(obj, *, at):
    # Resolves at= as the new anchor center and translates every owned piece
    # and movement-reference position by the same delta. A teleport of the
    # placement, not per-frame platform motion - existing physics determines
    # subsequent contact.
    _require_live_handle(obj, 'move_object')
    _reject_player_handle(obj, 'move_object')
    new_x, new_y = _resolve_at(at)
    dx = new_x - obj.x
    dy = new_y - obj.y
    _translate_owned(obj, dx, dy)

def _translate_owned(obj, dx, dy):
    obj.x += dx
    obj.y += dy
    for piece in _composite_pieces(obj):
        piece.x += dx
        piece.y += dy
    if hasattr(obj, 'spawnX'):
        obj.spawnX += dx
    if hasattr(obj, 'spawnY'):
        obj.spawnY += dy
    if hasattr(obj, 'startX'):
        obj.startX += dx
    if hasattr(obj, 'targetX'):
        obj.targetX += dx
    if hasattr(obj, 'startY'):
        obj.startY += dy
    if hasattr(obj, 'targetY'):
        obj.targetY += dy

def _require_type(catalog, type, what):
    # Every placement factory requires an explicit type - no catalog has a
    # pack-configured default (ENEMY_DEFAULT_TYPE, the one exception, was
    # removed as a source of hard-to-remember implicit behavior).
    if type is None:
        raise ValueError(f"{what} needs an explicit type - assign one when authoring this content.")
    if type in catalog:
        return catalog[type]
    raise ValueError(f"Unknown type {type!r} - expected one of {sorted(catalog.keys())}")

def _require_str(value, what):
    if not isinstance(value, str):
        raise ValueError(f"{what} needs a string.")
    return value