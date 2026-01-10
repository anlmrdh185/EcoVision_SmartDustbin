import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import pandas as pd
import time
from datetime import datetime
import plotly.express as px 

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="EcoVision Recycle Bin",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .big-font { font-size: 20px !important; }
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- CONNECT TO FIREBASE ---
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json.json") 
    # REPLACE WITH YOUR URL IF NEEDED
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://smartdustbin-61ec7-default-rtdb.firebaseio.com/' 
    })

# --- SIDEBAR (CONTROLS) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3299/3299908.png", width=100)
    st.title("⚙️ System Status")
    
    # Status Indicators
    status_placeholder = st.empty()
    last_update_placeholder = st.empty()
    
    st.divider()
    st.write("### 🎛 Controls")
    auto_refresh = st.checkbox('Auto-Refresh Data', value=True)
    refresh_rate = st.slider('Refresh Rate (sec)', 1, 10, 2)
    
    st.info("💡 Tip: Recycle Plastic bottles to level up faster!")

# --- MAIN DASHBOARD LAYOUT ---
st.title("♻️ Smart Dustbin Analytics")
st.markdown("Real-time monitoring of waste classification and usage trends.")

# Create Tabs
tab1, tab2, tab3 = st.tabs(["📊 Dashboard Overview", "📅 Trends & History", "📥 Export Data"])

# --- TAB 1: DASHBOARD PLACEHOLDERS ---
with tab1:
    # Row 1: Key Metrics (Changed to 3 Columns)
    col1, col2, col3 = st.columns(3)
    with col1: metric_total = st.empty()
    with col2: metric_accuracy = st.empty()
    with col3: metric_peak = st.empty()

    st.divider()
    
    # Row 2: Charts & Gamification
    c1, c2 = st.columns([2, 1])
    with c1: 
        st.subheader("🗑️ Waste Composition")
        chart_placeholder = st.empty()
    with c2:
        st.subheader("🏆 Recycling Level")
        level_placeholder = st.empty()
        progress_bar = st.empty()
        badge_placeholder = st.empty()

# --- TAB 2: HISTORY PLACEHOLDERS ---
with tab2:
    st.subheader("📈 Activity Over Time")
    trend_chart_placeholder = st.empty()
    
    st.subheader("📝 Recent Logs")
    table_placeholder = st.empty()

# --- MAIN LOOP ---
while True:
    if not auto_refresh:
        time.sleep(1)
        continue

    try:
        # 1. Fetch ALL Data from Firebase
        ref = db.reference('SmartBin_Logs')
        data = ref.get()

        if data:
            # 2. Convert JSON to Pandas DataFrame
            df = pd.DataFrame.from_dict(data, orient='index')
            
            # 3. Process Timestamps
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values(by='timestamp', ascending=False)
            
            # 4. CALCULATE LIFETIME TOTALS
            # We count every row in the database history
            c_plastic = len(df[df['category'].astype(str).str.contains("Plastic", case=False)])
            c_paper = len(df[df['category'].astype(str).str.contains("Paper", case=False)])
            c_metal = len(df[df['category'].astype(str).str.contains("Metal", case=False)])
            
            total_items = c_plastic + c_paper + c_metal

            # 5. UPDATE SYSTEM STATUS (Active/Idle)
            latest_time = df.iloc[0]['timestamp']
            seconds_ago = (datetime.now() - latest_time).total_seconds()
            
            if seconds_ago < 30:
                status_placeholder.success("🟢 ONLINE & ACTIVE")
            else:
                status_placeholder.warning("🟡 IDLE / STANDBY")
            
            last_update_placeholder.caption(f"Last Update: {datetime.now().strftime('%H:%M:%S')}")

            # --- UPDATE UI ELEMENTS ---

            # Metrics
            with metric_total:
                st.metric("Lifetime Recycled", total_items, delta="Items")
            
            with metric_accuracy:
                if 'confidence' in df.columns:
                    clean_conf = df['confidence'].astype(str).str.replace('%','').astype(float)
                    avg_conf = clean_conf.mean()
                    st.metric("Avg AI Accuracy", f"{int(avg_conf)}%")
                else:
                     st.metric("Avg AI Accuracy", "N/A")

            with metric_peak:
                mats = {'Plastic': c_plastic, 'Paper': c_paper, 'Metal': c_metal}
                top_item = max(mats, key=mats.get) if total_items > 0 else "None"
                st.metric("Top Category", top_item)

            # Pie Chart
            if total_items > 0:
                fig = px.pie(
                    names=['Plastic', 'Paper', 'Metal'], 
                    values=[c_plastic, c_paper, c_metal], 
                    hole=0.5,
                    color_discrete_sequence=px.colors.sequential.RdBu
                )
                chart_placeholder.plotly_chart(fig, use_container_width=True)
            else:
                chart_placeholder.info("No recycling data yet.")

            # Gamification
            level = (total_items // 20) + 1
            progress = (total_items % 20) / 20
            level_placeholder.markdown(f"### 🎖️ Level: **{level}**")
            progress_bar.progress(progress)
            badge_placeholder.write(f"Next Rank: {20 - (total_items % 20)} items to go!")

            # Trends Chart (Activity per Hour)
            if not df.empty:
                df['Hour'] = df['timestamp'].dt.strftime('%H:00')
                trend_data = df.groupby('Hour').size()
                trend_chart_placeholder.line_chart(trend_data)

            # Recent Logs Table
            display_cols = ['timestamp', 'category', 'confidence']
            valid_cols = [c for c in display_cols if c in df.columns]
            table_placeholder.dataframe(df[valid_cols].head(10), use_container_width=True)

            # --- EXPORT DATA (Tab 3) ---
            with tab3:
                st.write("Download the full database history for reports.")
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Full CSV Report",
                    data=csv,
                    file_name='smartbin_history.csv',
                    mime='text/csv',
                )

        else:
            st.warning("⚠️ Database connected but found NO DATA in 'SmartBin_Logs'.")
            st.info("Check: Did you run the Python AI script yet?")

    except Exception as e:
        # st.error(f"Error: {e}") 
        pass

    # Refresh

    time.sleep(refresh_rate)
