if self._destroyed:
    return
if getattr(game, 'finished', False):
    _freeze_for_win(self)
    return
near = get_collision(self, 'PlayerHitbox')
# Once talking, this NPC stays the interact target until its conversation ends.
isTarget = (near or self.talking) and is_interact_target(self)

_update_interact_prompt(self, isTarget and not self.talking, 'npc')

if isTarget and _control_was_pressed('interact'):
    if self.talking and _finish_dialog_typing():
        pass
    elif self.index < len(self.lines):
        line = self.lines[self.index]
        if isinstance(line, dict):
            show_dialog(line.get('speaker', ''), line['text'])
        else:
            show_dialog('', line)
        self.index += 1
        self.talking = True
        game.dialogOwner = self
    else:
        hide_dialog()
        self.index = 0
        self.talking = False
elif self.talking and getattr(game, 'dialogBox', None) is None:
    # The dialog box can close from this NPC's own branch above, or from
    # the generic dialog-dismiss fallback once the player is out of range -
    # either way, reset local state so the "press E" prompt can show again.
    self.index = 0
    self.talking = False
