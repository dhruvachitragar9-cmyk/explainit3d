import streamlit as st
import streamlit.components.v1 as components

st.title("Component Test")

components.html(
    """
    <div style="
        background: #222;
        color: white;
        padding: 50px;
        font-size: 30px;
        text-align: center;
    ">
        ✅ HTML COMPONENT WORKS
    </div>
    """,
    height=200
)