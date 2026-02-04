import streamlit as st
import subprocess
import sys
import base64
import os

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Gesture Doodle",
    layout="centered"
)

# ---------- BACKGROUND ----------
def set_bg(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Update this if your background image is in a different location
bg_path = "assets/bg.jpg"
if os.path.exists(bg_path):
    set_bg(bg_path)
else:
    st.warning(f"Background image not found at '{bg_path}'")

# ---------- UI ----------
st.markdown(
    """
    <h1 style='text-align:center; color:white;'>✋ Gesture Doodle</h1>
    <h4 style='text-align:center; color:#dddddd;'>Draw in Air using Hand Gestures</h4>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

st.markdown(
    """
    <div style="color:white; font-size:18px;">
    <b>🎮 Instructions</b><br><br>
    ☝ Index finger → Draw<br>
    🎨 Touch color image → Change color<br>
    🧽 Touch eraser → Erase<br>
    ❌ Press Q → Close camera<br>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("<br>", unsafe_allow_html=True)

if st.button("▶ Start Gesture Doodle"):
    st.info("Camera opening in separate window...")
    # Make sure 'hand_gesture_doodle.py' is in the same folder as this script
    subprocess.Popen([sys.executable, "hand_gesture_doodle.py"])

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; color:#cccccc;'>Built with Streamlit • OpenCV • MediaPipe</p>",
    unsafe_allow_html=True
)
