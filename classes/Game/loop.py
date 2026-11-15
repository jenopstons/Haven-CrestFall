game.frame += 1
_update_sound_fades()
# skipDialog closes any open dialog at once, skipping a conversation's
# remaining lines.
if _control_was_pressed('skipDialog') and getattr(game, 'dialogBox', None) is not None:
    hide_dialog()
# A dialog with nothing currently claiming the interact key (no NPC/sign
# conversation and no interact-activated exit is the active
# _resolve_interact_target()) just closes on the next press - covers an
# exit's own end-of-game dialog (its object stops running once reached) and
# any one-shot dialog a callback or room script shows directly, with no
# extra code needed from whoever called show_dialog().
if (
    _control_was_pressed('interact')
    and getattr(game, 'dialogBox', None) is not None
    and _resolve_interact_target() is None
    and not _finish_dialog_typing()
):
    hide_dialog()
# CONTROLS['debugGrid'] toggles a (row, col) label over every cell of the
# current room's grid - an authoring aid for finding the right
# cell(row, col) while building a map, not gameplay. An empty debugGrid
# opts out of this tool entirely.
if _control_was_pressed('debugGrid') and game.mapRows is not None:
    labels = getattr(game, 'debugCoordLabels', None)
    if labels:
        for label in labels:
            destroy(label)
        game.debugCoordLabels = None
    else:
        labels = []
        for row in range(game.mapRows):
            for col in range(game.mapCols):
                x, y = xy(row, col)
                label = text(f'({row}, {col})', x, y)
                label.fontSize = 12
                label.halign = 'center'
                label.valign = 'middle'
                label.color = 'magenta'
                label.z = 999
                labels.append(label)
        game.debugCoordLabels = labels
# CONTROLS['debugHitbox'] toggles the player's own collision hitbox
# visible, for testing - not gameplay. An empty debugHitbox opts out.
if _control_was_pressed('debugHitbox') and game.player is not None:
    game.player.hitbox.visible = not game.player.hitbox.visible