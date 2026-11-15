FadeIn()

bg = Background()
bg.sprite = sprite("background.png")
bg.visible = True
title = text("Crestfall", 0, 40)
title.fontSize = 24
title.halign = 'center'
title.valign = 'middle'
title.color = '#ffffff'
title.font_family = "VT323"

prompt = text("Click to start", 0, -30)
prompt.fontSize = 12
prompt.halign = 'center'
prompt.valign = 'middle'
prompt.color = '#ffffff'
prompt.font_family = "VT323"