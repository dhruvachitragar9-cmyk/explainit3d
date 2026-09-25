import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="ExplainIt3D",
    layout="wide"
)

st.title("🌎 ExplainIt3D")
st.write("Interactive 3D model test")

html = """
<!DOCTYPE html>
<html>
<head>

<script type="importmap">
{
    "imports": {
        "three": "https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.js",
        "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/"
    }
}
</script>

<style>

body {
    margin: 0;
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

<script type="module">

import * as THREE from "three";

import { OrbitControls } from
"https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/controls/OrbitControls.js";

import { GLTFLoader } from
"https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/loaders/GLTFLoader.js";


const container = document.getElementById("viewer");


/* ------------------------------------------------
   SCENE
------------------------------------------------ */

const scene = new THREE.Scene();

scene.background = new THREE.Color(0x111111);


/* ------------------------------------------------
   CAMERA
------------------------------------------------ */

const camera = new THREE.PerspectiveCamera(
    45,
    container.clientWidth / container.clientHeight,
    0.1,
    1000
);

camera.position.set(
    3,
    2,
    5
);


/* ------------------------------------------------
   RENDERER
------------------------------------------------ */

const renderer = new THREE.WebGLRenderer({
    antialias: true
});

renderer.setPixelRatio(
    window.devicePixelRatio
);

renderer.setSize(
    container.clientWidth,
    container.clientHeight
);

container.appendChild(
    renderer.domElement
);


/* ------------------------------------------------
   LIGHT
------------------------------------------------ */

const light1 = new THREE.HemisphereLight(
    0xffffff,
    0x444444,
    3
);

scene.add(light1);


const light2 = new THREE.DirectionalLight(
    0xffffff,
    3
);

light2.position.set(
    5,
    5,
    5
);

scene.add(light2);


/* ------------------------------------------------
   CONTROLS
------------------------------------------------ */

const controls = new OrbitControls(
    camera,
    renderer.domElement
);

controls.enableDamping = true;

controls.autoRotate = true;

controls.autoRotateSpeed = 0.7;


/* ------------------------------------------------
   LOAD 3D MODEL
------------------------------------------------ */

const loader = new GLTFLoader();


const MODEL_URL =
"https://threejs.org/examples/models/gltf/DamagedHelmet/glTF/DamagedHelmet.gltf";


loader.load(

    MODEL_URL,

    function(gltf) {

        const model = gltf.scene;

        scene.add(model);

        model.scale.set(
            2,
            2,
            2
        );

    },

    function(xhr) {

        console.log(
            "Loading:",
            (xhr.loaded / xhr.total * 100) + "%"
        );

    },

    function(error) {

        console.error(
            "Model loading error:",
            error
        );

    }

);


/* ------------------------------------------------
   RESIZE
------------------------------------------------ */

window.addEventListener(
    "resize",
    function() {

        camera.aspect =
            container.clientWidth /
            container.clientHeight;

        camera.updateProjectionMatrix();

        renderer.setSize(
            container.clientWidth,
            container.clientHeight
        );

    }
);


/* ------------------------------------------------
   ANIMATION
------------------------------------------------ */

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

</script>

</body>
</html>
"""

components.html(
    html,
    height=650
)
