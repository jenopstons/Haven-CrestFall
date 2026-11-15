FadeIn()

bg = Background()
bg.sprite = sprite("background.png")
bg.visible = True
title = text("Controls", 0, 40)
title.fontSize = 24
title.halign = 'center'
title.valign = 'middle'
title.color = '#ffffff'
title.font_family = "VT323"

prompt = text("A/D | Move left/right \nW/S | Look up/down \nSpacebar | Jump \nRightClick/J | Use Item", 0, -30)
prompt.fontSize = 12
prompt.halign = 'center'
prompt.valign = 'middle'
prompt.color = '#ffffff'
prompt.font_family = "VT323"