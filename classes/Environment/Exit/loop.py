if self._destroyed:
    return
region = self.region
if region is None or region['reached']:
    return
# Two overlapping exits that end the game must not both finish it in the
# same frame.
if not region['toRoom'] and getattr(game, 'finished', False):
    return
touching = any(get_collision(trigger, 'PlayerHitbox') for trigger in region['triggers'])
indicator = region['promptIndicator']
if not touching:
    # Leaving the region re-arms it and resets the dialog guard.
    region['armed'] = True
    region['dialogFrame'] = None
    region['dialogShown'] = False
    if indicator is not None:
        destroy(indicator)
        region['promptIndicator'] = None
    return
# One region can be shared by several trigger parts - only process each once per frame.
if region['dialogFrame'] == game.frame:
    return
region['dialogFrame'] = game.frame
if not region['armed']:
    return
if region['prompt']:
    if indicator is None and not region.get('promptSuppressed') and UI_CONFIG['dialog']['indicator']['pose'] is not None:
        indicator = DialogPrompt()
        region['promptIndicator'] = indicator
    if indicator is not None:
        indicatorLayout = UI_CONFIG['dialog']['indicator']['exit']
        indicator.x = self.x + indicatorLayout['offsetX']
        indicator.y = self.y + get_height(self) / 2 + get_height(indicator) / 2 + indicatorLayout['gap']
        indicator.visible = not region.get('promptSuppressed')
        indicator.alpha = region.get('promptAlpha', 1)
    # The shared interaction selector may have picked a different nearby
    # NPC/sign/door for this frame's interact press - only the chosen
    # target acts.
    if not is_interact_target(region) or not _control_was_pressed('interact'):
        return
if not _requires_met(region['requires']):
    if not region['dialogShown']:
        if region['failText']:
            show_dialog('', region['failText'])
            region['dialogShown'] = True
        return
    if _control_was_pressed('interact') and not _finish_dialog_typing():
        hide_dialog()
    return
region['reached'] = True
if indicator is not None:
    destroy(indicator)
    region['promptIndicator'] = None
if region['toRoom']:
    _play_sound('travel')
    go_to_room(region['toRoom'], region['toLocation'])
    return
_play_sound('goal')
game.finished = True
# A callback observes completion - it never replaces the default
# freeze/dialog, so installing one can't silently disable it.
player = game.player
# Freezing skips Player-loop.py entirely, which is what normally ticks
# invulnerable/visible each frame - stop the damage-flash blink first, or
# the player can freeze mid-blink and stay invisible for the rest of the game.
player.invulnerable = 0
player.visible = True
if player.damageFilterId is not None:
    remove_filter(player, player.damageFilterId)
    player.damageFilterId = None
player.frozen = True
show_dialog('', region['successText'] or "Goal reached!")
# Nothing runs this object's loop again after 'reached' is set (see the
# early return at the top) - the generic game loop's own dialog-dismiss
# fallback (see assemble-game.ts) closes this one instead.
_dispatch('gameFinished', self)
