# Computer Vision Platformer

A multi-device platformer where real-world shapes detected via camera drive in-game progression.

## What it does
An OpenCV vision pipeline detects physical shapes through a camera feed (including an iPhone camera over the network) and uses MQTT + serial communication to drive game state across separate connected devices.

## Tech stack
Python · OpenCV · MQTT · Pygame · Serial

## Repository layout
- `game/` — Pygame platformer (entry point: `game/game.py`)
- `camera/` — OpenCV shape & color detection pipeline
- `Executable Programs/` — prebuilt executables
- `documentation/` — project docs

## Run
Install the Python dependencies (Python 3.x):

```
pip install opencv-python paho-mqtt pygame pyserial
```

Then start the game:

```
python game/game.py
```

The camera/vision side runs from the `camera/` folder.

## Notes
Built as a group project. Portfolio case study: coming soon.
