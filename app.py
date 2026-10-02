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

uploaded_file = st.file_uploader(
    "Or upload your own .glb file to preview it (temporary — not saved permanently)",
    type=["glb"],
)

if uploaded_file is not None:
    import base64
    file_bytes = uploaded_file.getvalue()
    b64 = base64.b64encode(file_bytes).decode("utf-8")
    model_url = f"data:model/gltf-binary;base64,{b64}"
    model_choice = "Uploaded File"
    st.caption(f"Previewing: {uploaded_file.name} ({len(file_bytes) / 1_000_000:.1f} MB)")
else:
    model_choice = st.selectbox("Model:", list(SAMPLE_MODELS.keys()), index=0)
    model_url = SAMPLE_MODELS[model_choice]

# User-added hotspots are kept here so you don't have to touch the
# code to add one — they last as long as the app is running.
if "custom_hotspots" not in st.session_state:
    st.session_state.custom_hotspots = {}
st.session_state.custom_hotspots.setdefault(model_choice, {})

built_in = MODEL_DATA.get(model_choice, {})
custom = st.session_state.custom_hotspots[model_choice]
parts = {**built_in, **custom}

find_mode = st.checkbox(
    "🎯 Placement mode — click the model to get coordinates for a new/moved hotspot"
)

if not parts:
    st.info(
        "No hotspots are set up for this model yet — add one below, or "
        "add entries to MODEL_DATA in app.py."
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

# The part details, ready to drop straight into the page's JavaScript.
# Built-in parts have material/function/notes; custom ones added via
# the form below just have a single free-text explanation — both get
# turned into one ready-to-show HTML snippet here.
info_data = {}
for name, d in parts.items():
    if "explanation" in d:
        info_data[name] = d["explanation"].replace("\n", "<br>")
    else:
        info_data[name] = (
            f"<b>Material:</b> {d['material']}<br>"
            f"<b>Function:</b> {d['function']}<br>"
            f"<b>Notes:</b> {d['notes']}"
        )
info_json = json.dumps(info_data)

# ---------------------------------------------------------------
# 5. THE FULL EMBEDDED PAGE (model-viewer + auto-rotate + hotspots)
# ---------------------------------------------------------------
html = f"""
<script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
<style>
  body {{ margin: 0; font-family: sans-serif; }}
  model-viewer {{
    width: 100%;
    height: 420px;
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
  #coord-box {{
    display: none;
    margin-top: 14px;
    padding: 16px 20px;
    border-radius: 8px;
    background: #2d1e30;
    color: #f0e6ff;
    font-size: 14px;
    font-family: monospace;
    white-space: pre-wrap;
  }}
</style>

<model-viewer
  id="mv"
  src="{model_url}"
  camera-controls
  auto-rotate
  rotation-per-second="18deg"
  shadow-intensity="1"
  exposure="1"
  environment-image="neutral"
  camera-orbit="auto auto 65%"
  interaction-prompt="none"
>
  {hotspot_html}
</model-viewer>

<div id="info-box"></div>
<div id="coord-box"></div>

<script>
  const partInfo = {info_json};
  const findMode = {str(find_mode).lower()};

  function showInfo(el) {{
    const name = el.getAttribute('data-name');
    const html = partInfo[name];
    const box = document.getElementById('info-box');
    if (!html) return;
    box.style.display = 'block';
    box.innerHTML = '<h3>📌 ' + name + '</h3>' + html;
  }}

  if (findMode) {{
    const mv = document.getElementById('mv');
    mv.addEventListener('click', (event) => {{
      const rect = mv.getBoundingClientRect();
      const hit = mv.positionAndNormalFromPoint(
        event.clientX - rect.left, event.clientY - rect.top
      );
      if (!hit) return;
      const p = hit.position;
      const n = hit.normal;
      const box = document.getElementById('coord-box');
      box.style.display = 'block';
      box.innerText =
        'Copy these into MODEL_DATA in app.py:\\n\\n' +
        'position: "' + p.x.toFixed(3) + ' ' + p.y.toFixed(3) + ' ' + p.z.toFixed(3) + '"\\n' +
        'normal:   "' + n.x.toFixed(3) + ' ' + n.y.toFixed(3) + ' ' + n.z.toFixed(3) + '"';
    }});
  }}
</script>
"""

components.html(html, height=780, scrolling=True)

# ---------------------------------------------------------------
# 6. FORM TO ADD A NEW HOTSPOT (no code editing needed)
# ---------------------------------------------------------------
st.divider()
st.subheader("➕ Add a hotspot")
st.caption(
    "Turn on Placement mode above, click the spot on the model, then "
    "copy the position/normal numbers it shows into the boxes below."
)

with st.form("add_hotspot_form", clear_on_submit=True):
    new_name = st.text_input("Part name (e.g. Charging Port)")
    new_explanation = st.text_area(
        "Explanation (material, function, whatever you want to say about it)"
    )
    col1, col2 = st.columns(2)
    with col1:
        pos_x = st.number_input("Position X", value=0.0, format="%.3f")
        pos_y = st.number_input("Position Y", value=0.0, format="%.3f")
        pos_z = st.number_input("Position Z", value=0.0, format="%.3f")
    with col2:
        norm_x = st.number_input("Normal X", value=0.0, format="%.3f")
        norm_y = st.number_input("Normal Y", value=1.0, format="%.3f")
        norm_z = st.number_input("Normal Z", value=0.0, format="%.3f")

    submitted = st.form_submit_button("Add Hotspot")
    if submitted:
        if not new_name.strip():
            st.warning("Give the part a name first.")
        else:
            st.session_state.custom_hotspots[model_choice][new_name.strip()] = {
                "position": f"{pos_x} {pos_y} {pos_z}",
                "normal": f"{norm_x} {norm_y} {norm_z}",
                "explanation": new_explanation.strip() or "No explanation added yet.",
            }
            st.success(f"Added '{new_name.strip()}' — scroll up to see it on the model.")
            st.rerun()

if st.session_state.custom_hotspots[model_choice]:
    st.caption("Hotspots you've added so far:")
    for name in st.session_state.custom_hotspots[model_choice]:
        c1, c2 = st.columns([5, 1])
        c1.write(f"• {name}")
        if c2.button("Remove", key=f"remove_{model_choice}_{name}"):
            del st.session_state.custom_hotspots[model_choice][name]
            st.rerun()
