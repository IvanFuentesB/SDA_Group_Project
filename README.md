# Computer Vision Platformer

<p align="center">
  <img src="https://raw.githubusercontent.com/IvanFuentesB/delete/main/assets/case-studies/diagrams/svg/sda_01_multidevice_architecture.svg" alt="Computer Vision Platformer architecture" width="100%" />
</p>

A multi-device 2D platformer where real-world geometric shapes detected through a camera are converted into in-game objects and progression triggers. The project combines a Pygame platformer, an OpenCV shape-and-color pipeline, MQTT messaging, and serial-linked device workflows.

## System at a glance

| Area | Details |
| --- | --- |
| Stack | Python, Pygame, OpenCV, MQTT, Serial |
| Game runtime | `640x480` at `60 FPS` |
| Structure | `4 levels`, including a boss sequence |
| Messaging | Topic `cv/shapes` with `color`, `type`, and `pos` |
| Vision target | Detect squares, triangles, and circles with color awareness |
| Confirmation logic | LS mode with `CONFIRM_TIME = 0.5` |

## Why the project is interesting

1. A physical object outside the game becomes a gameplay input inside the game loop.
2. The camera pipeline does more than contour detection: it handles color, validation, timing, and messaging.
3. The game side interprets those detections as actual progression logic rather than a disconnected demo overlay.

## Visual system overview

<table>
  <tr>
    <td width="50%" valign="top">
      <img src="https://raw.githubusercontent.com/IvanFuentesB/delete/main/assets/case-studies/diagrams/svg/sda_02_cv_pipeline.svg" alt="OpenCV detection pipeline" width="100%" /><br/>
      <strong>OpenCV detection pipeline</strong><br/>
      LAB + CLAHE preprocessing, HSV masks, morphology, contour filtering, shape classification, and MQTT publication.
    </td>
    <td width="50%" valign="top">
      <img src="https://raw.githubusercontent.com/IvanFuentesB/delete/main/assets/case-studies/diagrams/svg/sda_03_game_event_flow.svg" alt="Game event flow" width="100%" /><br/>
      <strong>Game event flow</strong><br/>
      MQTT messages are converted into Pygame objects and matched against level-specific requirements.
    </td>
  </tr>
</table>

## Confirmed implementation details

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

<details>
<summary><strong>Original project documentation proof pack</strong> — requirements, UML, sequence, and folder structure</summary>

<br/>

<table>
  <tr>
    <td width="50%" valign="top">
      <img src="https://raw.githubusercontent.com/IvanFuentesB/delete/main/assets/case-studies/sda-pdf-real-images/sda_pdf_03_project_definition.png" alt="SDA project definition" width="100%" /><br/>
      <strong>Project definition</strong><br/>
      External-camera gameplay goal and shape-import mechanic from the course document.
    </td>
    <td width="50%" valign="top">
      <img src="https://raw.githubusercontent.com/IvanFuentesB/delete/main/assets/case-studies/sda-pdf-real-images/sda_pdf_06_camera_requirements.png" alt="SDA camera requirements" width="100%" /><br/>
      <strong>Camera requirements</strong><br/>
      Course requirements for shape type and color detection.
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <img src="https://raw.githubusercontent.com/IvanFuentesB/delete/main/assets/case-studies/sda-pdf-real-images/sda_pdf_07_state_diagram.png" alt="SDA state diagram" width="100%" /><br/>
      <strong>State diagram</strong><br/>
      Original state transitions for gameplay and camera-linked flow.
    </td>
    <td width="50%" valign="top">
      <img src="https://raw.githubusercontent.com/IvanFuentesB/delete/main/assets/case-studies/sda-pdf-real-images/sda_pdf_08_class_diagram.png" alt="SDA class diagram" width="100%" /><br/>
      <strong>Class diagram</strong><br/>
      OOP structure supporting the game and its entities.
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <img src="https://raw.githubusercontent.com/IvanFuentesB/delete/main/assets/case-studies/sda-pdf-real-images/sda_pdf_09_sequence_diagram.png" alt="SDA sequence diagram" width="100%" /><br/>
      <strong>Sequence diagram</strong><br/>
      Messaging and interaction flow across camera, broker, and game logic.
    </td>
    <td width="50%" valign="top">
      <img src="https://raw.githubusercontent.com/IvanFuentesB/delete/main/assets/case-studies/sda-pdf-real-images/sda_pdf_10_game_folder_structure.png" alt="SDA game folder structure" width="100%" /><br/>
      <strong>Game folder structure</strong><br/>
      Supporting evidence for the actual project layout delivered in the course repo.
    </td>
  </tr>
</table>

</details>

## Repository layout

- `game/game.py` - main Pygame loop and level progression
- `game/scripts/` - camera ingestion, tilemaps, entities, shapes, particles, and gameplay logic
- `camera/MQTT/` - OpenCV camera detection, MQTT publishing, and config
- `camera/Camera_get_shape/` - alternate camera-side detection path
- `Executable Programs/` - packaged builds and deployment notes
- `documentation/` - original course documentation PDF

## Run

Install the Python dependencies with Python 3.x:

```bash
pip install opencv-python paho-mqtt pygame pyserial
```

Start the game:

```bash
python game/game.py
```

Run the camera or vision side from the `camera/` folder.
