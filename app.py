"""
ExplainIt3D — Interactive 3D Model Viewer with Part Annotations

Rotate a 3D model in the browser (it also spins slowly on its own),
tap the labeled dots on it, and see detailed information about that
part (material, function, notes) — with a highlight/zoom effect,
voice narration, dark/light theme, a sidebar part list, an "explode"
view, a reset-camera button, and PDF export of the part info.
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import base64
import io

try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False

# ---------------------------------------------------------------
# 1. PICK A MODEL
# ---------------------------------------------------------------
SAMPLE_MODELS = {
    "My Laptop": "https://raw.githubusercontent.com/dhruvachitragar9-cmyk/explainit3d/main/laptop.glb",
    "Engine": "https://alteirac.com/models/engine/scene.gltf",
    "Helmet": "https://alteirac.com/models/helmet/scene.gltf",
    "Turbine": "https://alteirac.com/models/turbine/scene.gltf",
}

# ---------------------------------------------------------------
# 2. YOUR PART DATA + HOTSPOT POSITIONS, PER MODEL
# ---------------------------------------------------------------
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

# --- Trim Streamlit's default top padding ---
st.markdown(
    """
    <style>
        .block-container { padding-top: 1.2rem; padding-bottom: 1rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Session state defaults ---
if "custom_hotspots" not in st.session_state:
    st.session_state.custom_hotspots = {}
if "scale_notes" not in st.session_state:
    st.session_state.scale_notes = {}
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"
if "selected_hotspot" not in st.session_state:
    st.session_state.selected_hotspot = None

# --- Sidebar: theme + part list ---
st.sidebar.header("⚙️ Settings")
st.session_state.theme = st.sidebar.radio(
    "Theme", ["Dark", "Light"], index=0 if st.session_state.theme == "Dark" else 1
)

st.title("🔍 ExplainIt3D")
st.caption("Rotate the model, tap a labeled point, and see the details.")

uploaded_file = st.file_uploader(
    "Or upload your own .glb file to preview it (temporary — not saved permanently)",
    type=["glb"],
)

if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    b64 = base64.b64encode(file_bytes).decode("utf-8")
    model_url = f"data:model/gltf-binary;base64,{b64}"
    model_choice = "Uploaded File"
    st.caption(f"Previewing: {uploaded_file.name} ({len(file_bytes) / 1_000_000:.1f} MB)")
else:
    model_choice = st.selectbox("Model:", list(SAMPLE_MODELS.keys()), index=0)
    model_url = SAMPLE_MODELS[model_choice]

st.session_state.custom_hotspots.setdefault(model_choice, {})
built_in = MODEL_DATA.get(model_choice, {})
custom = st.session_state.custom_hotspots[model_choice]
parts = {**built_in, **custom}

# --- Sidebar part list (click to jump straight to a part's info) ---
st.sidebar.header("🧩 Parts")
if parts:
    for pname in parts:
        if st.sidebar.button(pname, key=f"side_{model_choice}_{pname}", use_container_width=True):
            st.session_state.selected_hotspot = pname
else:
    st.sidebar.caption("No parts added for this model yet.")

# --- Optional real-world size note ---
scale_note = st.text_input(
    "Real-world size (optional, shown under the title)",
    value=st.session_state.scale_notes.get(model_choice, ""),
    key=f"scale_{model_choice}",
)
st.session_state.scale_notes[model_choice] = scale_note
if scale_note:
    st.caption(f"📏 {scale_note}")

find_mode = st.checkbox(
    "🎯 Placement mode — click the model, the coordinates auto-copy to your clipboard"
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
        f'data-name="{name}" onclick="showInfo(this.getAttribute(\'data-name\'))"></button>\n'
    )

info_data = {}
positions = {}
for name, d in parts.items():
    if "explanation" in d:
        info_data[name] = d["explanation"].replace("\n", "<br>")
    else:
        info_data[name] = (
            f"<b>Material:</b> {d['material']}<br>"
            f"<b>Function:</b> {d['function']}<br>"
            f"<b>Notes:</b> {d['notes']}"
        )
    positions[name] = d["position"]

info_json = json.dumps(info_data)
positions_json = json.dumps(positions)
initial_selected = (
    st.session_state.selected_hotspot if st.session_state.selected_hotspot in parts else ""
)

# --- Theme colors ---
if st.session_state.theme == "Dark":
    bg = "#15181f"
    panel_bg = "#1e2530"
    panel_text = "#eee"
    viewer_bg = "#20242c"
else:
    bg = "#ffffff"
    panel_bg = "#f0f0f3"
    panel_text = "#1a1a1a"
    viewer_bg = "#fafafa"

# ---------------------------------------------------------------
# 5. THE FULL EMBEDDED PAGE
# ---------------------------------------------------------------
html = f"""
<script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
<style>
  body {{ margin: 0; font-family: sans-serif; background: {bg}; }}
  .viewer-wrap {{ position: relative; }}
  model-viewer {{
    width: 100%;
    height: 420px;
    background-color: {viewer_bg};
    border-radius: 8px;
    cursor: grab;
  }}
  model-viewer:active {{ cursor: grabbing; }}
  .Hotspot {{
    width: 22px;
    height: 22px;
    border-radius: 50%;
    border: 2px solid white;
    background: #4361ee;
    cursor: pointer;
    box-shadow: 0 0 6px rgba(0,0,0,0.4);
    transition: transform 0.25s ease;
  }}
  .Hotspot.pulse {{ transform: scale(1.6); }}
  #info-box {{
    display: none;
    margin-top: 14px;
    margin-bottom: 10px;
    padding: 16px 20px;
    border-radius: 8px;
    background: {panel_bg};
    color: {panel_text};
    font-size: 15px;
    line-height: 1.6;
    min-height: 90px;
  }}
  #info-box h3 {{ margin: 0 0 8px 0; }}
  #coord-box {{
    display: none;
    margin-top: 10px;
    padding: 14px 18px;
    border-radius: 8px;
    background: #2d1e30;
    color: #f0e6ff;
    font-size: 14px;
    font-family: monospace;
    white-space: pre-wrap;
  }}
  .toolbar {{
    position: absolute;
    top: 10px;
    right: 10px;
    display: flex;
    gap: 8px;
    z-index: 5;
  }}
  .toolbar button {{
    background: rgba(0,0,0,0.55);
    color: white;
    border: none;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 13px;
    cursor: pointer;
  }}
  .toolbar button:hover {{ background: rgba(0,0,0,0.8); }}
  #loading-overlay {{
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: {viewer_bg};
    border-radius: 8px;
    z-index: 4;
    flex-direction: column;
    color: {panel_text};
    font-size: 14px;
  }}
  .spinner {{
    width: 34px;
    height: 34px;
    border: 4px solid #4361ee33;
    border-top: 4px solid #4361ee;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin-bottom: 10px;
  }}
  @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
</style>

<div class="viewer-wrap">
  <div class="toolbar">
    <button onclick="toggleExplode()">🧨 Explode</button>
    <button onclick="resetView()">↺ Reset</button>
  </div>
  <div id="loading-overlay"><div class="spinner"></div>Loading model...</div>
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
</div>

<div id="info-box"></div>
<div id="coord-box"></div>

<script>
  const partInfo = {info_json};
  const partPositions = {positions_json};
  const findMode = {str(find_mode).lower()};
  const mv = document.getElementById('mv');
  let exploded = false;

  mv.addEventListener('load', () => {{
    document.getElementById('loading-overlay').style.display = 'none';
  }});

  function speak(text) {{
    try {{
      const plain = text.replace(/<[^>]+>/g, ' ');
      const utter = new SpeechSynthesisUtterance(plain);
      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(utter);
    }} catch (e) {{}}
  }}

  function showInfo(name) {{
    const html = partInfo[name];
    const box = document.getElementById('info-box');
    if (!html) return;
    box.style.display = 'block';
    box.innerHTML = '<h3>📌 ' + name + '</h3>' + html;
    speak(name + '. ' + html);

    // Pulse the matching hotspot dot
    document.querySelectorAll('.Hotspot').forEach(h => {{
      if (h.getAttribute('data-name') === name) {{
        h.classList.add('pulse');
        setTimeout(() => h.classList.remove('pulse'), 600);
      }}
    }});

    // Gently focus the camera toward that part
    const pos = partPositions[name];
    if (pos) {{
      const [x, y, z] = pos.split(' ');
      mv.cameraTarget = x + 'm ' + y + 'm ' + z + 'm';
    }}
  }}

  function toggleExplode() {{
    exploded = !exploded;
    mv.cameraOrbit = exploded ? 'auto auto 130%' : 'auto auto 65%';
  }}

  function resetView() {{
    exploded = false;
    mv.cameraOrbit = 'auto auto 65%';
    mv.cameraTarget = 'auto';
  }}

  if (findMode) {{
    mv.addEventListener('click', (event) => {{
      const rect = mv.getBoundingClientRect();
      const hit = mv.positionAndNormalFromPoint(
        event.clientX - rect.left, event.clientY - rect.top
      );
      if (!hit) return;
      const p = hit.position;
      const n = hit.normal;
      const line = p.x.toFixed(3) + ' ' + p.y.toFixed(3) + ' ' + p.z.toFixed(3) + ' ' +
                   n.x.toFixed(3) + ' ' + n.y.toFixed(3) + ' ' + n.z.toFixed(3);
      const box = document.getElementById('coord-box');
      box.style.display = 'block';
      box.innerText = 'Copied to clipboard — paste it in the form below:\\n\\n' + line;
      if (navigator.clipboard) {{
        navigator.clipboard.writeText(line).catch(() => {{}});
      }}
    }});
  }}

  const initialSelected = "{initial_selected}";
  if (initialSelected) {{
    window.addEventListener('DOMContentLoaded', () => showInfo(initialSelected));
  }}
</script>
"""

components.html(html, height=800, scrolling=True)

# ---------------------------------------------------------------
# 6. FORM TO ADD A NEW HOTSPOT (simplified — paste, don't type numbers)
# ---------------------------------------------------------------
st.divider()
st.subheader("➕ Add a hotspot")
st.caption(
    "Turn on Placement mode above, click the spot on the model (the "
    "coordinates copy to your clipboard automatically), then paste "
    "them into the box below."
)

with st.form("add_hotspot_form", clear_on_submit=True):
    new_name = st.text_input("Part name (e.g. Charging Port)")
    new_explanation = st.text_area("Explanation (whatever you want to say about it)")
    pasted_coords = st.text_input(
        "Paste the coordinates here (just Ctrl+V — 6 numbers, auto-copied when you clicked)"
    )

    submitted = st.form_submit_button("Add Hotspot")
    if submitted:
        if not new_name.strip():
            st.warning("Give the part a name first.")
        else:
            nums = pasted_coords.replace(",", " ").split()
            if len(nums) != 6:
                st.warning(
                    "Couldn't read 6 numbers from that paste — turn on "
                    "Placement mode, click the model again, and paste fresh."
                )
            else:
                try:
                    nums = [float(n) for n in nums]
                except ValueError:
                    st.warning("Those don't look like valid numbers — try pasting again.")
                    nums = None
                if nums:
                    position = f"{nums[0]} {nums[1]} {nums[2]}"
                    normal = f"{nums[3]} {nums[4]} {nums[5]}"
                    st.session_state.custom_hotspots[model_choice][new_name.strip()] = {
                        "position": position,
                        "normal": normal,
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

# ---------------------------------------------------------------
# 7. EXPORT PART INFO AS PDF
# ---------------------------------------------------------------
st.divider()
st.subheader("📄 Export")

if not parts:
    st.caption("Add at least one hotspot to enable PDF export.")
elif not FPDF_AVAILABLE:
    st.caption("PDF export needs the 'fpdf2' package — add it to requirements.txt.")
else:
    def pdf_safe(text):
        # The built-in PDF font only supports a limited character set —
        # swap anything it can't render instead of crashing.
        return (
            str(text)
            .replace("—", "-").replace("–", "-")
            .replace(""", '"').replace(""", '"')
            .replace("'", "'").replace("'", "'")
            .encode("latin-1", "replace").decode("latin-1")
        )

    if st.button("Download part info as PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(0, 12, pdf_safe(f"ExplainIt3D - {model_choice}"), new_x="LMARGIN", new_y="NEXT")
        if scale_note:
            pdf.set_font("Helvetica", "", 11)
            pdf.cell(0, 8, pdf_safe(f"Size: {scale_note}"), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

        for name, d in parts.items():
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 10, pdf_safe(name), new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 11)
            if "explanation" in d:
                pdf.multi_cell(0, 7, pdf_safe(d["explanation"]))
            else:
                pdf.multi_cell(
                    0, 7,
                    pdf_safe(
                        f"Material: {d['material']}\n"
                        f"Function: {d['function']}\n"
                        f"Notes: {d['notes']}"
                    )
                )
            pdf.ln(3)

        pdf_bytes = bytes(pdf.output())
        st.download_button(
            "⬇️ Click to save the PDF",
            data=pdf_bytes,
            file_name=f"{model_choice.replace(' ', '_')}_parts.pdf",
            mime="application/pdf",
        )
