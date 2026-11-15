# Haven

Made in Studio. Studio writes every file here except this README each time you click
**Save to folder**, replacing any changes made here, so make lasting changes in Studio.

## Put the folder on GitHub

If you cloned this folder from GitHub, skip to the next section. Otherwise make an empty
repository on GitHub (no README), then run these in this folder, with your repository's address:

```
git init
git remote add origin https://github.com/YOUR-NAME/YOUR-REPOSITORY.git
git branch -M main
```

## Save a version

After each Save to folder, commit and push:

```
git add .
git commit -m "Describe what changed"
git push -u origin main
```

## Put the game on pixelpad.io

1. Make a new, empty game on pixelpad.io.
2. Upload every file in `art/` and `sound/` to it, keeping their names.
3. Export the game from pixelpad.io and save the file into this folder.
4. In this folder, run `python build_pp2d.py` with the exported file's name, for example
   `python build_pp2d.py exported.pp2d`. It puts this folder's code into `game.pp2d` and points
   its art and sound at your uploads.
5. Import `game.pp2d` into your pixelpad.io game.

If you change a `.py` file here, run `python build_pp2d.py exported.pp2d` again and import
`game.pp2d` again.

## What's here

- `game.pp2d`: the whole game, ready to import into pixelpad.io
- `build_pp2d.py`: puts the code and your uploads into `game.pp2d`
- `classes/`: one folder per class, with its `start.py` and `loop.py`
- `functions/`: the engine and the game's own function scripts
- `rooms/`: one folder per room, with its `start.py` and `loop.py`
- `art/` and `sound/`: the game's art and sound
