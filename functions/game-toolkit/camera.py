# Camera clamping and shake, genre-neutral.
# Imported here for CameraShake's own use (its loop needs randint).
import random

def _clamped_camera(x, y):
    # Keeps the camera inside cameraBounds (set by build_tilemap). A map narrower
    # than the viewport is centred; a map shorter than it sits on the bottom edge.
    # Unbounded if cameraBounds was never set.
    bounds = getattr(game, 'cameraBounds', None)
    if bounds is None:
        return (x, y)
    left, right, bottom, top = bounds
    viewport = ENGINE_DEFAULTS['viewport']
    view_w = viewport['width']
    view_h = viewport['height']
    if right - left <= view_w:
        cx = (left + right) / 2
    else:
        cx = min(max(x, left + view_w / 2), right - view_w / 2)
    if top - bottom <= view_h:
        cy = bottom + view_h / 2
    else:
        cy = min(max(y, bottom + view_h / 2), top - view_h / 2)
    return (cx, cy)

def _add_camera_shake():
    return CameraShake()

def _on_screen(obj):
    # True when any part of obj's sprite is inside the camera's view.
    viewport = ENGINE_DEFAULTS['viewport']
    return (abs(obj.x - camera_x()) * 2 < viewport['width'] + abs(get_width(obj))
            and abs(obj.y - camera_y()) * 2 < viewport['height'] + abs(get_height(obj)))