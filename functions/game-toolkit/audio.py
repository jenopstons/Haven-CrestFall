# Sound playback, genre-neutral.

def _play_sound(name):
    # name is a SOUNDS (generated from the active sound pack) key, not a filename.
    entry = SOUNDS[name]
    played = getattr(game, '_studio_sound_frames', {})
    last = played.get(name)
    if last is not None and game.frame - last < entry.get('cooldown', 0):
        return
    played[name] = game.frame
    game._studio_sound_frames = played
    clip = sound(entry['file'])
    set_volume(clip, entry['volume'])
    play_sound(clip)

def fade_sound(clip, from_volume, to_volume, frames, stop_at_end=False):
    set_volume(clip, from_volume)
    duration = max(1, int(frames))
    if frames <= 0:
        set_volume(clip, to_volume)
        if stop_at_end:
            stop_sound(clip)
        return
    fades = getattr(game, '_studio_sound_fades', [])
    active = []
    for fade in fades:
        if fade['clip'] is not clip:
            active.append(fade)
    active.append({
        'clip': clip,
        'from': from_volume,
        'to': to_volume,
        'frames': duration,
        'elapsed': 0,
        'stop': stop_at_end,
    })
    game._studio_sound_fades = active

def _cancel_sound_fades(clip):
    fades = getattr(game, '_studio_sound_fades', [])
    game._studio_sound_fades = [fade for fade in fades if fade['clip'] is not clip]

def _update_sound_fades():
    fades = getattr(game, '_studio_sound_fades', [])
    active = []
    for fade in fades:
        fade['elapsed'] += 1
        progress = min(1, fade['elapsed'] / fade['frames'])
        volume = fade['from'] + (fade['to'] - fade['from']) * progress
        set_volume(fade['clip'], volume)
        if progress >= 1:
            if fade['stop']:
                stop_sound(fade['clip'])
        else:
            active.append(fade)
    game._studio_sound_fades = active