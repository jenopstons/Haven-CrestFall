if self._destroyed:
    return
owner = self.owner
if owner is None or owner._destroyed or owner.dying:
    for part in (self.border, self.panel, self.frame, self.track, self.fill, self.label):
        destroy(part)
    destroy(self)
    return
live = _live_boss_bars()
index = next((slot for slot, bar in enumerate(live) if bar is self), 0)
layout = UI_CONFIG['bossBar']
nameHeight = layout['fontSize'] * BOSS_NAME_SHARE
barTop = layout['height'] / 2 + HUD_FRAME
panelWidth = layout['width'] + 2 * (HUD_FRAME + BOSS_PANEL_PADDING)
panelHeight = 2 * barTop + BOSS_PANEL_PADDING + layout['labelGap'] + nameHeight + BOSS_PANEL_TOP
x = camera_x()
y = camera_y() + layout['y'] - index * (panelHeight + 2 * HUD_FRAME + layout['gap'])
panelY = y - barTop - BOSS_PANEL_PADDING + panelHeight / 2
_place_hud_rect(self.border, x, panelY, panelWidth + 2 * HUD_FRAME, panelHeight + 2 * HUD_FRAME)
_place_hud_rect(self.panel, x, panelY, panelWidth, panelHeight)
share = min(max(owner.health / owner.maxHealth, 0), 1) if owner.maxHealth > 0 else 0
_place_hud_bar(self, x - layout['width'] / 2, y, layout['width'], layout['height'], share)
self.label.x = x
self.label.y = y + barTop + layout['labelGap'] + nameHeight / 2
