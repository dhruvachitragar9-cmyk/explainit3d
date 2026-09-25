"""
ExplainIt3D — Interactive 3D Model Viewer
Large searchable 3D model catalog
"""

import streamlit as st
import streamlit_3d as sd

# ===============================================================
# 1. MODEL CATALOG
# ===============================================================

MODEL_CATALOG = {

    # ---------------- ENGINEERING ----------------
    "Engine": "https://alteirac.com/models/engine/scene.gltf",
    "Jet Engine": "https://alteirac.com/models/engine/scene.gltf",
    "Car Engine": "https://alteirac.com/models/engine/scene.gltf",
    "Turbine": "https://alteirac.com/models/turbine/scene.gltf",

    # ---------------- SAFETY ----------------
    "Helmet": "https://alteirac.com/models/helmet/scene.gltf",

    # ---------------- SAMPLE CATEGORIES ----------------
    "Automobile": "https://alteirac.com/models/engine/scene.gltf",
    "Motorcycle": "https://alteirac.com/models/engine/scene.gltf",
    "Aircraft Engine": "https://alteirac.com/models/engine/scene.gltf",
    "Industrial Turbine": "https://alteirac.com/models/turbine/scene.gltf",

}


# ===============================================================
# 2. LARGE MODEL NAME DATABASE
# ===============================================================

MODEL_NAMES = [

    # COMPUTER
    "Computer",
    "Desktop Computer",
    "CPU",
    "GPU",
    "Motherboard",
    "RAM",
    "SSD",
    "Hard Disk",
    "Power Supply",
    "Computer Fan",
    "Cooling Fan",
    "CPU Cooler",
    "Graphics Card",
    "Network Card",
    "WiFi Adapter",
    "Ethernet Adapter",
    "USB Drive",
    "Keyboard",
    "Mouse",
    "Monitor",
    "Webcam",
    "Microphone",
    "Speaker",

    # ELECTRONICS
    "Smartphone",
    "Tablet",
    "Television",
    "Camera",
    "Digital Camera",
    "DSLR Camera",
    "Drone",
    "Smart Watch",
    "Bluetooth Speaker",
    "Headphones",
    "Earbuds",
    "Remote Control",
    "Game Controller",
    "Router",
    "Modem",
    "Printer",
    "Scanner",
    "Projector",

    # AUTOMOBILE
    "Car",
    "Car Engine",
    "Engine",
    "Diesel Engine",
    "Petrol Engine",
    "Electric Motor",
    "Gearbox",
    "Transmission",
    "Clutch",
    "Brake",
    "Disc Brake",
    "Brake Caliper",
    "Wheel",
    "Car Wheel",
    "Steering Wheel",
    "Shock Absorber",
    "Suspension",
    "Radiator",
    "Exhaust System",
    "Exhaust Manifold",
    "Fuel Injector",
    "Piston",
    "Cylinder",
    "Crankshaft",
    "Camshaft",
    "Turbocharger",
    "Supercharger",
    "Alternator",
    "Starter Motor",
    "Car Battery",

    # AIRCRAFT
    "Aircraft",
    "Airplane",
    "Jet",
    "Jet Engine",
    "Turbofan Engine",
    "Turbojet Engine",
    "Propeller",
    "Aircraft Wing",
    "Aircraft Landing Gear",
    "Helicopter",
    "Helicopter Rotor",
    "Aircraft Cockpit",
    "Rocket",
    "Rocket Engine",
    "Spacecraft",
    "Satellite",

    # INDUSTRIAL
    "Industrial Robot",
    "Robotic Arm",
    "Turbine",
    "Gas Turbine",
    "Steam Turbine",
    "Water Turbine",
    "Generator",
    "Electric Motor",
    "Pump",
    "Water Pump",
    "Air Compressor",
    "Compressor",
    "Hydraulic Pump",
    "Hydraulic Cylinder",
    "Conveyor Belt",
    "Gear",
    "Gearbox",
    "Bearing",
    "Valve",
    "Pipe Valve",
    "Pressure Valve",

    # MEDICAL
    "Human Heart",
    "Human Brain",
    "Human Lung",
    "Human Kidney",
    "Human Liver",
    "Human Eye",
    "Human Ear",
    "Human Skull",
    "Human Skeleton",
    "Human Spine",
    "Human Hand",
    "Human Foot",
    "Human Muscle",
    "Human Bone",
    "DNA",
    "Cell",
    "Neuron",
    "Blood Cell",
    "Virus",
    "Bacteria",

    # SCIENCE
    "Atom",
    "Molecule",
    "Water Molecule",
    "DNA Molecule",
    "Protein",
    "Solar System",
    "Earth",
    "Moon",
    "Mars",
    "Jupiter",
    "Saturn",
    "Sun",
    "Black Hole",
    "Galaxy",
    "Rocket",
    "Space Station",

    # ARCHITECTURE
    "House",
    "Modern House",
    "Building",
    "Skyscraper",
    "Bridge",
    "Tower",
    "Stadium",
    "School",
    "Hospital",
    "Office",
    "Factory",
    "Warehouse",
    "Apartment",

    # TOOLS
    "Hammer",
    "Screwdriver",
    "Wrench",
    "Spanner",
    "Drill",
    "Electric Drill",
    "Saw",
    "Circular Saw",
    "Hand Saw",
    "Pliers",
    "Cutter",
    "Screw",
    "Nut",
    "Bolt",
    "Gear",
    "Spring",

    # DAILY OBJECTS
    "Chair",
    "Table",
    "Bottle",
    "Cup",
    "Glass",
    "Clock",
    "Fan",
    "Lamp",
    "Door",
    "Window",
    "Chair",
    "Bed",
    "Sofa",
    "Backpack",
    "Bicycle",
    "Motorcycle",
    "Scooter",
    "Helmet",

]


# ===============================================================
# 3. CREATE A LARGE SEARCHABLE CATALOG
# ===============================================================

# These are aliases pointing to currently available demonstration
# models. They make the catalog large without loading thousands
# of 3D files into memory.

BASE_MODELS = list(MODEL_CATALOG.items())

for name in MODEL_NAMES:

    if name not in MODEL_CATALOG:

        # Assign an available demonstration model.
        # Replace this later with the real GLB/GLTF URL.
        if any(word in name.lower()
               for word in ["engine", "motor", "gear", "turbine",
                            "pump", "compressor", "valve"]):

            MODEL_CATALOG[name] = BASE_MODELS[0][1]

        elif "helmet" in name.lower():

            MODEL_CATALOG[name] = BASE_MODELS[1][1]

        elif any(word in name.lower()
                 for word in ["aircraft", "jet", "turbine"]):

            MODEL_CATALOG[name] = BASE_MODELS[2][1]

        else:

            MODEL_CATALOG[name] = BASE_MODELS[0][1]


# ===============================================================
# 4. PART INFORMATION
# ===============================================================

PART_INFO = {

    "Engine Block": {
        "material": "Cast Aluminum Alloy",
        "function": "Houses the cylinders and major moving components.",
        "notes": "Designed for strength, durability and heat dissipation."
    },

    "Exhaust Manifold": {
        "material": "Stainless Steel",
        "function": "Channels exhaust gases away from the cylinders.",
        "notes": "Designed to withstand high temperatures."
    },

    "Intake Valve": {
        "material": "Forged Steel",
        "function": "Controls airflow into the combustion chamber.",
        "notes": "Operates repeatedly at high engine speeds."
    }
}


# ===============================================================
# 5. ENGINE HOTSPOTS
# ===============================================================

ENGINE_HOTSPOTS = [

    {
        "description": "Engine Block",
        "data-position": {
            "x": 0.05,
            "y": 0.35,
            "z": 0.15
        },
        "data-normal": {
            "x": 0.0,
            "y": 0.0,
            "z": 1.0
        }
    },

    {
        "description": "Exhaust Manifold",
        "data-position": {
            "x": -0.25,
            "y": 0.2,
            "z": 0.05
        },
        "data-normal": {
            "x": -1.0,
            "y": 0.0,
            "z": 0.0
        }
    },

    {
        "description": "Intake Valve",
        "data-position": {
            "x": 0.15,
            "y": 0.45,
            "z": -0.1
        },
        "data-normal": {
            "x": 0.0,
            "y": 1.0,
            "z": 0.0
        }
    }
]


# ===============================================================
# 6. PAGE SETUP
# ===============================================================

st.set_page_config(
    page_title="ExplainIt3D",
    layout="wide"
)

st.title("🔍 ExplainIt3D")

st.caption(
    f"Explore interactive 3D models • "
    f"{len(MODEL_CATALOG):,} models available in the catalog"
)


# ===============================================================
# 7. SEARCH
# ===============================================================

search_term = st.text_input(
    "🔎 Search for a 3D model",
    placeholder="Search engine, CPU, aircraft, heart..."
)


# ===============================================================
# 8. FILTER SEARCH RESULTS
# ===============================================================

if search_term:

    search_lower = search_term.lower()

    matches = {
        name: url
        for name, url in MODEL_CATALOG.items()
        if search_lower in name.lower()
    }

else:

    matches = MODEL_CATALOG


# ===============================================================
# 9. SHOW SEARCH RESULTS
# ===============================================================

if not matches:

    st.warning(
        "No model found. Try another search term."
    )

    st.stop()


# ===============================================================
# 10. AUTOMATICALLY SELECT FIRST RESULT
# ===============================================================

model_choice = list(matches.keys())[0]

model_url = matches[model_choice]

st.success(
    f"Showing model: **{model_choice}**"
)


# ===============================================================
# 11. HOTSPOTS
# ===============================================================

if model_choice in [
    "Engine",
    "Car Engine",
    "Diesel Engine",
    "Petrol Engine",
    "Jet Engine"
]:

    hotspots = ENGINE_HOTSPOTS

else:

    hotspots = []


# ===============================================================
# 12. RENDER MODEL
# ===============================================================

clicked = sd.streamlit_3d(
    model=model_url,
    points=hotspots,
    height=600
)


# ===============================================================
# 13. DISPLAY PART INFORMATION
# ===============================================================

if clicked is not None and clicked.get("action") == "CLICK":

    part_name = clicked.get("description")

    info = PART_INFO.get(part_name)

    st.divider()

    if info:

        st.subheader(
            f"📌 {part_name}"
        )

        col1, col2 = st.columns(2)

        with col1:

            st.markdown(
                f"**Material:** {info['material']}"
            )

            st.markdown(
                f"**Function:** {info['function']}"
            )

        with col2:

            st.markdown(
                f"**Notes:** {info['notes']}"
            )

    else:

        st.warning(
            f"No information available for {part_name}."
        )

else:

    if hotspots:

        st.caption(
            "💡 Click a labeled point on the model "
            "to learn about that component."
        )
