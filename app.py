import streamlit as st
import folium
from streamlit_folium import st_folium
import time

# 1. PAGE CONFIGURATION & THEME STYLING
st.set_page_config(page_title="ZEGA - Universal Safety Map", page_icon="🛡️", layout="wide")

# Injecting Custom CSS for Dark Matte Black & Neon Theme (Mobile Responsive Layout)
st.markdown("""
<style>
    .reportview-container, .main { background-color: #121214; color: #FFFFFF; }
    .stButton>button { background-color: #1F1F23; color: #00FF66; border: 2px solid #00FF66; border-radius: 8px; width: 100%; font-weight: bold; }
    .stButton>button:hover { background-color: #00FF66; color: #121214; }
    .css-1d391kg { background-color: #1A1A1E; }
    h1, h2, h3 { color: #00E5FF !important; font-family: 'Courier New', monospace; }
    .stAlert { background-color: #261313; border: 1px solid #FF3333; color: #FF9999; }
</style>
""", unsafe_allow_html=True)

# Session States initialization to hold app variables safely
if 'emergency_triggered' not in st.session_state:
    st.session_state.emergency_triggered = False
if 'user_lat' not in st.session_state:
    st.session_state.user_lat = 32.2396  # Mock Default Manali Lat
if 'user_lng' not in st.session_state:
    st.session_state.user_lng = 77.1887  # Mock Default Manali Lng

# 2. EMERGENCY SOS OVERLAY (ANTI-PANIC RESCUE CANVAS)
if st.session_state.emergency_triggered:
    st.markdown("<h1 style='color: #FF3333; text-align: center; font-size: 40px; animation: blinker 1s linear infinite;'>🚨 EMERGENCY SOS ACTIVE 🚨</h1>", unsafe_allow_html=True)
    st.error("CRASH DETECTED! Automatically dispatching real-time telemetry details to closest responders...")
    
    st.info(f"""
    **📡 TRANSMISSION LOGS:**\n
    - [✔] Exact GPS Coordinates Packaged: ({st.session_state.user_lat}, {st.session_state.user_lng})\n
    - [✔] Last 15 Seconds Dashcam Clip Compressed\n
    - [✔] Digital Medical Passport Included\n
    - [⏳] Routing Packet to Local Emergency Helpline 112...
    """)
    
    if st.button("❌ CANCEL FALSE ALARM"):
        st.session_state.emergency_triggered = False
        st.rerun()
    st.stop()

# 3. SIDEBAR NAVIGATION
st.sidebar.title("🛡️ ZEGA CORE")
st.sidebar.markdown("""
<div style='background-color: #1F1F23; padding: 12px; border-radius: 8px; border-left: 5px solid #00E5FF;'>
    <p style='color: #00E5FF; margin: 0; font-weight: bold;'>🌐 OFFLINE MESH READY</p>
    <p style='color: #8A8A93; margin: 0; font-size: 12px;'>5 Peer Vehicles Connected via P2P</p>
</div>
""", unsafe_allow_html=True)

app_mode = st.sidebar.radio("CHOOSE UNIVERSAL MODE", ["🏎️ Drive Mode", "⛰️ Trek Mode"])

# 4. 🏎️ DRIVE MODE MODULE
if app_mode == "🏎️ Drive Mode":
    st.title("🏎️ ZEGA DRIVE ACTIVE")
    
    # Live Dashcam Widget Status Bar
    st.markdown("""
    <div style='background-color: #1C2821; padding: 10px; border-radius: 8px; margin-bottom: 15px;'>
        <p style='color: #00FF66; margin: 0; font-weight: bold;'>📷 DASHCAM STATUS: CONNECTED & STREAMING</p>
    </div>
    """, unsafe_allow_html=True)

    # Main Dashboard Columns Layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("3D-Vibe Navigation Layer")
        
        # FIXED: Using 100% Free OpenStreetMap without any watermark or API requirements
        m = folium.Map(location=[st.session_state.user_lat, st.session_state.user_lng], zoom_start=14, tiles="OpenStreetMap")
        
        # Render a mock route overlay around the current active marker coordinates
        folium.PolyLine([
            [st.session_state.user_lat - 0.004, st.session_state.user_lng - 0.003], 
            [st.session_state.user_lat, st.session_state.user_lng], 
            [st.session_state.user_lat + 0.005, st.session_state.user_lng + 0.004]
        ], color="#00E5FF", weight=5, opacity=0.8).add_to(m)
        
        # Add primary custom vehicle marker
        folium.Marker([st.session_state.user_lat, st.session_state.user_lng], popup="Your Active Avatar", icon=folium.Icon(color="blue", icon="car", prefix="fa")).add_to(m)
        st_folium(m, width="100%", height=350, key="drive_map")

    with col2:
        st.subheader("Telemetry Hub")
        st.metric(label="⚡ CURRENT REAL-TIME SPEED", value="64 km/h")
        st.markdown("<p style='color: #00FF66; font-weight: bold;'>🔀 LANE ASSIST: STICK TO LEFT LANE</p>", unsafe_allow_html=True)
        
        # GPS Device Simulator Feature Block
        st.markdown("---")
        if st.button("📍 SIMULATE MY ACTUAL GPS"):
            # Mock coordinate drift to simulate mobile telemetry engine transition
            st.session_state.user_lat = 28.6139  # New Delhi Core Simulation Base
            st.session_state.user_lng = 77.2090
            st.success("GPS Synced! Interface updated with your physical regional telemetry.")
            st.rerun()
            
        # Wrong Way Simulation Toggle Alert
        wrong_way = st.checkbox("Simulate Wrong-Way Event")
        if wrong_way:
            st.markdown("""
            <div style='background-color: #330000; padding: 15px; border-radius: 8px; border: 2px solid #FF3333; margin-top: 10px;'>
                <h4 style='color: #FF3333; margin: 0;'>⚠️ CRASH RISK!</h4>
                <p style='color: #FF9999; margin: 5px 0 0 0;'>You entered a WRONG WAY loop! Pull over or take a U-Turn safely.</p>
            </div>
            """, unsafe_allow_html=True)

    # Primary Action Lifeline Buttons Panel
    st.markdown("### 🛠️ Lifeline Assistance Panels")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🍲 ON-THE-WAY FOOD"):
            st.success("Displaying verified Highway Dhabas & Eateries (Updated 2 mins ago)")
    with c2:
        if st.button("⛺ SAFEST STOPS"):
            st.success("Showing Clean Washrooms & Secured Parking Spaces nearby")
    with c3:
        if st.button("🚨 TRIGGER SOS CRASH LOOP", key="sos_btn"):
            st.session_state.emergency_triggered = True
            st.rerun()

# 5. ⛰️ TREK MODE MODULE (WILDERNESS)
else:
    st.title("⛰️ ZEGA TREK/WILDERNESS ACTIVE")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Topological Terrain Tracker")
        
        # FIXED: Using clean OpenStreetMap canvas for topological simulations
        m_trek = folium.Map(location=[st.session_state.user_lat, st.session_state.user_lng], zoom_start=15, tiles="OpenStreetMap")
        
        # Display sequential Neon Breadcrumb footprints tracing back paths
        folium.CircleMarker([st.session_state.user_lat - 0.002, st.session_state.user_lng - 0.002], radius=6, color='#00FF66', fill=True).add_to(m_trek)
        folium.CircleMarker([st.session_state.user_lat - 0.001, st.session_state.user_lng - 0.001], radius=6, color='#00FF66', fill=True).add_to(m_trek)
        folium.CircleMarker([st.session_state.user_lat, st.session_state.user_lng], radius=6, color='#00E5FF', fill=True).add_to(m_trek)
        
        st_folium(m_trek, width="100%", height=350, key="trek_map")
        st.caption("🟢 Green indicators track your dropped breadcrumb footprints locally without network requirements.")

    with col2:
        st.subheader("Wilderness Protocol")
        if st.button("🌲 ESCAPE TO NEAREST VILLAGE"):
            st.warning("Compass Matrix: Safe Settlement found 1.4 KM Northeast (Heading 45°).")
            
        st.markdown("---")
        st.write("📌 Mark Custom Wilderness Trail")
        trail_name = st.text_input("Enter Trail Name / Danger Note:")
        if st.button("💾 SAVE TRAIL OFFLINE"):
            if trail_name:
                st.success(f"Path '{trail_name}' cached to local internal database memory storage successfully!")
            else:
                st.error("Please enter a label note description first.")
