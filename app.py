"""
ExplainIt3D — Interactive 3D Model Viewer with Part Annotations

Rotate a 3D model in the browser (it also spins slowly on its own),
tap the labeled dots on it, and see detailed information about that
part. Includes a sidebar part list, explode/reset buttons, a hotspot
manager (edit + delete), file upload preview and PDF export.
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import base64

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
if "hidden_builtin" not in st.session_state:
    st.session_state.hidden_builtin = {}
if "selected_hotspot" not in st.session_state:
    st.session_state.selected_hotspot = None

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
st.session_state.hidden_builtin.setdefault(model_choice, set())

hidden = st.session_state.hidden_builtin[model_choice]
built_in = {
    k: v for k, v in MODEL_DATA.get(model_choice, {}).items() if k not in hidden
}
custom = st.session_state.custom_hotspots[model_choice]
parts = {**built_in, **custom}


def remove_part(part_name):
    """Delete a hotspot — built-in ones get hidden, custom ones get removed."""
    if part_name in custom:
        del custom[part_name]
    if part_name in MODEL_DATA.get(model_choice, {}):
        hidden.add(part_name)


def part_as_text(d):
    if "explanation" in d:
        return d["explanation"]
    return (
        f"Material: {d['material']}\n"
        f"Function: {d['function']}\n"
        f"Notes: {d['notes']}"
    )


def parse_coords(text):
    """Turn '0.1 0.2 0.3 0 1 0' into (position, normal) strings, or None."""
    nums = text.replace(",", " ").split()
    if len(nums) != 6:
        return None
    try:
        nums = [float(n) for n in nums]
    except ValueError:
        return None
    return (
        f"{nums[0]} {nums[1]} {nums[2]}",
        f"{nums[3]} {nums[4]} {nums[5]}",
    )


# --- Sidebar part list (click to jump straight to a part's info) ---
st.sidebar.header("🧩 Parts")
if parts:
    for pname in parts:
        if st.sidebar.button(pname, key=f"side_{model_choice}_{pname}", use_container_width=True):
            st.session_state.selected_hotspot = pname
else:
    st.sidebar.caption("No parts added for this model yet.")

find_mode = st.checkbox(
    "🎯 Placement mode — click the model, the coordinates auto-copy to your clipboard"
)

if not parts:
    st.info("No hotspots on this model yet — add one below.")

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

# ---------------------------------------------------------------
# 5. THE FULL EMBEDDED PAGE
# ---------------------------------------------------------------
html = f"""
<script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
<style>
  body {{ margin: 0; font-family: sans-serif; background: #15181f; }}
  .viewer-wrap {{ position: relative; }}
  model-viewer {{
    width: 100%;
    height: 420px;
    background-color: #20242c;
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
    transition: transform 0.25s ease;
  }}
  .Hotspot.pulse {{ transform: scale(1.6); }}
  #info-box {{
    display: none;
    margin-top: 14px;
    margin-bottom: 10px;
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
    background: #20242c;
    border-radius: 8px;
    z-index: 4;
    flex-direction: column;
    color: #eee;
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

  function showInfo(name) {{
    const html = partInfo[name];
    const box = document.getElementById('info-box');
    if (!html) return;
    box.style.display = 'block';
    box.innerHTML = '<h3>📌 ' + name + '</h3>' + html;

    document.querySelectorAll('.Hotspot').forEach(h => {{
      if (h.getAttribute('data-name') === name) {{
        h.classList.add('pulse');
        setTimeout(() => h.classList.remove('pulse'), 600);
      }}
    }});

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
# 6. ADD A NEW HOTSPOT
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
        elif new_name.strip() in parts:
            st.warning("A hotspot with that name already exists — pick a different name.")
        else:
            coords = parse_coords(pasted_coords)
            if coords is None:
                st.warning(
                    "Couldn't read 6 numbers from that paste — turn on "
                    "Placement mode, click the model again, and paste fresh."
                )
            else:
                custom[new_name.strip()] = {
                    "position": coords[0],
                    "normal": coords[1],
                    "explanation": new_explanation.strip() or "No explanation added yet.",
                }
                st.rerun()

# ---------------------------------------------------------------
# 7. MANAGE HOTSPOTS (edit + delete)
# ---------------------------------------------------------------
st.divider()
st.subheader("🛠️ Manage hotspots")
st.caption(
    "Open a hotspot to edit it or delete it. Changes last while the app "
    "is open — refreshing the page resets to what's saved in app.py."
)

if not parts:
    st.caption("Nothing to manage yet.")

for pname, pdata in list(parts.items()):
    with st.expander(pname):
        with st.form(f"edit_{model_choice}_{pname}"):
            edit_name = st.text_input("Name", value=pname)
            edit_text = st.text_area("Explanation", value=part_as_text(pdata))
            edit_coords = st.text_input(
                "New coordinates (optional — paste 6 numbers to move the dot, leave blank to keep it where it is)"
            )
            save = st.form_submit_button("💾 Save changes")

        if save:
            new_nm = edit_name.strip()
            if not new_nm:
                st.warning("The name can't be empty.")
            elif new_nm != pname and new_nm in parts:
                st.warning("Another hotspot already has that name.")
            else:
                position, normal = pdata["position"], pdata["normal"]
                if edit_coords.strip():
                    coords = parse_coords(edit_coords)
                    if coords is None:
                        st.warning("Couldn't read 6 numbers from the coordinates — nothing was changed.")
                        st.stop()
                    position, normal = coords
                remove_part(pname)
                custom[new_nm] = {
                    "position": position,
                    "normal": normal,
                    "explanation": edit_text.strip() or "No explanation added yet.",
                }
                st.rerun()

        if st.button("🗑️ Delete this hotspot", key=f"del_{model_choice}_{pname}"):
            remove_part(pname)
            st.rerun()

# ---------------------------------------------------------------
# 8. EXPORT PART INFO AS PDF
# ---------------------------------------------------------------
st.divider()
st.subheader("📄 Export")

if not parts:
    st.caption("Add at least one hotspot to enable PDF export.")
elif not FPDF_AVAILABLE:
    st.caption("PDF export needs the 'fpdf2' package — add it to requirements.txt.")
else:
    def pdf_safe(text):
        return (
            str(text)
            .replace("\u2014", "-").replace("\u2013", "-")
            .replace("\u201c", '"').replace("\u201d", '"')
            .replace("\u2018", "'").replace("\u2019", "'")
            .encode("latin-1", "replace").decode("latin-1")
        )

    if st.button("Download part info as PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(0, 12, pdf_safe(f"ExplainIt3D - {model_choice}"), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

        for name, d in parts.items():
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 10, pdf_safe(name), new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(0, 7, pdf_safe(part_as_text(d)))
            pdf.ln(3)

        st.download_button(
            "⬇️ Click to save the PDF",
            data=bytes(pdf.output()),
            file_name=f"{model_choice.replace(' ', '_')}_parts.pdf",
            mime="application/pdf",
        )
