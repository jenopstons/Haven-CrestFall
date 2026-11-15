# Pickups, keys, barriers, switches, hazards, decor, signs - content a room
# script calls directly. _open_barrier is barrier-internal, used by
# Barrier's own loop. _requires_met/_validate_requires are the one shared
# global-gate primitive behind add_barrier/add_exit's `requires` and a
# placement's appears_when/disappears_when (grid.py): a global name, a list
# (all must be true), or None. Boolean-only, checked at author time
# (_validate_requires), not just at runtime - a truthiness check silently
# misreads a nonzero int or a non-empty enum string as "met," so a
# numeric/enum global here fails loudly instead of quietly doing the wrong
# thing.


def _requires_met(requires):
    # requires is a single declared global name, a list of names (all must
    # be true), or None (always met). Reads through get_global(), which
    # raises for any undeclared name instead of silently treating it as unset.
    if requires is None:
        return True
    names = requires if isinstance(requires, list) else [requires]
    for name in names:
        if not get_global(name):
            return False
    return True

def _validate_requires(requires, what):
    if requires is None:
        return
    for name in (requires if isinstance(requires, list) else [requires]):
        _validate_global(name, what)
        if _global_type(name) != 'bool':
            raise ValueError(
                f"{what} only supports boolean globals - "
                f"{name!r} is type {_global_type(name)!r}."
            )


def _clear_duplicate_tile(x, y, sprite, exclude=None):
    # Removes any Platform/Decor at this exact position using this exact
    # sprite - the map's own grid content sometimes draws the same art a
    # real object supplies itself. `exclude` is the object just created,
    # which can carry that same position/sprite and must never match itself.
    if sprite is None:
        return
    for obj in get_room_objects():
        if obj is exclude or obj._destroyed or not _tile_identities_overlap(getattr(obj, 'tileSprite', None), sprite):
            continue
        if obj.x == x and obj.y == y:
            destroy(obj)


def _open_barrier(barrier):
    if barrier._destroyed or not barrier.locked:
        return
    met = barrier.condition() if barrier.condition is not None else _requires_met(barrier.requires)
    if not met:
        return
    barrier.locked = False
    _play_sound('unlock')
    _mark_persisted('openedBarriers', barrier.persistentId)
    destroy_object(barrier)


def _validate_remember_as(remember_as, category, what):
    if remember_as is None:
        return
    if not isinstance(remember_as, str) or remember_as == '':
        raise ValueError(f"{what}'s remember_as must be a non-empty string.")


def add_collectible(*, at, type=None, sets_global=None, id=None, remember_as=None):
    # Validate everything that can fail before reserving id=/remember_as= -
    # a failed call must not leave a name reserved that a later, correct
    # call could otherwise use.
    x, y = _resolve_at(at)
    if sets_global is not None:
        _validate_global(sets_global, 'add_collectible')
        if _global_type(sets_global) != 'bool':
            raise ValueError(f"add_collectible's sets_global only supports boolean globals - {sets_global!r} is type {_global_type(sets_global)!r}.")
    cfg = _require_type(COLLECTIBLE_TYPES, type, 'add_collectible')
    _reserve_id(id)
    _reserve_remember_as(remember_as)
    persistent_id = _persistent_id(remember_as)
    _clear_duplicate_tile(x, y, _tile_identity(cfg['sprite']))
    if _is_persisted('collectedMapItems', persistent_id):
        return None
    c = _build_collectible(x, y, type, sets_global)
    c.persistentId = persistent_id
    _register_instance('collectible', type, c, id=id)
    return c


def _build_collectible(x, y, type, sets_global):
    # Shared by add_collectible and add_key - registration is the caller's
    # job, since a key registers as ('key', type) only, never also as
    # ('collectible', type) (that would double-count it under both kinds).
    cfg = _require_type(COLLECTIBLE_TYPES, type, 'add_collectible')
    c = Collectible()
    c.x = x
    c.y = y
    c.setsGlobal = sets_global
    c.counter = cfg['counter']
    c.sound = cfg.get('sound') or ('collect' if c.counter else 'pickup')
    c.effect = cfg.get('effect', 'none')
    c.healAmount = cfg.get('healAmount', 1)
    c.unlocks = cfg.get('unlocks')
    if c.effect not in PICKUP_EFFECTS:
        raise ValueError(f"Collectible type {type!r} has effect {c.effect!r}; use one of {PICKUP_EFFECTS}.")
    if c.effect == 'unlock' and c.unlocks not in UNLOCKABLES:
        raise ValueError(f"Collectible type {type!r} unlocks {c.unlocks!r}; use one of {UNLOCKABLES}.")
    _apply_pose(c, _load_pose(cfg['sprite']))
    c.scaleX = getattr(c, 'artFacing', 1)
    c.tileSprite = _tile_identity(cfg['sprite'])
    return c


def add_decor(*, at, type=None, id=None):
    # Decor has no collision tag or gameplay state - map art, not a
    # Platform masquerading as art. Never remembered.
    x, y = _resolve_at(at)
    _reserve_id(id)
    cfg = _require_type(DECOR_TYPES, type, 'add_decor')
    d = Decor()
    _apply_pose(d, _load_pose(cfg['sprite']))
    d.scaleX = getattr(d, 'artFacing', 1)
    d.tileSprite = _tile_identity(cfg['sprite'])
    d.x = x
    d.y = y
    _register_instance('decor', type, d, id=id)
    return d


def add_climbable(*, at, type=None, id=None):
    # A ladder, vine or rope: the player climbs it with up and down and can
    # stand on the top one of a column. Never blocks movement; never remembered.
    x, y = _resolve_at(at)
    _reserve_id(id)
    cfg = _require_type(CLIMBABLE_TYPES, type, 'add_climbable')
    c = Climbable()
    _apply_pose(c, _load_pose(cfg['sprite']))
    c.scaleX = getattr(c, 'artFacing', 1)
    c.tileSprite = _tile_identity(cfg['sprite'])
    c.x = x
    c.y = y
    _clear_duplicate_tile(x, y, c.tileSprite, exclude=c)
    _register_instance('climbable', type, c, id=id)
    return c


def add_key(*, at, sets_global=None, type=None, id=None, remember_as=None):
    # A labeled collectible - delegates to add_collectible rather than a
    # separate class/catalog. Returns the created Collectible, or None if
    # this authored key's remember_as was already resolved on an earlier
    # visit to this room - never a destroyed handle.
    x, y = _resolve_at(at)
    if sets_global is None:
        raise ValueError('add_key needs sets_global - the declared global name this key sets.')
    if type is None:
        raise ValueError('add_key needs an explicit type - assign one when authoring this content.')
    _validate_global(sets_global, 'add_key')
    if _global_type(sets_global) != 'bool':
        raise ValueError(f"add_key's sets_global only supports boolean globals - {sets_global!r} is type {_global_type(sets_global)!r}.")
    cfg = _require_type(COLLECTIBLE_TYPES, type, 'add_key')
    _reserve_id(id)
    _reserve_remember_as(remember_as)
    persistent_id = _persistent_id(remember_as)
    # Cleared unconditionally, even on a return visit where the key was
    # already collected - the raw grid's own placeholder art for this key
    # must never linger just because no Collectible gets built this time.
    _clear_duplicate_tile(x, y, _tile_identity(cfg['sprite']))
    if _is_persisted('collectedMapItems', persistent_id):
        return None
    key = _build_collectible(x, y, type, sets_global)
    key.persistentId = persistent_id
    _register_instance('key', type, key, id=id)
    return key


def add_barrier(*, at, requires=None, type=None, id=None, remember_as=None):
    # A solid, conditional obstruction that never changes rooms - opens
    # only when its requirement is met AND the player touches it. at=
    # identifies the part at row=0, col=0. remember_as makes the opened
    # state persistent across room re-entry (a remember_as-less barrier
    # rebuilds locked every visit, same as a remember_as-less key never
    # persisting).
    x, y = _resolve_at(at)
    if requires is None:
        raise ValueError('add_barrier needs requires - the declared global name (or list of names) that unlocks it.')
    _validate_requires(requires, 'add_barrier')
    cfg = _require_type(BARRIER_TYPES, type, 'add_barrier')
    _reserve_id(id)
    _reserve_remember_as(remember_as)
    persistent_id = _persistent_id(remember_as)
    already_opened = _is_persisted('openedBarriers', persistent_id)
    b = Barrier()
    # A single part at the anchor by default - same convention as
    # add_exit's own composite handling (progression.py). A
    # multi-cell barrier type declares its own 'parts' to opt into that.
    parts = _composite_parts(cfg, [{'row_offset': 0, 'col_offset': 0, 'sprite': cfg.get('sprite')}])
    base = _composite_base_part(parts, 'Barrier type')
    _apply_pose(b, _load_pose(base['sprite']))
    b.scaleX = getattr(b, 'artFacing', 1)
    b.tileSprite = _tile_identity(base['sprite'])
    b.x = x
    b.y = y
    b.requires = requires
    b.persistentId = persistent_id
    _clear_duplicate_tile(x, y, b.tileSprite, exclude=b)
    # Measured spacing, not an assumed CELL-sized grid - a barrier's own art
    # need not match the room's tile size. World y increases upward, so a
    # positive (downward) row_offset subtracts from y.
    step_w = get_width(b)
    step_h = get_height(b)
    b.parts = []
    for part in parts:
        if part is base:
            continue
        piece = Platform()
        _apply_pose(piece, _load_pose(part['sprite']))
        piece.scaleX = getattr(piece, 'artFacing', 1)
        piece.tileSprite = _tile_identity(part['sprite'])
        piece.x = x + part['col_offset'] * step_w
        piece.y = y - part['row_offset'] * step_h
        piece.z = 2
        piece.barrier = b
        _clear_duplicate_tile(piece.x, piece.y, piece.tileSprite, exclude=piece)
        b.parts.append(piece)
    if already_opened:
        # Unlocked on an earlier visit to this room - every part's raw grid
        # duplicate is already cleared above, so just remove the (re-locked)
        # barrier itself rather than making the player open it again. No
        # live handle for an absent placement - return None.
        b.locked = False
        for part in b.parts:
            destroy(part)
        destroy(b)
        return None
    _register_instance('barrier', type, b, id=id)
    return b


def add_switch(*, at, sets_global=None, type=None, id=None, remember_as=None, reusable=False, activation='touch'):
    # Use-once by default: first touch sets the global and it stops
    # reacting after that. reusable=True flips the global on every touch.
    # A one-shot switch whose global is already true starts used. remember_as
    # preserves used state independently if another script later clears that
    # global. A reusable switch with remember_as is rejected because it has no
    # one-time effect to remember. activation='touch' (default) fires on
    # contact; 'interact' requires 'e' and only fires when is_interact_target
    # selects it - same convention as add_exit.
    x, y = _resolve_at(at)
    if reusable and remember_as is not None:
        raise ValueError('add_switch cannot combine reusable=True with remember_as - a reusable switch has no one-time effect to remember.')
    if sets_global is None:
        raise ValueError('add_switch needs sets_global - the declared global name this switch toggles.')
    if activation not in ('touch', 'interact'):
        raise ValueError("add_switch needs activation='touch' or 'interact'.")
    _validate_global(sets_global, 'add_switch')
    if _global_type(sets_global) != 'bool':
        raise ValueError(f"add_switch's sets_global only supports boolean globals - {sets_global!r} is type {_global_type(sets_global)!r}.")
    poses = _require_type(SWITCH_TYPES, type, 'add_switch')['poses']
    _reserve_id(id)
    _reserve_remember_as(remember_as)
    persistent_id = _persistent_id(remember_as)
    s = Switch()
    s.onSprite = _load_pose(_resolve_pose(poses, 'on'))
    s.offSprite = _load_pose(_resolve_pose(poses, 'off'))
    s.setsGlobal = sets_global
    s.reusable = reusable
    s.activation = activation
    s.interactSeq = _next_interact_seq()
    s.persistentId = persistent_id
    if (not reusable and get_global(sets_global)) or _is_persisted('usedSwitches', persistent_id):
        s.used = True
    s.x = x
    s.y = y
    # A one-shot switch's visible pose always reflects its global, including
    # immediately on construction, not only on its next loop() - used state
    # and global value are distinct (a used switch can be inert even if the
    # global later goes false).
    _apply_pose(s, s.onSprite if get_global(sets_global) else s.offSprite)
    s.scaleX = getattr(s, 'artFacing', 1)
    _clear_duplicate_tile(x, y, _tile_identity(_resolve_pose(poses, 'on')), exclude=s)
    _clear_duplicate_tile(x, y, _tile_identity(_resolve_pose(poses, 'off')), exclude=s)
    _register_instance('switch', type, s, id=id)
    return s


def add_hazard(*, at, type=None, id=None):
    # Never remembered. A switch-gated hazard is a placement with
    # disappears_when (see grid.py's _update_appearing).
    x, y = _resolve_at(at)
    _reserve_id(id)
    cfg = _require_type(HAZARD_TYPES, type, 'add_hazard')
    h = Hazard()
    _apply_pose(h, _load_pose(cfg['sprite']))
    h.scaleX = getattr(h, 'artFacing', 1)
    h.tileSprite = _tile_identity(cfg['sprite'])
    h.x = x
    h.y = y
    h.damage = cfg.get('damage', 1)
    h.hitbox = _pose_hitbox(cfg['sprite'])
    _clear_duplicate_tile(x, y, h.tileSprite, exclude=h)
    _register_instance('hazard', type, h, id=id)
    return h


def add_sign(*, at, lines=None, type=None, id=None):
    # Uses the NPC dialogue interaction, with its own visual catalog. Never
    # remembered. lines has the same shape as add_npc's lines - speaker
    # labels belong to the dialogue data.
    x, y = _resolve_at(at)
    _reserve_id(id)
    if lines is None:
        raise ValueError('add_sign needs lines - the list of things it says.')
    if not isinstance(lines, list):
        raise ValueError('add_sign needs lines to be a list.')
    _validate_dialogue_lines(lines, 'add_sign')
    s = NPC()
    cfg = _require_type(SIGN_TYPES, type, 'add_sign')
    signSprite = cfg['sprite']
    _apply_pose(s, _load_pose(signSprite))
    s.stillPose = signSprite
    s.scaleX = getattr(s, 'artFacing', 1)
    s.lines = lines
    s.interactSeq = _next_interact_seq()
    s.x = x
    s.y = y
    _clear_duplicate_tile(x, y, _tile_identity(cfg['sprite']), exclude=s)
    _register_instance('sign', type, s, id=id)
    return s