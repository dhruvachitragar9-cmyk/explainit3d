"""
ExplainIt3D — Interactive 3D Model Viewer with Part Annotations
Search bar added on top of your existing catalog (including your laptop).
"""

import streamlit as st
import streamlit_3d as sd

# ---------------------------------------------------------------
# 1. MODEL CATALOG — add new entries here (just a name + URL/file,
#    no need to touch anything else in this file).
# ---------------------------------------------------------------
MODEL_CATALOG = {
    "My Laptop": "laptop.glb",
    "Engine":    "https://alteirac.com/models/engine/scene.gltf",
    "Helmet":    "https://alteirac.com/models/helmet/scene.gltf",
    "Turbine":   "https://alteirac.com/models/turbine/scene.gltf",
}

# ---------------------------------------------------------------
# 2. YOUR PART DATA
# ---------------------------------------------------------------
PART_INFO = {
    "Screen": {
        "material": "LCD panel with glass/plastic casing",
        "function": "Displays visual output to the user.",
        "notes": "Fill in the real details for your laptop here.",
    },
    "Keyboard": {
        "material": "Plastic keys over a membrane/scissor mechanism",
        "function": "Primary text input device.",
        "notes": "Fill in the real details for your laptop here.",
    },
    "Trackpad": {
        "material": "Glass or plastic surface over touch sensors",
        "function": "Cursor control and gestures.",
        "notes": "Fill in the real details for your laptop here.",
    },
    "Engine Block": {
        "material": "Cast Aluminum Alloy",
        "function": "Houses the cylinders and core moving components.",
        "notes": "Chosen for strength-to-weight ratio and heat dissipation.",
    },
    "Exhaust Manifold": {
        "material": "Stainless Steel",
        "function": "Channels exhaust gases away from the cylinders.",
        "notes": "Resistant to high temperatures and corrosion.",
    },
    "Intake Valve": {
        "material": "Forged Steel",
        "function": "Controls airflow into the combustion chamber.",
        "notes": "Must withstand repeated high-speed mechanical stress.",
    },
}

ENGINE_HOTSPOTS = [
    {"description": "Engine Block",
     "data-position": {"x": 0.05, "y": 0.35, "z": 0.15},
     "data-normal": {"x": 0.0, "y": 0.0, "z": 1.0}},
    {"description": "Exhaust Manifold",
     "data-position": {"x": -0.25, "y": 0.2, "z": 0.05},
     "data-normal": {"x": -1.0, "y": 0.0, "z": 0.0}},
    {"description": "Intake Valve",
     "data-position": {"x": 0.15, "y": 0.45, "z": -0.1},
     "data-normal": {"x": 0.0, "y": 1.0, "z": 0.0}},
]

# Add real hotspot coordinates for your laptop here once you place them
# (right-click on the model in the viewer to get x/y/z, per your README).
LAPTOP_HOTSPOTS = []

# ---------------------------------------------------------------
# 3. PAGE SETUP
# ---------------------------------------------------------------
st.set_page_config(page_title="ExplainIt3D", layout="wide")
st.title("🔍 ExplainIt3D")
st.caption("Search for a model, rotate it, tap a labeled point to see details.")

# ---------------------------------------------------------------
# 4. SEARCH BAR — filters the catalog above
# ---------------------------------------------------------------
search_term = st.text_input("Search models:", placeholder="e.g. laptop, engine, helmet...")

if search_term:
    matches = {name: url for name, url in MODEL_CATALOG.items()
               if search_term.lower() in name.lower()}
else:
    matches = MODEL_CATALOG

if not matches:
    st.warning("No matching model in the catalog yet. Add its entry to MODEL_CATALOG in app.py.")
    st.stop()

model_choice = st.selectbox("Pick a model:", list(matches.keys()))
model_url = matches[model_choice]

if model_choice == "Engine":
    hotspots = ENGINE_HOTSPOTS
elif model_choice == "My Laptop":
    hotspots = LAPTOP_HOTSPOTS
    if not hotspots:
        st.info("Right-click on the laptop model to drop hotspot pins, then add "
                 "their coordinates to LAPTOP_HOTSPOTS in app.py.")
else:
    hotspots = []
    st.info("Hotspots aren't mapped for this model yet — add coordinates the same way.")

# ---------------------------------------------------------------
# 5. RENDER MODEL
# ---------------------------------------------------------------
clicked = sd.streamlit_3d(model=model_url, points=hotspots, height=600)

# ---------------------------------------------------------------
# 6. SHOW INFO WHEN A HOTSPOT IS TAPPED
# ---------------------------------------------------------------
if clicked is not None and clicked.get("action") == "CLICK":
    part_name = clicked.get("description")
    info = PART_INFO.get(part_name)
    st.divider()
    if info:
        st.subheader(f"📌 {part_name}")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Material:** {info['material']}")
            st.markdown(f"**Function:** {info['function']}")
        with col2:
            st.markdown(f"**Notes:** {info['notes']}")
    else:
        st.warning(f"No info stored yet for '{part_name}'.")
else:
    st.caption("Tap a labeled dot on the model above to see its details here.")
