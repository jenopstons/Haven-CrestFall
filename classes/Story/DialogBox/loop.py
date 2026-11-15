# Guards against one extra loop() call the same frame this box is
# destroyed.
if self._destroyed:
    return
dialogLayout = UI_CONFIG['dialog']
self.x = camera_x()
self.y = camera_y() + dialogLayout['y']
self.speakerText.x = self.x + dialogLayout['textOffsetX']
self.speakerText.y = self.y + dialogLayout['speakerOffsetY']
self.speakerText.visible = self.visible
self.messageText.x = self.x + dialogLayout['textOffsetX']
self.messageText.y = self.y + dialogLayout['messageOffsetY']
self.messageText.visible = self.visible
if self.hint is not None:
    _place_dialog_hint(self)
    self.hint.visible = self.visible
if self.revealed < len(self.fullText):
    shownBefore = int(self.revealed)
    self.revealed = min(len(self.fullText), self.revealed + dialogLayout['typeSpeed'])
    shownNow = int(self.revealed)
    self.messageText.text = self.fullText[:shownNow]
    for letter in self.fullText[shownBefore:shownNow]:
        if letter.strip():
            if self.talkCount % dialogLayout.get('talkSoundEvery', 3) == 0:
                _play_sound('talk')
            self.talkCount += 1
