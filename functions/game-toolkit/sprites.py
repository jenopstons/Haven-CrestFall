# Pose loading/resolution, genre-neutral. A raw "pose" is a filename, a
# (filename, frame) tuple, or a {sheet, start, end} range - SPRITES (config)
# says how each filename slices into frames. Sprite-pack poses may wrap that
# descriptor with art-facing metadata; _load_pose accepts both shapes.

def _tile_identity(sprite):
    # A comparable (file, {frames}) identity for a tile's raw sprite
    # descriptor - a single frame or an animated range - or None when it's
    # neither (a bare filename, ...). Pack-compiled poses wrap the
    # descriptor under 'pose' (see _load_pose above) - unwrap that first so
    # a pack-bound type and a grid-imported type using the same frame(s)
    # compare equal.
    if isinstance(sprite, dict) and 'pose' in sprite:
        sprite = sprite['pose']
    if isinstance(sprite, (tuple, list)) and len(sprite) == 2:
        return (sprite[0], {sprite[1]})
    if isinstance(sprite, dict) and 'sheet' in sprite and 'start' in sprite and 'end' in sprite:
        return (sprite['sheet'], set(range(sprite['start'], sprite['end'] + 1)))
    return None

def _tile_identities_overlap(a, b):
    # A raw grid duplicate is often just one static frame of what a real
    # object animates through (e.g. one frame of a 2-frame waving flag) -
    # same underlying art, so this matches on any shared frame, not
    # identity equality.
    if a is None or b is None:
        return False
    return a[0] == b[0] and bool(a[1] & b[1])

def _load_pose(file, fps=None):
    # Pack-compiled poses carry the old descriptor under 'pose' plus the
    # resolved art orientation. Raw descriptors remain supported for map
    # imports and hand-authored engine data.
    facing = 1
    if isinstance(file, dict) and 'pose' in file:
        facing = file.get('facing', 1)
        file = file.get('pose')
    if file is None:
        return None
    if isinstance(file, dict):
        # A shared atlas sheet plus a contiguous frame range.
        filename = file.get('sheet')
        if filename is None:
            return None
        meta = SPRITES.get(filename, {'rows': 1, 'cols': 1})
        resolved_fps = fps if fps is not None else file.get('fps', meta.get('fps', 15))
        start = int(file.get('start', 0))
        end = int(file.get('end', start))
        sheet = sprite(filename, meta['rows'], meta['cols'])
        return ('anim', animation(sheet, resolved_fps, start, end), facing)
    if isinstance(file, tuple):
        # (filename, frame_index) - one static frame cut from an atlas.
        filename, frame = file
        meta = SPRITES.get(filename, {'rows': 1, 'cols': 1})
        sheet = sprite(filename, meta['rows'], meta['cols'])
        return ('anim', animation(sheet, 0, frame, frame), facing)
    meta = SPRITES.get(file, {'rows': 1, 'cols': 1})
    resolved_fps = fps if fps is not None else meta.get('fps', 15)
    sheet = sprite(file, meta['rows'], meta['cols'])
    frames = meta['rows'] * meta['cols']
    if frames > 1:
        return ('anim', animation(sheet, resolved_fps, 0, frames - 1), facing)
    return ('sprite', sheet, facing)

def _apply_pose(obj, pose):
    if pose is None:
        return
    kind = pose[0]
    data = pose[1]
    # `artFacing` is metadata from the current pose, not the character's
    # logical travel direction. A two-item runtime pose remains valid for
    # older hand-authored callers and uses the neutral orientation.
    obj.artFacing = pose[2] if len(pose) > 2 else 1
    if kind == 'anim':
        set_animation(obj, data)
    else:
        obj.sprite = data

def _resolve_pose(poses, wanted):
    # Falls back to 'idle', then any defined pose, if `wanted` isn't set.
    if wanted in poses:
        return poses[wanted]
    if 'idle' in poses:
        return poses['idle']
    for value in poses.values():
        return value
    return None

def _set_character_pose(obj, poses, wanted):
    _apply_pose(obj, _load_pose(_resolve_pose(poses, wanted)))

def _pose_hitbox(sprite):
    if isinstance(sprite, dict) and 'pose' in sprite:
        return sprite.get('hitbox')
    return None

def _hitbox_touches(obj, hitbox, other):
    # hitbox fractions are measured from the unflipped art's top-left; world y points up.
    w = abs(get_width(obj))
    h = abs(get_height(obj))
    left = 1 - hitbox['x'] - hitbox['width'] if obj.scaleX < 0 else hitbox['x']
    top = 1 - hitbox['y'] - hitbox['height'] if obj.scaleY < 0 else hitbox['y']
    cx = obj.x - w / 2 + (left + hitbox['width'] / 2) * w
    cy = obj.y + h / 2 - (top + hitbox['height'] / 2) * h
    return (abs(cx - other.x) * 2 < hitbox['width'] * w + abs(get_width(other))
            and abs(cy - other.y) * 2 < hitbox['height'] * h + abs(get_height(other)))


def _apply_game_font(label):
    # Gives a text object the game's font, when the project picked one.
    font = UI_CONFIG.get('font')
    if font:
        label.font_family = font