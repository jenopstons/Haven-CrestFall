FadeIn()

bg = Background()
bg.sprite = sprite("background.png")
bg.visible = True
self.timer = 200
self.message = text("Victory!", 0, 0)
self.message.fontSize = 36
self.message.halign = 'center'
self.message.valign = 'middle'
self.message.color = '#ffffff'
self.message.font_family = "VT323"

creditStr = "Crestfall: \nDev - Liam M \nDev - Toby W \nSong - Arthur DA"
self.credit = text(creditStr)
self.credit.fontSizw = 12
self.credit.color = "white"
self.credit.halign = "center"
self.credit.valign = 'middle'
self.credit.color = '#ffffff'
self.credit.font_family = "VT323"
self.credit.y = -400