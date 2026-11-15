# Every CONTROLS action is a list of keys; pressing any of them triggers it. A name starting
# with 'mouse' is a mouse button instead: 'mouseleft' or 'mouseright'.

def _input_is_pressed(key):
    return mouse_is_pressed(key[5:]) if key.startswith('mouse') else key_is_pressed(key)


def _input_was_pressed(key):
    return mouse_was_pressed(key[5:]) if key.startswith('mouse') else key_was_pressed(key)


def _input_was_released(key):
    return mouse_was_released(key[5:]) if key.startswith('mouse') else key_was_released(key)


def _control_is_pressed(action):
    return any(_input_is_pressed(key) for key in CONTROLS[action])


def _control_was_pressed(action):
    return any(_input_was_pressed(key) for key in CONTROLS[action])


def _control_was_released(action):
    return any(_input_was_released(key) for key in CONTROLS[action])