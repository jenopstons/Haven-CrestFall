# Exits: flags, doors and pipes that go to another room or end the game.


def _next_interact_seq():
    # A deterministic tie-break for the shared interaction selector below -
    # first-registered wins a tie, regardless of dict/list iteration order.
    seq = getattr(game, 'interactSeq', 0)
    game.interactSeq = seq + 1
    return seq


def _interact_distance(x, y):
    player = game.player
    dx = x - player.x
    dy = y - player.y
    return (dx * dx + dy * dy) ** 0.5


def _consider_simple_candidate(obj, best, best_key):
    # Shared by every single-object (non-composite-region) interactable -
    # npc/sign/interact-activated switch - so each category's branch below
    # only says which objects are eligible, not how to compare them. A
    # hidden interactable still works by intent (its prompt just stays
    # hidden) - hide_object never removes it from candidacy.
    if not get_collision(obj, 'PlayerHitbox'):
        return best, best_key
    key = (_interact_distance(obj.x, obj.y), obj.interactSeq)
    if best_key is None or key < best_key:
        return obj, key
    return best, best_key


def _resolve_interact_target():
    # NPCs, signs, interact-activated switches, and interact-activated
    # exits each want to consume the same 'e' press when the player
    # is near more than one at once. Recomputed once per frame (cached by
    # game.frame, not call order) so every candidate's loop() sees the same
    # answer regardless of which one runs first - exactly one interactable
    # can ever act on a given press.
    if getattr(game, 'interactFrame', None) == game.frame:
        return game.interactTarget
    game.interactFrame = game.frame
    # The NPC or sign that started an open conversation keeps every press
    # until it ends, even once the player walks out of range.
    owner = getattr(game, 'dialogOwner', None)
    if owner is not None:
        if (not owner._destroyed and getattr(owner, '_visitToken', game.visitToken) == game.visitToken
                and getattr(game, 'dialogBox', None) is not None):
            game.interactTarget = owner
            return owner
        game.dialogOwner = None
    best = None
    best_key = None
    for (category, _type), objs in game.byCategoryType.items():
        # A destroyed object raises on any attribute read except _destroyed.
        live = [obj for obj in objs if not obj._destroyed]
        if category in ('npc', 'sign'):
            for obj in live:
                if not getattr(obj, 'lines', None):
                    continue
                best, best_key = _consider_simple_candidate(obj, best, best_key)
        elif category == 'switch':
            for obj in live:
                if getattr(obj, 'activation', 'touch') != 'interact' or (not obj.reusable and obj.used):
                    continue
                best, best_key = _consider_simple_candidate(obj, best, best_key)
        elif category == 'exit':
            for trigger in live:
                region = trigger.region
                if not region.get('prompt') or region['reached'] or not region['armed']:
                    continue
                touching = [t for t in region['triggers'] if not t._destroyed and get_collision(t, 'PlayerHitbox')]
                if not touching:
                    continue
                nearest = min(touching, key=lambda t: _interact_distance(t.x, t.y))
                key = (_interact_distance(nearest.x, nearest.y), region['interactSeq'])
                if best_key is None or key < best_key:
                    best, best_key = region, key
    game.interactTarget = best
    return best


def is_interact_target(candidate):
    # False for None/dead/stale/noninteractable candidates, even though the
    # shared selector itself may resolve to None (no eligible candidate this
    # frame) - `None is None` would otherwise wrongly read as "yes."
    if candidate is None or getattr(candidate, '_destroyed', False):
        return False
    if getattr(candidate, '_visitToken', game.visitToken) != game.visitToken:
        return False
    return _resolve_interact_target() is candidate


def _update_interact_prompt(obj, show, layout):
    show = (show and not getattr(obj, 'promptSuppressed', False)
            and UI_CONFIG['dialog']['indicator']['pose'] is not None)
    if show and obj.prompt is None:
        obj.prompt = DialogPrompt()
    elif not show and obj.prompt is not None:
        destroy(obj.prompt)
        obj.prompt = None
    if obj.prompt is not None:
        offsets = UI_CONFIG['dialog']['indicator'][layout]
        obj.prompt.x = obj.x + offsets['offsetX']
        obj.prompt.y = obj.y + get_height(obj) / 2 + get_height(obj.prompt) / 2 + offsets['gap']
        obj.prompt.alpha = getattr(obj, 'promptAlpha', 1)


def _new_exit_region(requires, success_text, fail_text, to_room, to_location, prompt):
    # Exits are collision proxies; this record owns the state shared by
    # every proxy in one composite, so a multi-part door or flag need not
    # collapse to one object's own fields.
    return {
        'requires': requires,
        'successText': success_text,
        'failText': fail_text,
        'toRoom': to_room,
        'toLocation': to_location,
        'prompt': prompt,
        'promptIndicator': None,
        'promptSuppressed': False,
        'promptAlpha': 1,
        'dialogFrame': None,
        'dialogShown': False,
        'armed': to_room is None,
        'reached': False,
        'triggers': [],
        'interactSeq': _next_interact_seq(),
    }


def _add_exit_trigger(x, y, pose, region):
    g = Exit()
    _apply_pose(g, _load_pose(pose))
    g.scaleX = getattr(g, 'artFacing', 1)
    g.x = x
    g.y = y
    g.region = region
    _clear_duplicate_tile(x, y, _tile_identity(pose), exclude=g)
    region['triggers'].append(g)
    return g


def _composite_parts(cfg, default_parts):
    # A type's own 'parts' (row_offset/col_offset off the at= anchor), or
    # `default_parts` when the type declares none - shared by every
    # composite factory (add_barrier, add_exit) so "no authored parts"
    # resolves the same way everywhere: a single part at the anchor.
    # Multi-cell content built this way writes its shared state once per
    # touch, not once per cell.
    parts = cfg.get('parts')
    return parts if parts is not None else default_parts


def _composite_base_part(parts, what):
    for part in parts:
        if part['row_offset'] == 0 and part['col_offset'] == 0:
            return part
    raise ValueError(f'{what} needs one part at row_offset=0, col_offset=0.')


def _add_composite_triggers(x, y, parts, base, region, step_w, step_h):
    # Adds every part besides `base` (already added by the caller) as its
    # own trigger on the shared region, offset by measured spacing - not an
    # assumed CELL-sized grid, since a type's art need not match the room's
    # tile size.
    for part in parts:
        if part is base:
            continue
        px = x + part['col_offset'] * step_w
        py = y - part['row_offset'] * step_h
        _add_exit_trigger(px, py, part['sprite'], region)


def add_exit(*, at, destination=None, activation='touch', requires=None,
             fail_text=None, success_text=None, type=None, id=None):
    # A flag, door or pipe. destination=(room, location) goes to a map room,
    # destination='Room' goes to a script room, and no destination ends the
    # game with success_text. A multi-cell exit is one composite: the type's
    # own 'parts' each add a touchable trigger to the same region, so a
    # player spanning two cells fires it once. Never remembered.
    x, y = _resolve_at(at)
    _reserve_id(id)
    to_room, to_location = _exit_destination(destination)
    if to_room is not None:
        _require_destination(game.room, to_room, to_location)
    if activation not in ('touch', 'interact'):
        raise ValueError("add_exit needs activation='touch' or 'interact'.")
    _validate_requires(requires, 'add_exit')
    if fail_text is not None and not isinstance(fail_text, str):
        raise ValueError('add_exit needs fail_text to be a string or None.')
    if success_text is not None and not isinstance(success_text, str):
        raise ValueError('add_exit needs success_text to be a string or None.')
    cfg = _require_type(EXIT_TYPES, type, 'add_exit')
    parts = _composite_parts(cfg, [{'row_offset': 0, 'col_offset': 0, 'sprite': cfg.get('sprite')}])
    base = _composite_base_part(parts, 'Exit type')
    region = _new_exit_region(requires, success_text, fail_text, to_room, to_location,
                              activation == 'interact')
    base_trigger = _add_exit_trigger(x, y, base['sprite'], region)
    _add_composite_triggers(x, y, parts, base, region, get_width(base_trigger), get_height(base_trigger))
    _register_instance('exit', type, base_trigger, id=id)
    return base_trigger