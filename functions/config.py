# Game settings - change these to customize the game.
PLAYER_CONFIG = {
    "maxHealth": 3,
    "fallMargin": 80,
    "hitboxWidthPercent": 50,
    "hitboxHeightPercent": 60,
    "accel": 0.6666666666666666,
    "decel": 0.6666666666666666,
    "maxSpeed": 1.5555555555555554,
    "jumpSpeed": 4.444444444444445,
    "fallMult": 2,
    "gravity": -0.18871111111111108,
    "terminalVel": -4.444444444444445,
    "jumpCut": 0.4,
    "coyoteMax": 10,
    "bufferMax": 9,
    "invulnerableFrames": 30,
    "damageFlashFrames": 8,
    "blinkCycleFrames": 4,
    "knockbackX": 5.333333333333333,
    "knockbackY": 1.7777777777777777,
    "landingSquashX": 1.3,
    "landingSquashY": 0.7,
    "jumpSquashX": 0.7,
    "jumpSquashY": 1.3,
    "squashEaseRate": 0.1,
    "stompBounce": 0.6,
    "stompDamage": 1,
    "launchJumpMultiplier": 1.4,
    "climbSpeed": 1.3333333333333333,
    "poses": {"idle": {"pose": ("tileset.png", 13), "facing": 1}, "run": {"pose": ("tileset.png", 13), "facing": 1}, "jumpUp": {"pose": ("tileset.png", 15), "facing": 1}, "jumpDown": {"pose": ("tileset.png", 16), "facing": 1}, "climb": {"pose": ("tileset.png", 13), "facing": 1}, "attack": {"pose": ("tileset.png", 16), "facing": 1}, "strike": {"pose": ("slash.png", 0), "facing": 1}},
    "projectile": None,
}
CONTROLS = {
    "moveLeft": ["a", "arrowleft"],
    "moveRight": ["d", "arrowright"],
    "jump": [" ", "z"],
    "interact": ["e"],
    "skipDialog": ["escape"],
    "attack": ["j", "x", "mouseleft"],
    "shoot": ["k", "c", "mouseright"],
    "aimUp": ["w", "arrowup"],
    "aimDown": ["s", "arrowdown"],
    "dash": ["shift"],
    "heal": ["l", "v"],
    "debugGrid": ["f1"],
    "debugHitbox": ["f2"],
}
UI_CONFIG = {
    "lives": {
        "icon": {"full": {"pose": ("icons.png", 0), "facing": 1}, "empty": {"pose": ("icons.png", 1), "facing": 1}},
        "x": -195.55555555555557,
        "y": 102.22222222222223,
        "gap": 1.7777777777777777,
        "displayLimit": 10,
    },
    "counter": {
        "icon": {"pose": ("tileset.png", 18), "facing": 1},
        "x": 171.85182222222224,
        "y": 102.22222222222223,
        "gap": 1.7777777777777777,
        "labelOffsetY": 0,
        "fontSize": 8.296266666666666,
    },
    "dialog": {
        "box": {"pose": ("dialog-styles.png", 0), "facing": 1},
        "indicator": {"pose": {"pose": ("placeholder-prompt.png", 0), "facing": 1}, "npc": {"offsetX": 0, "gap": 1.7777777777777777}, "exit": {"offsetX": 0, "gap": 0}},
        "textColor": "#3a2412",
        "y": 72.59262222222223,
        "textOffsetX": -82.96293333333332,
        "speakerOffsetY": 19.259288888888886,
        "messageOffsetY": 5.9259555555555545,
        "speakerFontSize": 8.88888888888889,
        "messageFontSize": 7.703733333333333,
        "npcIndicatorGap": 1.7777777777777777,
        "exitIndicatorGap": 0,
        "hintMarginX": 4.5926222222222215,
        "hintMarginY": 5.6296,
        "typeSpeed": 1.5,
        "talkSoundEvery": 6,
    },
    "ammo": {
        "x": -195.55555555555557,
        "y": 86.22222222222223,
        "gap": 1.7777777777777777,
        "height": 8.88888888888889,
        "displayLimit": 10,
    },
    "meter": {
        "x": -202.66666666666669,
        "y": 75.55555555555556,
        "width": 53.33333333333333,
        "height": 4.444444444444445,
    },
    "bossBar": {
        "y": 95.11111111111111,
        "width": 142.22222222222223,
        "height": 4.444444444444445,
        "labelGap": 2.6666666666666665,
        "fontSize": 7.111111111111111,
        "gap": 3.5555555555555554,
    },
    "fadeOverlay": {
        "pose": "fade-black.png",
        "facing": 1,
    },
    "playerIndicators": {},
    "font": "VT323",
}
SPRITES = {
    "default-ui-heart-frames.png": {"rows": 1, "cols": 2, "fps": 0},
    "dialog-styles.png": {"rows": 3, "cols": 2, "fps": 0},
    "fade-black.png": {"rows": 1, "cols": 1},
    "enemy-bullet.png": {"rows": 1, "cols": 1},
    "tileset.png": {"rows": 3, "cols": 8},
    "placeholder-characters.png": {"rows": 1, "cols": 6, "fps": 0},
    "placeholder-prompt.png": {"rows": 1, "cols": 1, "fps": 0},
    "placeholder-projectiles.png": {"rows": 1, "cols": 3, "fps": 0},
    "icons.png": {"rows": 1, "cols": 3},
    "slash.png": {"rows": 1, "cols": 1},
    "theHoodedOne-Sheet.png": {"rows": 1, "cols": 11},
    "background.png": {"rows": 1, "cols": 1},
}
SOUNDS = {
    "jump": {"file": "jump.mp3", "volume": 0.05},
    "hurt": {"file": "hurt.wav", "volume": 0.3},
    "death": {"file": "death.wav", "volume": 0.2},
    "unlock": {"file": "unlock.wav", "volume": 0.6, "cooldown": 30},
    "pickup": {"file": "beep.wav", "volume": 0.2},
    "collect": {"file": "pop.mp3", "volume": 0.2},
    "switch": {"file": "switch.wav", "volume": 0.4},
    "spring": {"file": "spring.mp3", "volume": 0.2},
    "goal": {"file": "tada.mp3", "volume": 0.2},
    "travel": {"file": "travel.wav", "volume": 0.2},
    "enemyhit": {"file": "enemy-hit.wav", "volume": 0.05},
    "shoot": {"file": "shoot.wav", "volume": 0.15},
    "dash": {"file": "dash.mp3", "volume": 0.2},
    "swing": {"file": "dash.mp3", "volume": 0.15},
    "heal": {"file": "unlock.wav", "volume": 0.3},
    "talk": {"file": "talk.wav", "volume": 0.02},
    "dropper": {"file": "dropper.wav", "volume": 0.3},
}
ROOM_MUSIC = {
    "A_title_screen": None,
    "DungeonStart": None,
    "Hallway1": None,
    "RoomSplit1": None,
    "Room4": None,
    "Room3": None,
    "DungeonDrop_DROP": None,
    "Cellar": None,
    "Trap1": None,
    "LowerPuzzle1": None,
    "Puzzle1part2": None,
    "Maze": None,
    "Turret1": None,
    "HoodedOneFight": None,
}
GAME_MUSIC = {
    "file": "DecayingWill.mp3",
    "volume": 0.35,
}
SCRIPT_ROOMS = ["A_title_screen"]

# Game content - choose the types used by the map and room scripts.
COLLECTIBLE_TYPES = {
    "collectible_placeholder_tileset_18": {"sprite": {"pose": ("tileset.png", 18), "facing": 1}, "counter": True},
    "collectible_placeholder_tileset_17": {"sprite": {"pose": ("tileset.png", 17), "facing": 1}, "effect": "unlock", "counter": False, "unlocks": "melee"},
    "placeholder_key": {"sprite": {"pose": ("tileset.png", 6), "facing": 1}, "counter": False},
    "character_4_drop": {"sprite": {"pose": ("icons.png", 0), "facing": 1}, "fullSprite": {"pose": ("icons.png", 0), "facing": 1}, "emptySprite": {"pose": ("default-ui-heart-frames.png", 1), "facing": 1}, "effect": "maxHealth", "counter": False},
}
HAZARD_TYPES = {
    "placeholder_spikes": {"sprite": {"pose": ("tileset.png", 4), "facing": 1}, "damage": 1},
}
EXIT_TYPES = {
    "placeholder_door": {"sprite": {"pose": ("tileset.png", 12), "facing": 1}},
}
BARRIER_TYPES = {
    "placeholder_gate": {"sprite": {"pose": ("tileset.png", 11), "facing": 1}},
}
SWITCH_TYPES = {
    "placeholder_lever": {"poses": {"off": {"pose": ("tileset.png", 9), "facing": 1}, "on": {"pose": ("tileset.png", 10), "facing": 1}}},
}
CLIMBABLE_TYPES = {}
BACKGROUND_TYPES = {
    "background_1": {"pose": "background.png", "facing": 1},
}
SIGN_TYPES = {
    "placeholder_sign": {"sprite": {"pose": ("tileset.png", 8), "facing": 1}},
}
ENEMY_TYPES = {
    "character_1": {"poses": {"idle": {"pose": ("placeholder-characters.png", 3), "facing": 1}}, "speed": 0.4444444444444444, "behavior": "stationary", "maxHealth": 3, "projectile": "character_1_projectile", "noticeRange": 384, "contactDamage": 1, "bulletDistance": 384},
    "character_2": {"poses": {"idle": {"pose": ("tileset.png", 11), "facing": 1}, "dropping": {"pose": ("tileset.png", 19), "facing": 1}}, "speed": 0.4444444444444444, "behavior": "dropper", "maxHealth": 1, "contactDamage": 2},
    "character_3": {"poses": {"idle": {"pose": {"sheet": "placeholder-characters.png", "start": 4, "end": 5, "fps": 3}, "facing": 1}}, "speed": 0.4444444444444444, "behavior": "flyer", "maxHealth": 3, "projectile": "character_3_projectile", "contactDamage": 1},
    "placeholder_enemy": {"poses": {"idle": {"pose": ("placeholder-characters.png", 0), "facing": 1}, "run": {"pose": {"sheet": "placeholder-characters.png", "start": 0, "end": 1, "fps": 3}, "facing": 1}, "jumpUp": {"pose": ("placeholder-characters.png", 0), "facing": 1}, "jumpDown": {"pose": ("placeholder-characters.png", 1), "facing": 1}}, "displayName": "Placeholder enemy", "behavior": "jumper", "speed": 0.4444444444444444, "maxHealth": 2, "contactDamage": 1},
    "character_4": {"poses": {"idle": {"pose": {"sheet": "theHoodedOne-Sheet.png", "start": 0, "end": 9, "fps": 8}, "facing": 1}}, "boss": True, "drop": "character_4_drop", "speed": 0.4444444444444444, "behavior": "scripted", "maxHealth": 1, "projectile": "character_4_projectile", "contactDamage": 1, "name": "Hooded One"},
}
NPC_TYPES = {
    "placeholder_npc": {"poses": {"idle": {"pose": ("placeholder-characters.png", 2), "facing": 1}}, "displayName": "Placeholder NPC", "behavior": "stationary"},
}
PROJECTILE_TYPES = {
    "character_3_projectile": {"sprite": {"pose": ("placeholder-projectiles.png", 0), "facing": 1}},
    "character_1_projectile": {"sprite": {"pose": ("enemy-bullet.png", 0), "facing": 1}},
    "character_4_projectile": {"sprite": {"pose": ("placeholder-projectiles.png", 1), "facing": 1}},
}
ENEMY_DEFAULTS = {
    "patrolRange": 33.33333333333333,
    "sensorSize": 2.6666666666666665,
    "senseAhead": 1.7777777777777777,
    "senseDown": 1.3333333333333333,
}
ENEMY_BEHAVIORS = {
    "patrol": {"senseAhead": 1.7777777777777777, "senseDown": 1.3333333333333333, "fallGravity": -0.23706666666666665, "maxFallSpeed": -4.7407111111111115},
    "stationary": {},
    "jumper": {"senseAhead": 1.7777777777777777, "senseDown": 1.3333333333333333, "jumpSpeed": 2.2222222222222223, "hopGravity": -0.13333333333333333, "hopPauseMax": 40, "jumpSquashX": 0.7, "jumpSquashY": 1.3, "landingSquashX": 1.3, "landingSquashY": 0.7, "squashEaseRate": 0.1, "maxFallSpeed": -4.7407111111111115},
    "flyer": {"senseAhead": 1.7777777777777777},
    "scripted": {"senseAhead": 1.7777777777777777, "senseDown": 1.3333333333333333, "hopGravity": -0.26666666666666666, "maxFallSpeed": -4.7407111111111115},
    "dropper": {"senseWidth": 0, "warnFrames": 12, "warnShake": 0.8888888888888888, "fallGravity": -0.23706666666666665, "maxFallSpeed": -4.7407111111111115, "riseSpeed": 0.5926222222222222, "landedPauseMax": 45, "topPauseMax": 30, "maxFall": 480},
}
PROJECTILE_CONFIG = {
    "playerSpeed": 2.962933333333333,
    "enemySpeed": 1.481511111111111,
    "damage": 1,
    "maxDistance": 266.66666666666663,
    "enemyFireInterval": 90,
    "enemyRange": 177.77777777777777,
}
ABILITIES_CONFIG = {
    "dash": {"enabled": 0, "style": "burst", "speed": 5.333333333333333, "frames": 12, "cooldown": 60, "charges": 1, "safe": 0, "requires": ""},
    "airJump": {"enabled": 0, "count": 1, "refill": "landing", "requires": ""},
    "wallJump": {"enabled": 1, "speed": 2.6666666666666665, "frames": 10, "requires": ""},
}
COMBAT_CONFIG = {
    "melee": 1,
    "stomp": 0,
    "meleeDamage": 1,
    "windupFrames": 4,
    "activeFrames": 6,
    "recoveryFrames": 10,
    "upAttack": 1,
    "downAttack": 1,
    "pogo": 1,
    "knockback": 10.666666666666666,
    "stagger": 12,
    "hitStop": 5,
    "shootCooldown": 15,
    "ammo": "unlimited",
    "maxAmmo": 3,
    "ammoRechargeFrames": 60,
    "shotCost": 3,
    "meter": 0,
    "meterMax": 9,
    "meterPerHit": 1,
    "heal": 0,
    "healCost": 3,
    "healFrames": 45,
    "meleeFromPickup": 1,
    "upDownFromPickup": 0,
    "shootFromPickup": 0,
    "dashFromPickup": 0,
    "airJumpFromPickup": 0,
    "wallJumpFromPickup": 1,
}

# Engine settings - change these only when you need different engine behavior.
ENGINE_DEFAULTS = {
    "viewport": {"width": 426.6666666666667, "height": 240},
    "tilemap": {"defaultCell": 16},
    "unit": 0.8888888888888888,
}
UNIT = ENGINE_DEFAULTS.get('unit', 1)
ENEMY_POSE_NAMES = ["idle", "run", "jumpUp", "jumpDown", "climb", "dropping", "attack", "strike"]
CAMERA_SHAKE_CONFIG = {
    "timer": 20,
    "distance": 1,
}

# Map type catalogs - edit these to customize the tiles used by the map.
PLATFORM_TYPES = {
    "decor_0": {"sprite": ("tileset.png", 0)},
    "decor_11": {"sprite": ("tileset.png", 11)},
}
DECOR_TYPES = {
    "decor_9": {"sprite": ("tileset.png", 9)},
    "decor_12": {"sprite": ("tileset.png", 12)},
}

# Every checkpointed global this project uses, with its type - set_global/
# get_global reject any name not listed here.
GLOBALS = {
    "hasKey": {"type": "bool", "default": False},
    "SWITCH_1": {"type": "bool", "default": False},
    "SWITCH_2": {"type": "bool", "default": False},
    "SWITCH_3": {"type": "bool", "default": False},
    "SWITCH_4": {"type": "bool", "default": False},
    "SWITCH_5": {"type": "bool", "default": False},
    "SWITCH_6": {"type": "bool", "default": False},
    "SWITCH_7": {"type": "bool", "default": False},
    "SWITCH_8": {"type": "bool", "default": False},
    "SWITCH_9": {"type": "bool", "default": False},
    "hasSword": {"type": "bool", "default": False},
    "SWITCH_10": {"type": "bool", "default": False},
    "SWITCH_11": {"type": "bool", "default": False},
    "SWITCH_12": {"type": "bool", "default": False},
    "SwordSwitch": {"type": "bool", "default": False},
    "HoodedPhase2": {"type": "bool", "default": False},
    "Puzzle2Switch": {"type": "bool", "default": False},
    "SectionOneUnlock": {"type": "bool", "default": False},
    "Puzzle2SwitchUnlock": {"type": "bool", "default": False},
    "interactSwitch_DROP": {"type": "bool", "default": False},
    "SwordSwitchActivated": {"type": "bool", "default": False},
}