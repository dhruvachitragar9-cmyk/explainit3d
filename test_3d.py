import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Three.js Test",
    layout="wide"
)

st.title("🧪 Three.js Test")

components.html(
    """
    <!DOCTYPE html>
    <html>

    <head>

    <style>

    html, body {
        margin: 0;
        padding: 0;
        overflow: hidden;
        background: #111;
        }

        #viewer {
            width: 100%;
            height: 600px;
        }

        </style>

        </head>

        <body>

        <div id="viewer"></div>

        <script type="importmap">
        {
            "imports": {
                "three": "https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js",
                "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/"
            }
        }
        </script>

        <script type="module">

import * as THREE from "three";

import { OrbitControls } from
"three/addons/controls/OrbitControls.js";

import { GLTFLoader } from
"three/addons/loaders/GLTFLoader.js";


const scene = new THREE.Scene();

scene.background =
new THREE.Color(0x111111);


const camera =
new THREE.PerspectiveCamera(
    45,
    window.innerWidth / 600,
    0.01,
    100
);

camera.position.set(
    0,
    1,
    4
);


const renderer =
new THREE.WebGLRenderer({
    antialias: true
});

renderer.setSize(
    window.innerWidth,
    600
);

renderer.setPixelRatio(
    window.devicePixelRatio
);

renderer.outputColorSpace =
THREE.SRGBColorSpace;


document
.getElementById("viewer")
.appendChild(renderer.domElement);


// Controls

const controls =
new OrbitControls(
    camera,
    renderer.domElement
);

controls.enableDamping = true;

controls.autoRotate = true;

controls.autoRotateSpeed = 0.5;


// Lights

scene.add(
    new THREE.AmbientLight(
        0xffffff,
        2
    )
);

const light =
new THREE.DirectionalLight(
    0xffffff,
    3
);

light.position.set(
    3,
    5,
    5
);

scene.add(light);


// Load public test model

const loader =
new GLTFLoader();

loader.load(
    "https://threejs.org/examples/models/gltf/DamagedHelmet/glTF/DamagedHelmet.gltf",

    function(gltf) {

        const model =
        gltf.scene;

        scene.add(model);

        model.scale.setScalar(2);

        controls.target.set(
            0,
            0,
            0
        );

        controls.update();

        console.log(
            "THREE.JS MODEL LOADED"
        );
    },

    undefined,

    function(error) {

        console.error(
            "MODEL ERROR:",
            error
        );
    }
);


// Animation

function animate() {

    requestAnimationFrame(
        animate
    );

    controls.update();

    renderer.render(
        scene,
        camera
    );
}

animate();


// Resize

window.addEventListener(
    "resize",
    function() {

        camera.aspect =
        window.innerWidth / 600;

        camera.updateProjectionMatrix();

        renderer.setSize(
            window.innerWidth,
            600
        );
    }
);

</script>

</body>
</html>
""",
height=630
)