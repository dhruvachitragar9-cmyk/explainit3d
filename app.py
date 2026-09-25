"""
ExplainIt3D — Interactive 3D Model Viewer with Part Annotations

Rotate a 3D model in the browser, tap the labeled dots on it, and see
detailed information about that part (material, function, notes).

Everything here is plain Python. Streamlit turns it into a web page.
"""

import streamlit as st
import streamlit_3d as sd

# ---------------------------------------------------------------
# 1. PICK A MODEL
# ---------------------------------------------------------------
SAMPLE_MODELS = {
    "My Laptop": "laptop.glb",
    "Engine": "https://alteirac.com/models/engine/scene.gltf",
    "Helmet": "https://alteirac.com/models/helmet/scene.gltf",
    "Turbine": "https://alteirac.com/models/turbine/scene.gltf",
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
        "notes": "Chosen for its strength-to-weight ratio and heat dissipation.",
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
    {
        "description": "Engine Block",
        "data-position": {"x": 0.05, "y": 0.35, "z": 0.15},
        "data-normal": {"x": 0.0, "y": 0.0, "z": 1.0},
    },
    {
        "description": "Exhaust Manifold",
        "data-position": {"x": -0.25, "y": 0.2, "z": 0.05},
        "data-normal": {"x": -1.0, "y": 0.0, "z": 0.0},
    },
    {
        "description": "Intake Valve",
        "data-position": {"x": 0.15, "y": 0.45, "z": -0.1},
        "data-normal": {"x": 0.0, "y": 1.0, "z": 0.0},
    },
]

# ---------------------------------------------------------------
# 3. PAGE SETUP
# ---------------------------------------------------------------
st.set_page_config(page_title="ExplainIt3D", layout="wide")

st.title("🔍 ExplainIt3D")
st.caption("Rotate the model, tap a labeled point, and see the details.")

model_choice = st.selectbox("Model:", list(SAMPLE_MODELS.keys()), index=0)
model_url = SAMPLE_MODELS[model_choice]

hotspots = ENGINE_HOTSPOTS if model_choice == "Engine" else []

if model_choice == "My Laptop":
    st.info(
        "This is your laptop model — right-click anywhere on it to drop "
        "a hotspot pin (see README for the full steps), then match its "
        "label to an entry in PART_INFO in app.py."
    )
elif model_choice != "Engine":
    st.info(
        "Hotspots are only set up for the Engine sample right now — "
        "switch back to Engine to see tap-for-info in action, or add "
        "hotspot coordinates for the other models yourself."
    )

# ---------------------------------------------------------------
# 4. RENDER THE 3D MODEL WITH HOTSPOTS
# ---------------------------------------------------------------
clicked = sd.streamlit_3d(model=model_url, points=hotspots, height=600)

# ---------------------------------------------------------------
# 5. SHOW INFO WHEN A HOTSPOT IS TAPPED
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
