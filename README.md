# Computer Vision Platformer

![Computer Vision Platformer architecture](https://raw.githubusercontent.com/IvanFuentesB/delete/main/assets/case-studies/diagrams/svg/sda_01_multidevice_architecture.svg)

A multi-device 2D platformer where real-world geometric shapes detected through a camera are turned into in-game objects and progression triggers. The project combines a Pygame platformer, an OpenCV shape-and-color pipeline, MQTT messaging, and serial-linked device workflows.

## System snapshot

- Stack: Python, Pygame, OpenCV, MQTT, Serial
- Game runtime: `640x480` at `60 FPS`
- Structure: `4 levels`, including a boss sequence
- Messaging: topic `cv/shapes` with `color`, `type`, and `pos`
- Vision goal: detect squares, triangles, and circles with color awareness
- Confirmation logic: LS mode with `CONFIRM_TIME = 0.5`

## Repository layout

- `game/game.py` - main Pygame loop and level progression
- `game/scripts/` - camera ingestion, tilemaps, entities, shapes, particles, and gameplay logic
- `camera/MQTT/` - OpenCV camera detection, MQTT publishing, and config
- `camera/Camera_get_shape/` - alternate camera-side detection path
- `Executable Programs/` - packaged builds and deployment notes
- `documentation/` - original course documentation PDF

## Architecture and flow

### Multi-device architecture

![Multi-device architecture](https://raw.githubusercontent.com/IvanFuentesB/delete/main/assets/case-studies/diagrams/svg/sda_01_multidevice_architecture.svg)

### OpenCV detection pipeline

![OpenCV detection pipeline](https://raw.githubusercontent.com/IvanFuentesB/delete/main/assets/case-studies/diagrams/svg/sda_02_cv_pipeline.svg)

### Game event flow

![Game event flow](https://raw.githubusercontent.com/IvanFuentesB/delete/main/assets/case-studies/diagrams/svg/sda_03_game_event_flow.svg)

## Real SDA documentation evidence

The original project PDF documents the system scope, camera requirements, and the course deliverables expected for the platformer.

### Project definition

![SDA project definition](https://raw.githubusercontent.com/IvanFuentesB/delete/main/assets/case-studies/sda-pdf-real-images/sda_pdf_03_project_definition.png)

### Camera requirements

![SDA camera requirements](https://raw.githubusercontent.com/IvanFuentesB/delete/main/assets/case-studies/sda-pdf-real-images/sda_pdf_06_camera_requirements.png)

### State diagram

![SDA state diagram](https://raw.githubusercontent.com/IvanFuentesB/delete/main/assets/case-studies/sda-pdf-real-images/sda_pdf_07_state_diagram.png)

### Class diagram

![SDA class diagram](https://raw.githubusercontent.com/IvanFuentesB/delete/main/assets/case-studies/sda-pdf-real-images/sda_pdf_08_class_diagram.png)

### Sequence diagram

![SDA sequence diagram](https://raw.githubusercontent.com/IvanFuentesB/delete/main/assets/case-studies/sda-pdf-real-images/sda_pdf_09_sequence_diagram.png)

### Game folder structure

![SDA game folder structure](https://raw.githubusercontent.com/IvanFuentesB/delete/main/assets/case-studies/sda-pdf-real-images/sda_pdf_10_game_folder_structure.png)

## Implementation notes

### Camera and detection

- The camera side tries DroidCam first and can fall back to other available cameras.
- The detection path uses HSV masks for red, green, blue, and yellow.
- A `5x5` morphology close/open pass cleans the combined mask.
- Minimum contour area is `1200`.
- The preprocessing path uses LAB conversion, CLAHE, and a sharpen step before contour analysis.
- Shapes are classified with `approxPolyDP(c, 0.025 * perimeter, True)` plus circularity checks.
- Circles use a circularity threshold above `0.83`; triangles use `3` vertices; quadrilaterals accept `4-6` vertices.
- Color assignment picks the strongest valid mask only when it covers at least `60%` of the candidate contour.

### Game integration

- The game reads `mqtt_ip` and `mqtt_port` from config files.
- The MQTT topic is `cv/shapes`.
- Payloads contain `color`, `type`, and `pos`.
- The game maps detected shapes into Pygame objects and flips `spawned_shape = True` when the right shape reaches the current level logic.
- The repo code shows `TOTAL_LEVELS = 4`, a `FRAMERATE = 60`, and a boss-timed sequence in the third gameplay stage.

### Course requirements reflected in the documentation

- Python, Pygame, OpenCV, MQTT, keyboard and mouse control
- At least `10` OOP classes plus state, class, and sequence diagrams
- A 2D platformer linked to an external camera
- Real geometric shape import into gameplay progression
- Shape and color detection for squares, triangles, and circles

## Run

Install the Python dependencies with Python 3.x:

```bash
pip install opencv-python paho-mqtt pygame pyserial
```

Start the game:

```bash
python game/game.py
```

Run the camera/vision side from the `camera/` folder.
