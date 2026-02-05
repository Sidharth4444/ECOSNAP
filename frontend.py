import streamlit as st
import pandas as pd
import os
import math
import hashlib
import requests  # NEW

# --- Page Setup ---
st.set_page_config(page_title="EcoSnap", page_icon="🌱", layout="centered")

DATA_FILE = "data.csv"
BACKEND_URL = "http://localhost:5000"  # NEW

POINTS_MAP = {
    "Recycling ♻": 10,
    "Tree Planting 🌳": 20,
    "Beach Cleanup 🏖": 25,
    "Energy Saving 💡": 15,
    "Water Conservation 💧": 15,
    "Cycling 🚲": 12,
    "Composting 🌱": 18,
    "Eco-Friendly Shopping 🛍": 10
}

REWARD_MILESTONE = 50

REWARDS_LIST = [
    "🎁 $5 eco-shop voucher",
    "🎉 1-month GreenLiving magazine subscription",
    "💵 $10 cashback",
    "🌿 Eco-friendly product discount coupon",
    "♻ Special recycling kit",
]

# Load leaderboard from backend instead of local file # NEW
try:
    leaderboard = pd.read_json(requests.get(f"{BACKEND_URL}/leaderboard").text)  # NEW
except:
    leaderboard = pd.DataFrame(columns=["Name", "Action", "Points", "Photo"])

CONFLICTING_KEYWORDS = {
    "Recycling ♻": ["rocket", "fire", "smoke"],
    "Tree Planting 🌳": ["trash", "waste", "pollution"],
    "Beach Cleanup 🏖": ["rocket", "fire"],
    "Energy Saving 💡": ["trash", "waste", "pollution"],
    "Water Conservation 💧": ["rocket", "fire"],
    "Cycling 🚲": ["trash", "waste", "pollution"],
    "Composting 🌱": ["rocket", "fire", "smoke"],
    "Eco-Friendly Shopping 🛍": ["rocket", "fire", "smoke"]
}

ACTION_KEYWORDS = {
    "Recycling ♻": ["recycle", "bin", "trash", "waste", "plastic"],
    "Tree Planting 🌳": ["tree", "planting", "sapling", "garden", "forest"],
    "Beach Cleanup 🏖": ["beach", "cleanup", "sea", "shore", "litter"],
    "Energy Saving 💡": ["energy", "bulb", "light", "saving", "electricity"],
    "Water Conservation 💧": ["water", "conservation", "tap", "drip", "saving"],
    "Cycling 🚲": ["cycle", "bike", "bicycle", "cycling"],
    "Composting 🌱": ["compost", "composting", "soil", "organic"],
    "Eco-Friendly Shopping 🛍": ["shopping", "bag", "eco", "market", "store"]
}

def is_photo_conflicting(uploaded_file, selected_action):
    fname = uploaded_file.name.lower()
    conflict_words = CONFLICTING_KEYWORDS.get(selected_action, [])
    return any(word in fname for word in conflict_words)

def is_photo_matching_action(uploaded_file, selected_action):
    fname = uploaded_file.name.lower()
    keywords = ACTION_KEYWORDS.get(selected_action, [])
    return any(kw in fname for kw in keywords)

if "last_submission_hash" not in st.session_state:
    st.session_state.last_submission_hash = None

def hash_submission(name, action, photo_bytes):
    hasher = hashlib.sha256()
    hasher.update(name.encode('utf-8'))
    hasher.update(action.encode('utf-8'))
    hasher.update(photo_bytes)
    return hasher.hexdigest()

st.markdown("<h1 style='text-align: center; color: green;'>EcoSnap 🌱 — Capture, Earn, Compete!</h1>", unsafe_allow_html=True)
st.write("")

name = st.text_input("👤 Enter your name:")
uploaded_file = st.file_uploader("📤 Upload your eco-action photo", type=["jpg", "jpeg", "png"])
action = st.selectbox("🌟 Select your action type", list(POINTS_MAP.keys()))

if st.button("✅ Submit Action"):
    if name and uploaded_file and action:
        photo_bytes = uploaded_file.read()
        current_hash = hash_submission(name, action, photo_bytes)

        if st.session_state.last_submission_hash == current_hash:
            st.error("❌ You have already submitted this exact action and photo. Please try something new.")
        else:
            st.session_state.last_submission_hash = current_hash

            if is_photo_conflicting(uploaded_file, action):
                st.error(f"❌ The photo filename contains conflicting keywords that do not match the action '{action}'. Please upload a correct photo.")
            elif not is_photo_matching_action(uploaded_file, action):
                st.error("❌ Uploaded photo does not match the selected action. Please upload a correct photo.")
            else:
                points = POINTS_MAP[action]
                st.success(f"🎉 {name}, your action '{action}' earned you {points} points!")

                # Send data to backend # NEW
                try:
                    files = {"photo": uploaded_file}
                    data = {"name": name, "action": action, "points": points}
                    requests.post(f"{BACKEND_URL}/submit", data=data, files=files)
                except Exception as e:
                    st.error(f"Backend error: {e}")

                st.image(photo_bytes, caption=f"{action} by {name}", use_container_width=True)
                st.balloons()
    else:
        st.warning("Please enter your name, upload a photo, and select your action.")

# Leaderboard display
st.subheader("🏆 Leaderboard")
if not leaderboard.empty:
    leaderboard_display = leaderboard.groupby("Name")["Points"].sum().reset_index()
    leaderboard_display = leaderboard_display.sort_values(by="Points", ascending=False)
    st.table(leaderboard_display)

    st.subheader("🎯 Your Badge & Rewards")
    if name in leaderboard_display["Name"].values:
        total_points = leaderboard_display.loc[leaderboard_display["Name"] == name, "Points"].values[0]
        if total_points < 30:
            st.info("🌱 Eco Starter")
        elif total_points < 60:
            st.success("🌿 Green Hero")
        else:
            st.warning("🌍 Planet Guardian")

        next_milestone = (math.floor(total_points / REWARD_MILESTONE) + 1) * REWARD_MILESTONE
        points_towards_next = total_points % REWARD_MILESTONE
        progress = points_towards_next / REWARD_MILESTONE
        st.write(f"Points: {total_points} | Next reward at {next_milestone} points")
        st.progress(progress)

        rewards_earned = total_points // REWARD_MILESTONE
        if rewards_earned > 0:
            st.subheader("🎉 Rewards you've earned:")
            for i in range(rewards_earned):
                reward = REWARDS_LIST[i % len(REWARDS_LIST)]
                st.success(f"{reward} (at {REWARD_MILESTONE * (i+1)} points)")
else:
    st.write("No actions submitted yet. Be the first!")
