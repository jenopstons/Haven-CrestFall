game.frame = 0
game.counter = 0
game.persisted = {}
game.globals = {}
game._studio_sound_fades = []
game._studio_room_music = None
game._studio_room_music_volume = 0
if GAME_MUSIC is not None:
    game._studio_game_music = sound(GAME_MUSIC['file'])
    set_volume(game._studio_game_music, GAME_MUSIC['volume'])
    loop_sound(game._studio_game_music)
_validate_static_exit_destinations()
game.startRoom = "DungeonStart"
game.startLocation = "start"
_validate_start(game.startRoom, game.startLocation)
_validate_title("A_title_screen")
_enter_room("A_title_screen", None)