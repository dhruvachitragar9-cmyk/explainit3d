"""
ExplainIt3D — Interactive 3D Model Viewer with Part Annotations

Rotate a 3D model in the browser (it also spins slowly on its own),
tap the labeled dots on it, and see detailed information about that
part (material, function, notes).

This version embeds Google's <model-viewer> web component directly,
which gives us auto-rotate and full control over hotspots — no extra
add-on package needed.
"""

import streamlit as st
import streamlit.components.v1 as components
import json

# ---------------------------------------------------------------
# 1. PICK A MODEL
# ---------------------------------------------------------------
# Swap "My Laptop"'s URL for your own model whenever you re-upload
# a new .glb to GitHub — just update the link below.
SAMPLE_MODELS = {
    "My Laptop": "https://raw.githubusercontent.com/dhruvachitragar9-cmyk/explainit3d/main/laptop.glb",
    "Engine": "https://alteirac.com/models/engine/scene.gltf",
    "Helmet": "https://alteirac.com/models/helmet/scene.gltf",
    "Turbine": "https://alteirac.com/models/turbine/scene.gltf",
}

# ---------------------------------------------------------------
# 2. YOUR PART DATA + HOTSPOT POSITIONS, PER MODEL
# ---------------------------------------------------------------
# Each hotspot needs a "position" (x y z, as a single space-separated
# string) and a "normal" (direction it faces, same format). Once you
# know where you want a label on YOUR laptop, you place it here.
# (Rough starting guesses below — nudge the numbers to match your
# actual model; see the README for the placement trick.)
MODEL_DATA = {
    "My Laptop": {
        "Screen": {
            "position": "0 0.55 -0.05",
            "normal": "0 0 1",
            "material": "LCD panel with glass/plastic casing",
            "function": "Displays visual output to the user.",
            "notes": "Fill in the real details for your laptop here.",
        },
        "Keyboard": {
            "position": "0 0.05 0.1",
            "normal": "0 1 0",
            "material": "Plastic keys over a membrane/scissor mechanism",
            "function": "Primary text input device.",
            "notes": "Fill in the real details for your laptop here.",
        },
        "Trackpad": {
            "position": "0 0.02 0.3",
            "normal": "0 1 0",
            "material": "Glass or plastic surface over touch sensors",
            "function": "Cursor control and gestures.",
            "notes": "Fill in the real details for your laptop here.",
        },
    },
    "Engine": {
        "Engine Block": {
            "position": "0.05 0.35 0.15",
            "normal": "0 0 1",
            "material": "Cast Aluminum Alloy",
            "function": "Houses the cylinders and core moving components.",
            "notes": "Chosen for its strength-to-weight ratio and heat dissipation.",
        },
        "Exhaust Manifold": {
            "position": "-0.25 0.2 0.05",
            "normal": "-1 0 0",
            "material": "Stainless Steel",
            "function": "Channels exhaust gases away from the cylinders.",
            "notes": "Resistant to high temperatures and corrosion.",
        },
        "Intake Valve": {
            "position": "0.15 0.45 -0.1",
            "normal": "0 1 0",
            "material": "Forged Steel",
            "function": "Controls airflow into the combustion chamber.",
            "notes": "Must withstand repeated high-speed mechanical stress.",
        },
    },
}

# ---------------------------------------------------------------
# 3. PAGE SETUP
# ---------------------------------------------------------------
st.set_page_config(page_title="ExplainIt3D", layout="wide")

st.title("🔍 ExplainIt3D")
st.caption("Rotate the model, tap a labeled point, and see the details.")

model_choice = st.selectbox("Model:", list(SAMPLE_MODELS.keys()), index=0)
model_url = SAMPLE_MODELS[model_choice]
parts = MODEL_DATA.get(model_choice, {})

if not parts:
    st.info(
        "No hotspots are set up for this model yet — add entries to "
        "MODEL_DATA in app.py."
    )

# ---------------------------------------------------------------
# 4. BUILD THE HOTSPOT BUTTONS + INFO DATA
# ---------------------------------------------------------------
hotspot_html = ""
for name, data in parts.items():
    hotspot_html += (
        f'<button class="Hotspot" slot="hotspot-{name}" '
        f'data-position="{data["position"]}" data-normal="{data["normal"]}" '
        f'data-name="{name}" onclick="showInfo(this)"></button>\n'
    )

# The part details, ready to drop straight into the page's JavaScript
info_json = json.dumps(
    {name: {"material": d["material"], "function": d["function"], "notes": d["notes"]}
     for name, d in parts.items()}
)

# ---------------------------------------------------------------
# 5. THE FULL EMBEDDED PAGE (model-viewer + auto-rotate + hotspots)
# ---------------------------------------------------------------
html = f"""
<script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
<style>
  body {{ margin: 0; font-family: sans-serif; }}
  model-viewer {{
    width: 100%;
    height: 480px;
    background-color: #fafafa;
    border-radius: 8px;
  }}
  .Hotspot {{
    width: 22px;
    height: 22px;
    border-radius: 50%;
    border: 2px solid white;
    background: #4361ee;
    cursor: pointer;
    box-shadow: 0 0 6px rgba(0,0,0,0.4);
  }}
  #info-box {{
    display: none;
    margin-top: 14px;
    margin-bottom: 20px;
    padding: 16px 20px;
    border-radius: 8px;
    background: #1e2530;
    color: #eee;
    font-size: 15px;
    line-height: 1.6;
    min-height: 90px;
  }}
  #info-box h3 {{ margin: 0 0 8px 0; }}
</style>

<model-viewer
  src="{model_url}"
  camera-controls
  auto-rotate
  rotation-per-second="18deg"
  shadow-intensity="1"
  exposure="1"
  environment-image="neutral"
>
  {hotspot_html}
</model-viewer>

<div id="info-box"></div>

<script>
  const partInfo = {info_json};

  function showInfo(el) {{
    const name = el.getAttribute('data-name');
    const info = partInfo[name];
    const box = document.getElementById('info-box');
    if (!info) return;
    box.style.display = 'block';
    box.innerHTML =
      '<h3>📌 ' + name + '</h3>' +
      '<b>Material:</b> ' + info.material + '<br>' +
      '<b>Function:</b> ' + info.function + '<br>' +
      '<b>Notes:</b> ' + info.notes;
  }}
</script>
"""

components.html(html, height=650, scrolling=False)
