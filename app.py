import streamlit as st
import streamlit.components.v1 as components
import os
import base64
import json


# =====================================================
# PAGE
# =====================================================

st.set_page_config(
    page_title="ExplainIt3D",
    layout="wide"
)

st.title("🔬 ExplainIt3D")
st.write("Interactive 3D Object Explorer")


# =====================================================
# GAMING MOUSE MODEL
# =====================================================

model_path = os.path.expanduser(
    "~/.objaverse/hf-objaverse-v1/glbs/000-000/"
    "fb9d4da093bd4d1cab6cc29424a3e591.glb"
)


# =====================================================
# CHECK MODEL
# =====================================================

if not os.path.isfile(model_path):

    st.error("Gaming Mouse model not found.")

    st.code(model_path)

    st.stop()


    # =====================================================
    # READ GLB
    # =====================================================

    with open(model_path, "rb") as f:

        model_base64 = base64.b64encode(
            f.read()
        ).decode("ascii")


        model_json = json.dumps(model_base64)


        # =====================================================
        # THREE.JS VIEWER
        # =====================================================

        html = f"""
        <!DOCTYPE html>

        <html>

        <head>

        <style>

        html,
        body {{

            margin: 0;
            padding: 0;

            overflow: hidden;

            background: #111;

            }}

            #viewer {{

                width: 100%;
                height: 650px;

            }}

            canvas {{

                display: block;

            }}

            </style>

            </head>


            <body>

            <div id="viewer"></div>


            <script type="importmap">

            {{
                "imports": {{

                    "three":
                        "https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js",

                        "three/addons/":
                            "https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/"

                        }}
                    }}

                    </script>


                    <script type="module">

import * as THREE from "three";

import {{ OrbitControls }}
from "three/addons/controls/OrbitControls.js";

import {{ GLTFLoader }}
from "three/addons/loaders/GLTFLoader.js";


// =====================================================
// SCENE
// =====================================================

const scene = new THREE.Scene();

scene.background = new THREE.Color(0x111111);


// =====================================================
// CAMERA
// =====================================================

const camera = new THREE.PerspectiveCamera(
    45,
    window.innerWidth / 650,
    0.01,
    1000
);

camera.position.set(
    0,
    0.5,
    3
);


// =====================================================
// RENDERER
// =====================================================

const renderer = new THREE.WebGLRenderer({

    antialias: true

});

renderer.setSize(
    window.innerWidth,
    650
);

renderer.setPixelRatio(
    Math.min(window.devicePixelRatio, 2)
);

renderer.outputColorSpace =
THREE.SRGBColorSpace;


document
.getElementById("viewer")
.appendChild(renderer.domElement);


// =====================================================
// CONTROLS
// =====================================================

const controls = new OrbitControls(
    camera,
    renderer.domElement
);

controls.enableDamping = true;

controls.autoRotate = true;

controls.autoRotateSpeed = 0.5;


// =====================================================
// LIGHTING
// =====================================================

const ambient = new THREE.AmbientLight(
    0xffffff,
    2
);

scene.add(ambient);


const light = new THREE.DirectionalLight(
    0xffffff,
    3
);

light.position.set(
    3,
    5,
    5
);

scene.add(light);


// =====================================================
// GAMING MOUSE DATA
// =====================================================

const base64 = {model_json};

const binary = atob(base64);

const bytes = new Uint8Array(
    binary.length
);


for (
    let i = 0;
    i < binary.length;
    i++
) {{

    bytes[i] =
    binary.charCodeAt(i);

}}


// =====================================================
// LOAD MODEL
// =====================================================

const loader = new GLTFLoader();


loader.parse(

    bytes.buffer,

    "",

    function(gltf) {{

        const model = gltf.scene;

        scene.add(model);


        // Find model size

        const box = new THREE.Box3()
        .setFromObject(model);


        const center = box.getCenter(
            new THREE.Vector3()
        );


        const size = box.getSize(
            new THREE.Vector3()
        );


        // Center model

        model.position.sub(center);


        // Scale model

        const largest = Math.max(
            size.x,
            size.y,
            size.z
        );


        if (largest > 0) {{

            model.scale.setScalar(
                2 / largest
            );

        }}


        controls.target.set(
            0,
            0,
            0
        );

        controls.update();


        console.log(
            "Gaming Mouse loaded successfully!"
        );

    }},


    function(error) {{

        console.error(
            "Gaming Mouse loading error:",
            error
        );

    }}

);


// =====================================================
// ANIMATION
// =====================================================

function animate() {{

    requestAnimationFrame(
        animate
    );

    controls.update();

    renderer.render(
        scene,
        camera
    );

}}

animate();


// =====================================================
// RESIZE
// =====================================================

window.addEventListener(
    "resize",
    function() {{

        camera.aspect =
        window.innerWidth / 650;

        camera.updateProjectionMatrix();

        renderer.setSize(
            window.innerWidth,
            650
        );

    }}
);

</script>


</body>

</html>
"""


# =====================================================
# DISPLAY VIEWER
# =====================================================

components.html(
    html,
    height=680
)