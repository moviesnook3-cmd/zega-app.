import streamlit as st
import folium
from streamlit_folium import st_folium
import math
import time
from datetime import datetime

# ==========================================
# 1. PAGE SETUP & CYBERPUNK/ANTI-PANIC THEME
# ==========================================
st.set_page_config(
    page_title="ZEGA // GEOSHIELD HUD",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom High-Contrast Dark Mode & HUD Styling
st.markdown(
    """
<style>
    /* Global Canvas Styling */
    .stApp {
        background-color: #0b0f19;
        color: #e0e6ed;
        font-family: 'Segoe UI', -apple-system, Roboto, sans-serif;
    }
    
    /* Top Header Bar */
    header[data-testid="stHeader"] {
        background-color: rgba(11, 15, 25, 0.9);
    }
    
    /* Sidebar Layout */
    section[data-testid="stSidebar"] {
        background-color: #070a10;
        border-right: 1px solid #1e293b;
    }

    /* Metric Containers & Cards */
    div[data-testid="stMetricValue"] {
        color: #00f2fe;
        font-family: 'Courier New', monospace;
        font-weight: 800;
    }
    
    .hud-card {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
    }
    
    /* Pulsing Neon Animations */
    @keyframes pulse-red {
        0% { box-shadow: 0 0 0 0 rgba(255, 0, 85, 0.7); }
        70% { box-shadow: 0 0 0 15px rgba(255, 0, 85, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 0, 85, 0); }
    }
    
    @keyframes pulse-green {
        0% { box-shadow: 0 0 0 0 rgba(0, 255, 136, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(0, 255, 136, 0); }
        100% { box-shadow: 0 0 0 0 rgba(0, 255, 136, 0); }
    }
    
    .sos-overlay {
        background: radial-gradient(circle, #4a000f 0%, #050002 90%);
        border: 3px solid #ff0055;
        border-radius: 14px;
        padding: 25px;
        text-align: center;
        animation: pulse-red 1.5s infinite;
        margin-bottom: 20px;
    }
    
    .wrong-way-banner {
        background: #ff0055;
        color: #ffffff;
        font-weight: 900;
        text-align: center;
        padding: 16px;
        font-size: 1.25rem;
        border-radius: 8px;
        letter-spacing: 1.5px;
        animation: pulse-red 1s infinite;
        margin-bottom: 16px;
    }

    .live-dot {
        height: 10px;
        width: 10px;
        background-color: #00ff88;
        border-radius: 50%;
        display: inline-block;
        margin-right: 6px;
        animation: pulse-green 1.2s infinite;
    }

    /* Buttons Styling */
    .stButton > button {
        border-radius: 8px;
        font-weight: 700;
        transition: all 0.2s ease-in-out;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 2. STATE MANAGEMENT & LOCAL STORAGE SETUP
# ==========================================
if "sos_active" not in st.session_state:
    st.session_state.sos_active = False

if "show_food" not in st.session_state:
    st.session_state.show_food = False

if "show_safe_stops" not in st.session_state:
    st.session_state.show_safe_stops = False

if "custom_trails" not in st.session_state:
    st.session_state.custom_trails = []

if "escape_located" not in st.session_state:
    st.session_state.escape_located = False

if "breadcrumbs" not in st.session_state:
    # Himalayan Ridge Simulation
    st.session_state.breadcrumbs = [
        {"lat": 32.2396, "lon": 77.1887, "elev": 2050},
        {"lat": 32.2415, "lon": 77.1912, "elev": 2180},
        {"lat": 32.2440, "lon": 77.1935, "elev": 2340},
        {"lat": 32.2482, "lon": 77.1970, "elev": 2510},
        {"lat": 32.2530, "lon": 77.2010, "elev": 2720},
    ]

# Local Static Settlements
SETTLEMENTS = [
    {"name": "Old Village Shelter", "lat": 32.2610, "lon": 77.1850, "type": "Shelter & Water"},
    {"name": "Forest Ranger Base", "lat": 32.2350, "lon": 77.2150, "type": "Medical & Comms"},
    {"name": "Valley Outpost Echo", "lat": 32.2280, "lon": 77.1720, "type": "Road Access"},
]

# Highway Trajectory
HIGHWAY_PATH = [
    (31.8000, 77.0500),
    (31.8500, 77.0800),
    (31.9200, 77.1100),
    (32.0000, 77.1400),
    (32.1000, 77.1650),
    (32.1800, 77.1750),
    (32.2396, 77.1887),
]

CURRENT_VEHICLE_POS = [32.1800, 77.1750]

# ==========================================
# 3. UTILITY ALGORITHMS
# ==========================================
def calculate_haversine(lat1, lon1, lat2, lon2):
    r = 6371.0  # km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def calculate_bearing(lat1, lon1, lat2, lon2):
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_lambda = math.radians(lon2 - lon1)

    y = math.sin(delta_lambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(
        phi2
    ) * math.cos(delta_lambda)
    bearing = (math.degrees(math.atan2(y, x)) + 360) % 360
    return bearing


# ==========================================
# 4. SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.markdown(
        """
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:15px;">
            <span style="font-size:2rem;">🛡️</span>
            <div>
                <h2 style="margin:0; color:#00f2fe; letter-spacing:2px; font-weight:900;">ZEGA</h2>
                <small style="color:#94a3b8;">GEOSHIELD CORE v4.2</small>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    mode = st.radio(
        "SELECT OPERATIONAL MODE",
        ["🏎️ Drive Mode", "⛰️ Trek Mode"],
        index=0,
    )

    st.markdown("---")

    st.markdown(
        """
        <div class="hud-card" style="border-left: 4px solid #00ff88;">
            <div style="font-size:0.8rem; color:#94a3b8; font-weight:700;">SECURE COMMUNICATIONS</div>
            <div style="color:#00ff88; font-weight:800; margin-top:4px;">
                <span class="live-dot"></span>OFFLINE MESH ACTIVE
            </div>
            <div style="font-size:0.85rem; color:#cbd5e1; margin-top:5px;">
                📡 <b>5 Peer Nodes</b> Connected via P2P Direct
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    col_s1, col_s2 = st.columns(2)
    col_s1.metric("BATTERY", "94%", "+Solar")
    col_s2.metric("GPS ACC", "0.8m", "RTK-LOCKED")

    st.markdown("---")
    if not st.session_state.sos_active:
        if st.button("🚨 TRIGGER EMERGENCY SOS", use_container_width=True, type="primary"):
            st.session_state.sos_active = True
            st.rerun()

# ==========================================
# 5. EMERGENCY SOS OVERLAY
# ==========================================
if st.session_state.sos_active:
    st.markdown(
        """
        <div class="sos-overlay">
            <h1 style="color:#ff0055; font-size: 2.5rem; margin:0; font-weight:900; letter-spacing:2px;">
                ⚠️ CRASH DETECTED // EMERGENCY ACTIVATED
            </h1>
            <p style="color:#ffd6e0; font-size:1.1rem; margin-top:12px; line-height:1.6;">
                Broadcasting encrypted emergency packet to <b>Helpline 112</b>, Forest Responders, and Emergency Contacts.<br>
                Payload: <b>Exact RTK GPS Fix, Digital Medical Passport (O+), and last 15s Dashcam Blackbox Buffer</b>.
            </p>
            <div style="font-size: 1.4rem; color: #ff0055; font-family: monospace; font-weight:800; margin: 15px 0;">
                AUTO-DISPATCH DISPATCHING IN: 00:08 SECONDS
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    col_sos1, col_sos2 = st.columns([2, 1])
    with col_sos1:
        st.info("ℹ️ Local siren sounding and P2P beacon relay broadcasting on 433MHz Mesh.")
    with col_sos2:
        if st.button("❌ CANCEL FALSE ALARM", use_container_width=True):
            st.session_state.sos_active = False
            st.rerun()

    st.markdown("---")

# ==========================================
# 6. DRIVE MODE
# ==========================================
if mode == "🏎️ Drive Mode":
    st.markdown("### 🏎️ TACTICAL DRIVE HUD // HIGH-SPEED ACTIVE MONITORING")

    top_col1, top_col2, top_col3 = st.columns([1.2, 1.2, 1.6])

    with top_col1:
        st.markdown(
            """
            <div class="hud-card" style="display:flex; align-items:center; justify-content:space-between;">
                <div>
                    <div style="font-size:0.75rem; color:#94a3b8;">EDGE AI DASHCAM</div>
                    <div style="font-weight:700; color:#ffffff; margin-top:2px;">
                        <span class="live-dot"></span>STREAMING (1080p 60FPS)
                    </div>
                </div>
                <div style="font-size:1.4rem;">📷</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with top_col2:
        st.markdown(
            """
            <div class="hud-card" style="border-left: 4px solid #00f2fe;">
                <div style="font-size:0.75rem; color:#94a3b8;">3D LANE ASSISTANT</div>
                <div style="font-weight:800; color:#00f2fe; margin-top:2px;">
                    🛡️ STICK TO LEFT LANE (OPTIMAL)
                </div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with top_col3:
        wrong_way_sim = st.checkbox(
            "⚠️ Simulate Wrong-Way Driving Hazard",
            value=False,
        )

    if wrong_way_sim:
        st.markdown(
            """
            <div class="wrong-way-banner">
                🚨 CRASH RISK WARNING! YOU ARE DRIVING THE WRONG WAY! PLEASE MAKE A SAFE U-TURN IMMEDIATELY!
            </div>
        """,
            unsafe_allow_html=True,
        )

    drive_map = folium.Map(
        location=CURRENT_VEHICLE_POS,
        zoom_start=11,
        tiles="CartoDB dark_matter",
    )

    folium.PolyLine(
        HIGHWAY_PATH,
        color="#00f2fe",
        weight=4,
        opacity=0.85,
        tooltip="National Highway NH-3 Route",
    ).add_to(drive_map)

    folium.Marker(
        location=CURRENT_VEHICLE_POS,
        popup="<b>YOU (Current Position)</b><br>Speed: 84 km/h<br>Heading: 015° NNE",
        icon=folium.Icon(color="blue", icon="arrow-up", prefix="fa"),
    ).add_to(drive_map)

    folium.CircleMarker(
        location=[32.0500, 77.1500],
        radius=9,
        color="#ffcc00",
        fill=True,
        fill_color="#ffcc00",
        fill_opacity=0.6,
        popup="⚠️ Sharp Hairpin Curve Ahead (Speed Advisory: 40 km/h)",
    ).add_to(drive_map)

    if st.session_state.show_food:
        folium.Marker(
            location=[32.1400, 77.1680],
            popup="🍲 <b>Local Dhaba & Fresh Food</b><br>Freshness: <i>2 mins ago</i>",
            icon=folium.Icon(color="green", icon="cutlery", prefix="fa"),
        ).add_to(drive_map)

    if st.session_state.show_safe_stops:
        folium.Marker(
            location=[32.1100, 77.1620],
            popup="⛺ <b>Verified Safe Stop Bay</b><br>Illuminated, 24/7 Security",
            icon=folium.Icon(color="cadetblue", icon="shield", prefix="fa"),
        ).add_to(drive_map)

    st_folium(drive_map, height=480, use_container_width=True)

    c_m1, c_m2, c_m3, c_btn1, c_btn2 = st.columns([1, 1, 1, 1.2, 1.2])
    c_m1.metric("SPEED", "84 KM/H", "Optimal")
    c_m2.metric("CURRENT ROAD", "NH-3 Express", "Flow Normal")
    c_m3.metric("NEXT HAZARD", "2.8 km", "Hairpin")

    with c_btn1:
        if st.button("🍲 On-The-Way Food", use_container_width=True):
            st.session_state.show_food = not st.session_state.show_food
            st.rerun()

    with c_btn2:
        if st.button("⛺ Safest Stops", use_container_width=True):
            st.session_state.show_safe_stops = not st.session_state.show_safe_stops
            st.rerun()

# ==========================================
# 7. TREK MODE
# ==========================================
else:
    st.markdown("### ⛰️ TREK MODE // TOPOLOGICAL OFFLINE SAFETY ENGINE")

    user_trek_pos = st.session_state.breadcrumbs[-1]
    u_lat, u_lon = user_trek_pos["lat"], user_trek_pos["lon"]

    trek_map = folium.Map(
        location=[u_lat, u_lon],
        zoom_start=13,
        tiles="OpenStreetMap",
    )

    breadcrumb_coords = [[b["lat"], b["lon"]] for b in st.session_state.breadcrumbs]
    folium.PolyLine(
        breadcrumb_coords,
        color="#00ff88",
        weight=3,
        dash_array="5, 8",
        tooltip="Digital Breadcrumb Trail",
    ).add_to(trek_map)

    for idx, pt in enumerate(st.session_state.breadcrumbs[:-1]):
        folium.CircleMarker(
            location=[pt["lat"], pt["lon"]],
            radius=4,
            color="#00ff88",
            fill=True,
            fill_color="#00ff88",
            popup=f"Waypoint #{idx+1} | Elev: {pt['elev']}m",
        ).add_to(trek_map)

    folium.Marker(
        location=[u_lat, u_lon],
        popup=f"<b>YOU (Trekker)</b><br>Elevation: {user_trek_pos['elev']}m",
        icon=folium.Icon(color="red", icon="user", prefix="fa"),
    ).add_to(trek_map)

    for trail in st.session_state.custom_trails:
        folium.Marker(
            location=[trail["lat"], trail["lon"]],
            popup=f"📍 <b>{trail['name']}</b><br>Notes: {trail['notes']}",
            icon=folium.Icon(color="purple", icon="flag", prefix="fa"),
        ).add_to(trek_map)

    nearest_settlement = None
    min_dist = float("inf")
    escape_bearing = 0.0

    for s in SETTLEMENTS:
        d = calculate_haversine(u_lat, u_lon, s["lat"], s["lon"])
        if d < min_dist:
            min_dist = d
            nearest_settlement = s
            escape_bearing = calculate_bearing(u_lat, u_lon, s["lat"], s["lon"])

        folium.Marker(
            location=[s["lat"], s["lon"]],
            popup=f"🏠 <b>{s['name']}</b><br>Type: {s['type']}",
            icon=folium.Icon(color="orange", icon="home", prefix="fa"),
        ).add_to(trek_map)

    if st.session_state.escape_located and nearest_settlement:
        folium.PolyLine(
            [[u_lat, u_lon], [nearest_settlement["lat"], nearest_settlement["lon"]]],
            color="#ff0055",
            weight=4,
            dash_array="6, 6",
            tooltip=f"ESCAPE VECTOR: {min_dist:.2f} km @ {escape_bearing:.0f}°",
        ).add_to(trek_map)

    st_folium(trek_map, height=450, use_container_width=True)

    t_col1, t_col2 = st.columns([1.2, 1.8])

    with t_col1:
        st.markdown(
            """
            <div class="hud-card">
                <div style="font-weight:700; color:#00f2fe; margin-bottom:8px;">🧭 INERTIAL ESCAPE VECTOR</div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("🌲 Locate Nearest Escape Route", use_container_width=True):
            st.session_state.escape_located = True
            st.rerun()

        if st.session_state.escape_located and nearest_settlement:
            st.markdown(
                f"""
                <div style="margin-top:10px; padding:10px; background:#1e293b; border-radius:6px;">
                    <div style="font-size:0.8rem; color:#94a3b8;">TARGET SETTLEMENT</div>
                    <div style="font-size:1.1rem; font-weight:800; color:#ffcc00;">{nearest_settlement['name']}</div>
                    <div style="display:flex; justify-content:space-between; margin-top:6px; font-family:monospace;">
                        <span>DIST: <b>{min_dist:.2f} km</b></span>
                        <span>BEARING: <b>{escape_bearing:.0f}° NNE</b></span>
                    </div>
                </div>
            """,
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with t_col2:
        with st.expander("📍 Pin New Unmapped Trail / Memory Point", expanded=True):
            f_col1, f_col2 = st.columns(2)
            trail_name = f_col1.text_input("Trail / Landmark Name", value="Secret Ridge Point")
            trail_notes = f_col2.text_input("Hazards / Water Source Notes", value="Clean mountain spring")
            photo_file = st.file_uploader("Attach Offline Reference Photo (Simulated)", type=["jpg", "png"])

            if st.button("💾 Store Trail to Offline Memory", use_container_width=True):
                new_lat = u_lat + 0.003
                new_lon = u_lon + 0.002
                st.session_state.custom_trails.append(
                    {
                        "name": trail_name,
                        "notes": trail_notes,
                        "lat": new_lat,
                        "lon": new_lon,
                        "timestamp": datetime.now().strftime("%H:%M:%S"),
                    }
                )
                st.success(f"Pinned '{trail_name}' at [{new_lat:.4f}, {new_lon:.4f}]. Stored locally.")
                time.sleep(0.5)
                st.rerun()
