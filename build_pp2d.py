"""
Puts this folder's code, and the art and sound you uploaded to pixelpad.io, into game.pp2d.

    python build_pp2d.py                 copy the .py files' code into game.pp2d
    python build_pp2d.py exported.pp2d   also use the art and sound from your pixelpad.io export

Studio rewrites this file each time you click Save to folder.
"""

import json
import os
import re
import sys

GAME = "game.pp2d"
LAYOUT = json.loads("[{\"tree\":\"script\",\"path\":[\"Game\"],\"files\":{\"start\":\"classes/Game/start.py\",\"loop\":\"classes/Game/loop.py\"}},{\"tree\":\"script\",\"path\":[\"Player\"],\"files\":{\"start\":\"classes/Player/start.py\",\"loop\":\"classes/Player/loop.py\"}},{\"tree\":\"script\",\"path\":[\"Enemies\",\"Enemy\"],\"files\":{\"start\":\"classes/Enemies/Enemy/start.py\",\"loop\":\"classes/Enemies/Enemy/loop.py\"}},{\"tree\":\"script\",\"path\":[\"Enemies\",\"EnemyHitbox\"],\"files\":{\"start\":\"classes/Enemies/EnemyHitbox/start.py\",\"loop\":\"classes/Enemies/EnemyHitbox/loop.py\"}},{\"tree\":\"script\",\"path\":[\"Enemies\",\"EnemySensor\"],\"files\":{\"start\":\"classes/Enemies/EnemySensor/start.py\",\"loop\":\"classes/Enemies/EnemySensor/loop.py\"}},{\"tree\":\"script\",\"path\":[\"Environment\",\"Barrier\"],\"files\":{\"start\":\"classes/Environment/Barrier/start.py\",\"loop\":\"classes/Environment/Barrier/loop.py\"}},{\"tree\":\"script\",\"path\":[\"Environment\",\"Climbable\"],\"files\":{\"start\":\"classes/Environment/Climbable/start.py\",\"loop\":\"classes/Environment/Climbable/loop.py\"}},{\"tree\":\"script\",\"path\":[\"Environment\",\"EdgeWall\"],\"files\":{\"start\":\"classes/Environment/EdgeWall/start.py\",\"loop\":\"classes/Environment/EdgeWall/loop.py\"}},{\"tree\":\"script\",\"path\":[\"Environment\",\"Exit\"],\"files\":{\"start\":\"classes/Environment/Exit/start.py\",\"loop\":\"classes/Environment/Exit/loop.py\"}},{\"tree\":\"script\",\"path\":[\"Environment\",\"Hazard\"],\"files\":{\"start\":\"classes/Environment/Hazard/start.py\",\"loop\":\"classes/Environment/Hazard/loop.py\"}},{\"tree\":\"script\",\"path\":[\"Environment\",\"Platform\"],\"files\":{\"start\":\"classes/Environment/Platform/start.py\",\"loop\":\"classes/Environment/Platform/loop.py\"}},{\"tree\":\"script\",\"path\":[\"Environment\",\"Decor\"],\"files\":{\"start\":\"classes/Environment/Decor/start.py\",\"loop\":\"classes/Environment/Decor/loop.py\"}},{\"tree\":\"script\",\"path\":[\"Environment\",\"Switch\"],\"files\":{\"start\":\"classes/Environment/Switch/start.py\",\"loop\":\"classes/Environment/Switch/loop.py\"}},{\"tree\":\"script\",\"path\":[\"Pickups\",\"Collectible\"],\"files\":{\"start\":\"classes/Pickups/Collectible/start.py\",\"loop\":\"classes/Pickups/Collectible/loop.py\"}},{\"tree\":\"script\",\"path\":[\"Projectiles\",\"Projectile\"],\"files\":{\"start\":\"classes/Projectiles/Projectile/start.py\",\"loop\":\"classes/Projectiles/Projectile/loop.py\"}},{\"tree\":\"script\",\"path\":[\"Combat\",\"Strike\"],\"files\":{\"start\":\"classes/Combat/Strike/start.py\",\"loop\":\"classes/Combat/Strike/loop.py\"}},{\"tree\":\"script\",\"path\":[\"Combat\",\"StrikeHitbox\"],\"files\":{\"start\":\"classes/Combat/StrikeHitbox/start.py\",\"loop\":\"classes/Combat/StrikeHitbox/loop.py\"}},{\"tree\":\"script\",\"path\":[\"Story\",\"DialogBox\"],\"files\":{\"start\":\"classes/Story/DialogBox/start.py\",\"loop\":\"classes/Story/DialogBox/loop.py\"}},{\"tree\":\"script\",\"path\":[\"Story\",\"DialogPrompt\"],\"files\":{\"start\":\"classes/Story/DialogPrompt/start.py\",\"loop\":\"classes/Story/DialogPrompt/loop.py\"}},{\"tree\":\"script\",\"path\":[\"Story\",\"NPC\"],\"files\":{\"start\":\"classes/Story/NPC/start.py\",\"loop\":\"classes/Story/NPC/loop.py\"}},{\"tree\":\"script\",\"path\":[\"UI\",\"Counter\"],\"files\":{\"start\":\"classes/UI/Counter/start.py\",\"loop\":\"classes/UI/Counter/loop.py\"}},{\"tree\":\"script\",\"path\":[\"UI\",\"CounterBackdrop\"],\"files\":{\"start\":\"classes/UI/CounterBackdrop/start.py\",\"loop\":\"classes/UI/CounterBackdrop/loop.py\"}},{\"tree\":\"script\",\"path\":[\"UI\",\"LivesBackdrop\"],\"files\":{\"start\":\"classes/UI/LivesBackdrop/start.py\",\"loop\":\"classes/UI/LivesBackdrop/loop.py\"}},{\"tree\":\"script\",\"path\":[\"UI\",\"Life\"],\"files\":{\"start\":\"classes/UI/Life/start.py\",\"loop\":\"classes/UI/Life/loop.py\"}},{\"tree\":\"script\",\"path\":[\"UI\",\"PlayerIndicator\"],\"files\":{\"start\":\"classes/UI/PlayerIndicator/start.py\",\"loop\":\"classes/UI/PlayerIndicator/loop.py\"}},{\"tree\":\"script\",\"path\":[\"UI\",\"AmmoPip\"],\"files\":{\"start\":\"classes/UI/AmmoPip/start.py\",\"loop\":\"classes/UI/AmmoPip/loop.py\"}},{\"tree\":\"script\",\"path\":[\"UI\",\"MeterBar\"],\"files\":{\"start\":\"classes/UI/MeterBar/start.py\",\"loop\":\"classes/UI/MeterBar/loop.py\"}},{\"tree\":\"script\",\"path\":[\"UI\",\"HudRect\"],\"files\":{\"start\":\"classes/UI/HudRect/start.py\",\"loop\":\"classes/UI/HudRect/loop.py\"}},{\"tree\":\"script\",\"path\":[\"UI\",\"BossBar\"],\"files\":{\"start\":\"classes/UI/BossBar/start.py\",\"loop\":\"classes/UI/BossBar/loop.py\"}},{\"tree\":\"script\",\"path\":[\"Engine\",\"Background\"],\"files\":{\"start\":\"classes/Engine/Background/start.py\",\"loop\":\"classes/Engine/Background/loop.py\"}},{\"tree\":\"script\",\"path\":[\"Engine\",\"CameraShake\"],\"files\":{\"start\":\"classes/Engine/CameraShake/start.py\",\"loop\":\"classes/Engine/CameraShake/loop.py\"}},{\"tree\":\"script\",\"path\":[\"Engine\",\"FadeIn\"],\"files\":{\"start\":\"classes/Engine/FadeIn/start.py\",\"loop\":\"classes/Engine/FadeIn/loop.py\"}},{\"tree\":\"script\",\"path\":[\"Engine\",\"FadeOut\"],\"files\":{\"start\":\"classes/Engine/FadeOut/start.py\",\"loop\":\"classes/Engine/FadeOut/loop.py\"}},{\"tree\":\"script\",\"path\":[\"Engine\",\"PlayerHitbox\"],\"files\":{\"start\":\"classes/Engine/PlayerHitbox/start.py\",\"loop\":\"classes/Engine/PlayerHitbox/loop.py\"}},{\"tree\":\"room\",\"path\":[\"A_title_screen\"],\"files\":{\"start\":\"rooms/A_title_screen/start.py\",\"loop\":\"rooms/A_title_screen/loop.py\"}},{\"tree\":\"room\",\"path\":[\"DungeonStart\"],\"files\":{\"start\":\"rooms/DungeonStart/start.py\",\"loop\":\"rooms/DungeonStart/loop.py\"}},{\"tree\":\"room\",\"path\":[\"Hallway1\"],\"files\":{\"start\":\"rooms/Hallway1/start.py\",\"loop\":\"rooms/Hallway1/loop.py\"}},{\"tree\":\"room\",\"path\":[\"RoomSplit1\"],\"files\":{\"start\":\"rooms/RoomSplit1/start.py\",\"loop\":\"rooms/RoomSplit1/loop.py\"}},{\"tree\":\"room\",\"path\":[\"Room4\"],\"files\":{\"start\":\"rooms/Room4/start.py\",\"loop\":\"rooms/Room4/loop.py\"}},{\"tree\":\"room\",\"path\":[\"Room3\"],\"files\":{\"start\":\"rooms/Room3/start.py\",\"loop\":\"rooms/Room3/loop.py\"}},{\"tree\":\"room\",\"path\":[\"DungeonDrop_DROP\"],\"files\":{\"start\":\"rooms/DungeonDrop_DROP/start.py\",\"loop\":\"rooms/DungeonDrop_DROP/loop.py\"}},{\"tree\":\"room\",\"path\":[\"Cellar\"],\"files\":{\"start\":\"rooms/Cellar/start.py\",\"loop\":\"rooms/Cellar/loop.py\"}},{\"tree\":\"room\",\"path\":[\"Trap1\"],\"files\":{\"start\":\"rooms/Trap1/start.py\",\"loop\":\"rooms/Trap1/loop.py\"}},{\"tree\":\"room\",\"path\":[\"LowerPuzzle1\"],\"files\":{\"start\":\"rooms/LowerPuzzle1/start.py\",\"loop\":\"rooms/LowerPuzzle1/loop.py\"}},{\"tree\":\"room\",\"path\":[\"Puzzle1part2\"],\"files\":{\"start\":\"rooms/Puzzle1part2/start.py\",\"loop\":\"rooms/Puzzle1part2/loop.py\"}},{\"tree\":\"room\",\"path\":[\"Maze\"],\"files\":{\"start\":\"rooms/Maze/start.py\",\"loop\":\"rooms/Maze/loop.py\"}},{\"tree\":\"room\",\"path\":[\"Turret1\"],\"files\":{\"start\":\"rooms/Turret1/start.py\",\"loop\":\"rooms/Turret1/loop.py\"}},{\"tree\":\"room\",\"path\":[\"HoodedOneFight\"],\"files\":{\"start\":\"rooms/HoodedOneFight/start.py\",\"loop\":\"rooms/HoodedOneFight/loop.py\"}},{\"tree\":\"room\",\"path\":[\"Ending\"],\"files\":{\"start\":\"rooms/Ending/start.py\",\"loop\":\"rooms/Ending/loop.py\"}},{\"tree\":\"room\",\"path\":[\"tower\"],\"files\":{\"start\":\"rooms/tower/start.py\",\"loop\":\"rooms/tower/loop.py\"}},{\"tree\":\"room\",\"path\":[\"towerLore\"],\"files\":{\"start\":\"rooms/towerLore/start.py\",\"loop\":\"rooms/towerLore/loop.py\"}},{\"tree\":\"function\",\"path\":[\"game-toolkit\",\"placement.py\"],\"files\":{\"head\":\"functions/game-toolkit/placement.py\"}},{\"tree\":\"function\",\"path\":[\"game-toolkit\",\"audio.py\"],\"files\":{\"head\":\"functions/game-toolkit/audio.py\"}},{\"tree\":\"function\",\"path\":[\"game-toolkit\",\"camera.py\"],\"files\":{\"head\":\"functions/game-toolkit/camera.py\"}},{\"tree\":\"function\",\"path\":[\"game-toolkit\",\"dialog.py\"],\"files\":{\"head\":\"functions/game-toolkit/dialog.py\"}},{\"tree\":\"function\",\"path\":[\"game-toolkit\",\"sprites.py\"],\"files\":{\"head\":\"functions/game-toolkit/sprites.py\"}},{\"tree\":\"function\",\"path\":[\"game-toolkit\",\"tilemap.py\"],\"files\":{\"head\":\"functions/game-toolkit/tilemap.py\"}},{\"tree\":\"function\",\"path\":[\"game-toolkit\",\"controls.py\"],\"files\":{\"head\":\"functions/game-toolkit/controls.py\"}},{\"tree\":\"function\",\"path\":[\"game-toolkit\",\"player.py\"],\"files\":{\"head\":\"functions/game-toolkit/player.py\"}},{\"tree\":\"function\",\"path\":[\"game-toolkit\",\"abilities.py\"],\"files\":{\"head\":\"functions/game-toolkit/abilities.py\"}},{\"tree\":\"function\",\"path\":[\"game-toolkit\",\"combat.py\"],\"files\":{\"head\":\"functions/game-toolkit/combat.py\"}},{\"tree\":\"function\",\"path\":[\"game-toolkit\",\"terrain.py\"],\"files\":{\"head\":\"functions/game-toolkit/terrain.py\"}},{\"tree\":\"function\",\"path\":[\"game-toolkit\",\"progression.py\"],\"files\":{\"head\":\"functions/game-toolkit/progression.py\"}},{\"tree\":\"function\",\"path\":[\"game-toolkit\",\"interactables.py\"],\"files\":{\"head\":\"functions/game-toolkit/interactables.py\"}},{\"tree\":\"function\",\"path\":[\"game-toolkit\",\"characters.py\"],\"files\":{\"head\":\"functions/game-toolkit/characters.py\"}},{\"tree\":\"function\",\"path\":[\"game-toolkit\",\"grid.py\"],\"files\":{\"head\":\"functions/game-toolkit/grid.py\"}},{\"tree\":\"function\",\"path\":[\"config.py\"],\"files\":{\"head\":\"functions/config.py\"}},{\"tree\":\"function\",\"path\":[\"enemy_code.py\"],\"files\":{\"head\":\"functions/enemy_code.py\"}},{\"tree\":\"function\",\"path\":[\"maps.py\"],\"files\":{\"head\":\"functions/maps.py\"}}]")


def fail(message):
    print(message)
    sys.exit(1)


def read_json(path):
    try:
        with open(path, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        fail(f"Couldn't find {path}.")
    except ValueError:
        fail(f"{path} isn't a pixelpad.io game file.")


def find(tree, path):
    for index, name in enumerate(path):
        match = None
        for entry in tree if isinstance(tree, list) else []:
            if isinstance(entry, dict) and name in entry:
                match = entry[name]
                break
        if match is None:
            return None
        if index < len(path) - 1:
            tree = match
        else:
            return match if isinstance(match, dict) else None
    return None


def walk_files(tree, visit):
    for entry in tree if isinstance(tree, list) else []:
        if not isinstance(entry, dict):
            continue
        for name, value in entry.items():
            if isinstance(value, list):
                walk_files(value, visit)
            elif isinstance(value, dict) and isinstance(value.get("uri"), str) and value["uri"]:
                visit(name, value)


def match_key(name):
    stem = name.rsplit(".", 1)[0] if "." in name[1:] else name
    return re.sub(r"[^A-Za-z0-9]", "_", stem).lower()


def put_code(game):
    missing = []
    for item in LAYOUT:
        entry = find(game["pythonAssets"].get(item["tree"]), item["path"])
        if entry is None:
            fail("game.pp2d doesn't match this folder. Click Save to folder in Studio, then run this again.")
        for field, path in item["files"].items():
            try:
                with open(path, encoding="utf-8", newline="") as file:
                    entry[field] = file.read()
            except FileNotFoundError:
                missing.append(path)
    if missing:
        fail("These code files are missing:\n  " + "\n  ".join(missing))


def put_uploads(game, exported):
    uploads = {}
    for kind in ("texture", "sound"):
        found = {}
        walk_files(exported.get("pythonAssets", {}).get(kind), lambda name, data: found.setdefault(match_key(name), []).append(data["uri"]))
        uploads[kind] = found
    not_uploaded = []
    unclear = []

    def swap(kind):
        def visit(name, data):
            uris = uploads[kind].get(match_key(name), [])
            if len(uris) == 1:
                data["uri"] = uris[0]
            elif uris:
                unclear.append(name)
            else:
                not_uploaded.append(name)
        return visit

    for kind in ("texture", "sound"):
        walk_files(game["pythonAssets"].get(kind), swap(kind))
    return not_uploaded, unclear


def main():
    if len(sys.argv) > 2:
        fail(__doc__)
    if not os.path.exists(GAME):
        fail("Run this from your game's folder, the one with game.pp2d in it.")
    game = read_json(GAME)
    put_code(game)
    not_uploaded, unclear = [], []
    if len(sys.argv) == 2:
        exported = read_json(sys.argv[1])
        if not isinstance(exported, dict) or not isinstance(exported.get("pythonAssets"), dict):
            fail(f"{sys.argv[1]} isn't a pixelpad.io game file.")
        not_uploaded, unclear = put_uploads(game, exported)
    with open(GAME, "w", encoding="utf-8", newline="\n") as file:
        file.write(json.dumps(game, indent=2, ensure_ascii=False) + "\n")
    print("Updated game.pp2d. Import it into your pixelpad.io game.")
    if not_uploaded:
        print("\nThese aren't in your export, so they keep their old address:\n  " + "\n  ".join(not_uploaded))
    if unclear:
        print("\nMore than one upload matches these names, so they keep their old address:\n  " + "\n  ".join(unclear))


main()
