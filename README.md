# ExplainIt3D

An interactive 3D model viewer — rotate the model, tap labeled points on
it, and see details (material, function, notes) about that part.

Built with **Streamlit** (Python), so the whole app is one Python file.

## How to run it (you already have Python + VS Code)

1. Open this folder in VS Code.
2. Open a terminal in VS Code (Terminal > New Terminal).
3. Install the two packages this app needs (one-time):
   ```
   pip install streamlit streamlit-3d
   ```
4. Run the app:
   ```
   streamlit run app.py
   ```
5. A browser tab opens automatically at `http://localhost:8501` showing
   the app. If it doesn't open automatically, click the "Local URL"
   link shown in the terminal.

To stop the app, go back to the terminal and press `Ctrl+C`.

## How to use it
- Rotate: click and drag on the model
- Zoom: scroll on the model
- Tap any labeled dot on the model to see its info appear below

## Project structure
- `app.py` — the whole app: model setup, part info data, and the page
- `PART_INFO` (inside app.py) — this is your "database." Add/edit
  entries here for each part of your object.
- `ENGINE_HOTSPOTS` (inside app.py) — the dot positions on the model.
  Each one needs a `description` that matches a key in `PART_INFO`.

## Swapping in your own prototype (next step, once you have a 3D file)

Right now the app uses a free sample "Engine" model so you can see
everything working immediately. To use your own prototype:

1. **Get a 3D file of your object** (`.glb` or `.gltf` format). Two
   common ways:
   - **3D scan it**: apps like Polycam or Scaniverse (free, iPhone/
     Android) let you scan a real object with your phone camera and
     export a `.glb` file.
   - **Model it from scratch**: Blender (free) if you want to build
     it by hand, especially for simpler geometric shapes.
2. Put the exported file in this project folder (e.g. `my_model.glb`).
3. In `app.py`, add it to `SAMPLE_MODELS`, e.g.:
   ```python
   "My Prototype": "my_model.glb",
   ```
4. Run the app, right-click on your model where you want a label to
   place a hotspot (this is a built-in feature of the 3D component),
   note the position values it gives you, and add them to a new
   hotspot list like `ENGINE_HOTSPOTS`.
5. Update `PART_INFO` with real details about your actual parts.

## For your project report
**Problem statement:** Understanding a physical prototype's design —
materials, components, and how parts function — usually needs
physical access or static documents that can't show spatial detail.
ExplainIt3D solves this with an interactive 3D viewer where tapping
any part instantly shows its material and function, making design
communication clearer without the physical object present.

**Tech stack:** Python, Streamlit, streamlit-3d (wraps Google's
model-viewer web component), glTF/GLB 3D model format.
