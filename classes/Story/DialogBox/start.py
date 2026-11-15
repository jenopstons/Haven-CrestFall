_apply_pose(self, _load_pose(UI_CONFIG['dialog']['box']))
# With its box art removed, the dialogue shows its text with no background.
if UI_CONFIG['dialog']['box'] is None:
    self.alpha = 0
self.z = 200
self.fullText = ''
self.revealed = 0
self.talkCount = 0

# Positioned here too, not just in loop(), so it doesn't flash at the
# world origin for one frame before loop() first runs.
dialogLayout = UI_CONFIG['dialog']
self.x = camera_x()
self.y = camera_y() + dialogLayout['y']

textColor = dialogLayout.get('textColor', '#3a2412')

self.speakerText = text('', self.x + dialogLayout['textOffsetX'], self.y + dialogLayout['speakerOffsetY'])
self.speakerText.fontSize = UI_CONFIG['dialog']['speakerFontSize']
self.speakerText.color = textColor
_apply_game_font(self.speakerText)
self.speakerText.halign = 'left'
self.speakerText.z = 201

self.messageText = text('', self.x + dialogLayout['textOffsetX'], self.y + dialogLayout['messageOffsetY'])
self.messageText.fontSize = UI_CONFIG['dialog']['messageFontSize']
self.messageText.color = textColor
_apply_game_font(self.messageText)
self.messageText.halign = 'left'
self.messageText.z = 201

# The "press E" art in the corner, when the config pack lays it out.
self.hint = None
if 'hintMarginX' in dialogLayout and dialogLayout['indicator']['pose'] is not None:
    self.hint = DialogPrompt()
    _place_dialog_hint(self)
    self.hint.z = 201
