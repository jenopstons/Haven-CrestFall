# Narrative dialog box, genre-neutral. Lines are wrapped manually by
# measuring each candidate line's rendered width.

def _validate_dialogue_lines(lines, what):
    for index, line in enumerate(lines):
        if isinstance(line, str):
            continue
        if not isinstance(line, dict) or not isinstance(line.get('text'), str):
            raise ValueError(f"{what} line {index + 1} needs a string or a dict with string 'text'.")
        speaker = line.get('speaker')
        if speaker is not None and not isinstance(speaker, str):
            raise ValueError(f"{what} line {index + 1} needs 'speaker' to be a string when provided.")

def _wrap_dialog(box, s):
    maxWidth = abs(UI_CONFIG['dialog']['textOffsetX']) * 2
    words = s.split(' ')
    lines = []
    current = ''
    for word in words:
        candidate = (current + ' ' + word) if current else word
        box.messageText.text = candidate
        if get_width(box.messageText) > maxWidth and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return '\n'.join(lines)

def _place_dialog_hint(box):
    # Keeps the hint inside the box's bottom-right corner at its own size, whatever the zoom.
    layout = UI_CONFIG['dialog']
    box.hint.x = box.x + get_width(box) / 2 - layout['hintMarginX'] - get_width(box.hint) / 2
    box.hint.y = box.y - get_height(box) / 2 + layout['hintMarginY'] + get_height(box.hint) / 2

def show_dialog(speaker, line):
    box = getattr(game, 'dialogBox', None)
    if box is None:
        box = DialogBox()
        game.dialogBox = box
    box.speakerText.text = speaker or ''
    box.fullText = _wrap_dialog(box, line)
    box.talkCount = 0
    if UI_CONFIG['dialog'].get('typeSpeed', 0) > 0:
        box.revealed = 0
        box.messageText.text = ''
    else:
        box.revealed = len(box.fullText)
        box.messageText.text = box.fullText
    box.visible = True

def _finish_dialog_typing():
    # Shows the rest of a line that is still typing out; False when there was nothing left to show.
    box = getattr(game, 'dialogBox', None)
    if box is None or box.revealed >= len(box.fullText):
        return False
    box.revealed = len(box.fullText)
    box.messageText.text = box.fullText
    return True

def hide_dialog():
    box = getattr(game, 'dialogBox', None)
    if box is not None:
        destroy(box.speakerText)
        destroy(box.messageText)
        if box.hint is not None:
            destroy(box.hint)
        destroy(box)
        game.dialogBox = None
    game.dialogOwner = None