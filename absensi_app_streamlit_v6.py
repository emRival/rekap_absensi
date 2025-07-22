import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Smart Attendance Monitor",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    /* Sidebar styling and width adjustment */
    .css-1d391kg {
        width: 400px !important;
        min-width: 400px !important;
    }
    
    .css-1cypcdb {
        width: 400px !important;
        min-width: 400px !important;
    }
    
    section[data-testid="stSidebar"] {
        width: 400px !important;
        min-width: 400px !important;
    }
    
    .sidebar .sidebar-content {
        width: 400px !important;
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Main content area adjustment */
    .main .block-container {
        max-width: calc(100% - 420px);
        padding-left: 2rem;
    }
    
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    
    /* Enhanced sidebar styling */
    .stSelectbox > div > div {
        border-radius: 10px;
        border: 2px solid #e6e9ef;
        background-color: white;
    }
    
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e6e9ef;
        padding: 0.5rem;
    }
    
    .stNumberInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e6e9ef;
        padding: 0.5rem;
    }
    
    /* Sidebar headers */
    .sidebar h3 {
        color: #495057;
        font-weight: 600;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #667eea;
    }
    
    /* File uploader styling */
    .stFileUploader > div > div {
        border-radius: 10px;
        border: 2px dashed #667eea;
        background-color: #f8f9fa;
        padding: 1rem;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    .status-badge {
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.8rem;
        margin: 0.2rem;
        display: inline-block;
    }
    
    .status-excellent { background-color: #d4edda; color: #155724; }
    .status-good { background-color: #d1ecf1; color: #0c5460; }
    .status-warning { background-color: #fff3cd; color: #856404; }
    .status-danger { background-color: #f8d7da; color: #721c24; }
    
    /* Sidebar expander styling */
    .streamlit-expanderHeader {
        background-color: #e9ecef;
        border-radius: 8px;
        padding: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    /* Better spacing for sidebar content */
    .sidebar .element-container {
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Modern header
st.markdown("""
<div class="main-header">
    <h1>🎯 SMART ATTENDANCE MONITORING</h1>
    <p style="font-size: 1.2rem; margin: 0; opacity: 0.9;">
        Advanced Analytics & Real-time Insights Dashboard
    </p>
</div>
""", unsafe_allow_html=True)

# Role and time settings with modern sidebar configuration
with st.sidebar:
    st.markdown("### ⚙️ **Configuration Panel**")
    st.markdown("---")
    
    # Role time configuration with improved layout
    with st.expander("🕐 **Work Schedule Settings**", expanded=False):
        role_settings = {
            "SMPSMK": {"jam_masuk": "07:00", "jam_pulang": "15:00", "pulang_next_day": False},
            "ASRAMA": {"jam_masuk": "15:00", "jam_pulang": "07:00", "pulang_next_day": True},
            "MUSYRIF": {"jam_masuk": "15:00", "jam_pulang": "07:00", "pulang_next_day": True}
        }
        
        for role in role_settings:
            st.markdown(f"#### **{role} Schedule**")
            
            # Use wider columns in the larger sidebar
            col1, col2 = st.columns([1, 1])
            with col1:
                role_settings[role]["jam_masuk"] = st.text_input(
                    "⏰ Check In Time", 
                    value=role_settings[role]["jam_masuk"], 
                    key=f"masuk_{role}", 
                    help=f"Start time for {role} role"
                )
            with col2:
                suffix = " (Next Day)" if role_settings[role]["pulang_next_day"] else ""
                role_settings[role]["jam_pulang"] = st.text_input(
                    f"🏁 Check Out Time{suffix}", 
                    value=role_settings[role]["jam_pulang"], 
                    key=f"pulang_{role}", 
                    help=f"End time for {role} role"
                )
            st.markdown("---")
    
    # Date range selection with enhanced styling
    st.markdown("### 📅 **Period Selection**")
    st.markdown("*Choose the analysis period for attendance data*")
    
    bulan_map = {
        "January": 1, "February": 2, "March": 3, "April": 4,
        "May": 5, "June": 6, "July": 7, "August": 8,
        "September": 9, "October": 10, "November": 11, "December": 12
    }
    
    # Better month selection layout
    st.markdown("**📈 Analysis Period:**")
    col1, col2 = st.columns(2)
    with col1:
        bulan_awal = st.selectbox(
            "�️ Start Month", 
            list(bulan_map.keys()), 
            index=5,
            help="Select the starting month for analysis"
        )
    with col2:
        bulan_akhir = st.selectbox(
            "� End Month", 
            list(bulan_map.keys()), 
            index=6,
            help="Select the ending month for analysis"
        )
    
    # Year selection with better styling
    tahun = st.number_input(
        "🗓️ **Analysis Year**", 
        value=datetime.now().year, 
        step=1, 
        min_value=2020, 
        max_value=2030,
        help="Select the year for attendance analysis"
    )
    
    st.markdown("---")
    
    # File upload section with enhanced design
    st.markdown("### 📂 **File Upload**")
    st.markdown("*Upload your Excel attendance file*")
    
    uploaded_file = st.file_uploader(
        "📋 **Select Attendance File (.xlsx)**", 
        type=["xlsx"],
        help="Upload your Excel attendance file for comprehensive analysis",
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        st.success("✅ File uploaded successfully!")
        st.info(f"📄 **File:** {uploaded_file.name}")
    
    st.markdown("---")
    
    # Quick help section
    with st.expander("ℹ️ **Quick Help**", expanded=False):
        st.markdown("""
        **📋 File Requirements:**
        - Excel format (.xlsx)
        - Standard attendance template
        - Employee names in column A
        - Roles in column B
        - Daily attendance data starting from column C
        
        **🕐 Time Formats Supported:**
        - HH:MM (e.g., 07:30)
        - HH.MM.SS (e.g., 07.30.00)
        - Multiple entries per cell
        
        **📊 Analysis Features:**
        - Automatic role detection
        - Performance scoring
        - Detailed breakdowns
        - Export capabilities
        """)

def get_performance_badge(issues_count, total_days):
    """Generate performance badge based on attendance issues"""
    if total_days == 0:
        return "status-warning", "No Data"
    
    issue_rate = issues_count / total_days
    if issue_rate == 0:
        return "status-excellent", "Excellent"
    elif issue_rate <= 0.1:
        return "status-good", "Good"
    elif issue_rate <= 0.3:
        return "status-warning", "Needs Attention"
    else:
        return "status-danger", "Poor"

def create_summary_metrics(df_hasil):
    """Create summary metrics for dashboard"""
    total_employees = len(df_hasil)
    total_absences = df_hasil['Tidak Absen'].sum()
    total_late = df_hasil['Telat Masuk'].sum()
    total_early_leave = df_hasil['Pulang Cepat'].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="👥 Total Employees",
            value=total_employees,
            help="Total number of employees in the system"
        )
    
    with col2:
        st.metric(
            label="❌ Total Absences",
            value=total_absences,
            delta=f"{total_absences/total_employees:.1f} avg per employee" if total_employees > 0 else "0",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            label="⏰ Late Check-ins",
            value=total_late,
            delta=f"{total_late/total_employees:.1f} avg per employee" if total_employees > 0 else "0",
            delta_color="inverse"
        )
    
    with col4:
        st.metric(
            label="🏃‍♂️ Early Departures",
            value=total_early_leave,
            delta=f"{total_early_leave/total_employees:.1f} avg per employee" if total_employees > 0 else "0",
            delta_color="inverse"
        )

def parse_jam(cell):
    """Parse time entries from cell data"""
    if pd.isna(cell): 
        return []
    
    cell = str(cell).strip().lower()
    
    # If cell is empty after stripping
    if not cell:
        return []
    
    # Check for holiday marker
    if 'l' in cell: 
        return ['L']
    
    # Split by newlines and filter only valid time entries
    jam_entries = cell.replace('\n', '\n').split('\n')
    valid_times = []
    
    for entry in jam_entries:
        entry = entry.strip()
        
        # Check for time format with colon (:) or dot (.)
        if (':' in entry or '.' in entry):
            # Replace dots with colons for standardization
            normalized_entry = entry.replace('.', ':')
            time_parts = normalized_entry.split(':')
            
            # Support HH:MM or HH:MM:SS format
            if len(time_parts) >= 2:
                try:
                    hours = time_parts[0]
                    minutes = time_parts[1]
                    
                    # Validate if hours and minutes are digits
                    if hours.isdigit() and minutes.isdigit():
                        hour_int = int(hours)
                        minute_int = int(minutes)
                        
                        # Validate time range
                        if 0 <= hour_int <= 23 and 0 <= minute_int <= 59:
                            # Format to HH:MM (ignore seconds if present)
                            formatted_time = f"{hour_int:02d}:{minute_int:02d}"
                            valid_times.append(formatted_time)
                except:
                    continue
    
    return valid_times

def valid_jam_smpsmk(jam_list):
    """Extract valid check-in and check-out times for SMPSMK role"""
    masuk = None
    pulang = None
    for jam in jam_list:
        if jam >= "00:00" and masuk is None:
            masuk = jam
        pulang = jam  # Take the last time as check-out
    return masuk, pulang

if uploaded_file:
    with st.spinner("🔄 Processing attendance data..."):
        df = pd.read_excel(uploaded_file, header=None)

        # Process date headers
        tanggal_header = df.iloc[4, 2:].tolist()
        tanggal_final = []
        bulan_aktif = bulan_map[bulan_awal]
        current_bulan = bulan_aktif

        for i, val in enumerate(tanggal_header):
            try:
                tgl = int(val)
                if i > 0 and int(tanggal_header[i]) < int(tanggal_header[i-1]):
                    current_bulan = bulan_map[bulan_akhir]
                tanggal_final.append(datetime(tahun, current_bulan, tgl))
            except:
                tanggal_final.append(None)

        nama_guru = df.iloc[5:, 0].dropna().tolist()
        role_guru = df.iloc[5:, 1].tolist()
        data_absensi = df.iloc[5:, 2:2+len(tanggal_final)].values.tolist()

        hasil = []

        # Process each employee
        progress_bar = st.progress(0)
        debug_info = []  # For debugging purposes
        
        for idx, (nama, role, baris_absen) in enumerate(zip(nama_guru, role_guru, data_absensi)):
            progress_bar.progress((idx + 1) / len(nama_guru))
            
            role = role.strip().upper() if isinstance(role, str) else "SMPSMK"
            
            # Set default role if not in predefined roles
            if role not in role_settings:
                role = "SMPSMK"
                
            tdk_absen, absen_kurang, absen_bermasalah = [], [], []
            telat_masuk, pulang_cepat = [], []

            for i, (tgl, isi) in enumerate(zip(tanggal_final, baris_absen)):
                if not tgl:
                    continue
                jam_list = parse_jam(isi)
                if 'L' in jam_list:
                    continue

                if role == "SMPSMK":
                    # Debug info for SMPSMK incomplete records
                    if len(jam_list) == 1:
                        debug_info.append({
                            'nama': nama,
                            'role': role,
                            'tanggal': tgl.strftime("%d-%b"),
                            'isi_cell': str(isi),
                            'jam_parsed': jam_list,
                            'total_entries': len(jam_list),
                            'kategori': 'Absen Tidak Lengkap'
                        })
                    
                    if len(jam_list) == 0:
                        tdk_absen.append(tgl)
                    elif len(jam_list) == 1:
                        # Hanya 1 waktu absen = absen tidak lengkap
                        absen_kurang.append(tgl)
                    else:
                        masuk, pulang = valid_jam_smpsmk(jam_list)
                        jam_masuk_batas = role_settings[role]["jam_masuk"]
                        jam_pulang_batas = role_settings[role]["jam_pulang"]
                        
                        if not masuk or not pulang:
                            absen_kurang.append(tgl)
                        else:
                            if masuk > jam_masuk_batas:
                                telat_masuk.append(tgl)
                            if pulang < jam_pulang_batas:
                                pulang_cepat.append(tgl)
                        if len(jam_list) > 2:
                            absen_bermasalah.append(tgl)

                elif role == "ASRAMA" or role == "MUSYRIF":
                    jam_besok = parse_jam(data_absensi[idx][i+1]) if i+1 < len(baris_absen) and i+1 < len(data_absensi[idx]) else []
                    jam_hari_ini = parse_jam(isi)
                    
                    # Skip if holiday markers found
                    if 'L' in jam_hari_ini or 'L' in jam_besok:
                        continue
                    
                    # Debug info for ASRAMA/MUSYRIF incomplete records
                    total_entries = len(jam_hari_ini) + len(jam_besok)
                    if total_entries == 1:
                        debug_info.append({
                            'nama': nama,
                            'role': role,
                            'tanggal': tgl.strftime("%d-%b"),
                            'isi_hari_ini': str(isi),
                            'isi_besok': str(data_absensi[idx][i+1]) if i+1 < len(data_absensi[idx]) else "N/A",
                            'jam_hari_ini': jam_hari_ini,
                            'jam_besok': jam_besok,
                            'total_entries': total_entries,
                            'kategori': 'Absen Tidak Lengkap'
                        })

                    # Check for incomplete attendance first
                    if total_entries == 0:
                        tdk_absen.append(tgl)
                    elif total_entries == 1:
                        # Hanya 1 waktu absen = absen tidak lengkap
                        absen_kurang.append(tgl)
                    else:
                        masuk = next((jam for jam in reversed(jam_hari_ini) if jam >= "00:00"), None)
                        pulang = next((jam for jam in jam_besok if jam >= "00:00"), None)

                        jam_masuk_batas = role_settings[role]["jam_masuk"]
                        jam_pulang_batas = role_settings[role]["jam_pulang"]

                        if not masuk or not pulang:
                            absen_kurang.append(tgl)
                        else:
                            if masuk > jam_masuk_batas:
                                telat_masuk.append(tgl)
                            if pulang < jam_pulang_batas:
                                pulang_cepat.append(tgl)
                    
                    # Allow 2 entries per day (instead of 2 total across both days)
                    if len(jam_hari_ini) > 2 or len(jam_besok) > 2:
                        absen_bermasalah.append(tgl)

            # Calculate total working days for performance metric
            total_working_days = len([d for d in tanggal_final if d is not None])
            total_issues = len(tdk_absen) + len(absen_kurang) + len(telat_masuk) + len(pulang_cepat)
            badge_class, badge_text = get_performance_badge(total_issues, total_working_days)

            hasil.append({
                "Nama": nama,
                "Role": role,
                "Performance": badge_text,
                "Badge_Class": badge_class,
                "Tidak Absen": len(tdk_absen),
                "Tanggal Tidak Absen": ", ".join([d.strftime("%d-%b") for d in tdk_absen]),
                "Absen Tidak Lengkap": len(absen_kurang),
                "Tanggal Absen Kurang": ", ".join([d.strftime("%d-%b") for d in absen_kurang]),
                "Hari Absen >2x": len(absen_bermasalah),
                "Tanggal Absen >2x": ", ".join([d.strftime("%d-%b") for d in absen_bermasalah]),
                "Telat Masuk": len(telat_masuk),
                "Tanggal Telat Masuk": ", ".join([d.strftime("%d-%b") for d in telat_masuk]),
                "Pulang Cepat": len(pulang_cepat),
                "Tanggal Pulang Cepat": ", ".join([d.strftime("%d-%b") for d in pulang_cepat])
            })

        progress_bar.empty()
        df_hasil = pd.DataFrame(hasil)
        
        # Debug information for troubleshooting
        if debug_info:
            with st.expander("🐛 Debug Info - Incomplete Attendance Records", expanded=False):
                st.markdown("**Data yang dikategorikan sebagai 'Absen Tidak Lengkap' untuk semua role:**")
                debug_df = pd.DataFrame(debug_info)
                
                # Group by role for better organization
                for role in sorted(debug_df['role'].unique()):
                    role_data = debug_df[debug_df['role'] == role]
                    st.markdown(f"#### **{role} Role** ({len(role_data)} records)")
                    st.dataframe(role_data, use_container_width=True)
        
        # Success message with modern styling
        st.success("✅ **Analysis Complete!** Your attendance data has been processed successfully.")
        
        # Display summary metrics
        st.markdown("## 📊 **Performance Overview**")
        create_summary_metrics(df_hasil)
        
        st.markdown("---")
        
        # Enhanced data display with performance badges
        st.markdown("## 📋 **Detailed Results**")
        
        # View selection tabs
        tab1, tab2 = st.tabs(["📊 **Summary Table**", "🔍 **Detailed View**"])
        
        with tab1:
            st.markdown("### 📋 **Complete Attendance Summary**")
            
            # Simplified filter section - only 2 columns
            col1, col2 = st.columns(2)
            with col1:
                role_filter = st.multiselect(
                    "👥 Filter by Role", 
                    options=sorted(df_hasil['Role'].unique()),
                    default=sorted(df_hasil['Role'].unique())
                )
            with col2:
                performance_filter = st.multiselect(
                    "🎯 Filter by Performance",
                    options=sorted(df_hasil['Performance'].unique()),
                    default=sorted(df_hasil['Performance'].unique())
                )
            
            # Apply filters
            filtered_df = df_hasil[
                (df_hasil['Role'].isin(role_filter)) & 
                (df_hasil['Performance'].isin(performance_filter))
            ]
            
            # Show results count and date details toggle
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info(f"👥 Showing **{len(filtered_df)}** of **{len(df_hasil)}** employees")
            with col2:
                show_details = st.toggle("📅 Show Date Details", value=True)
            
            if show_details:
                # Create display dataframe with all details
                display_df = filtered_df[[
                    'Nama', 'Role', 'Performance',
                    'Tidak Absen', 'Tanggal Tidak Absen',
                    'Absen Tidak Lengkap', 'Tanggal Absen Kurang',
                    'Hari Absen >2x', 'Tanggal Absen >2x',
                    'Telat Masuk', 'Tanggal Telat Masuk',
                    'Pulang Cepat', 'Tanggal Pulang Cepat'
                ]].copy()
                
                # Rename columns for better display
                display_df.columns = [
                    'Nama', 'Role', 'Performance',
                    'Absent Count', 'Absent Dates',
                    'Incomplete Count', 'Incomplete Dates',
                    'Multiple Check-ins', 'Multiple Check-in Dates',
                    'Late Count', 'Late Dates',
                    'Early Leave Count', 'Early Leave Dates'
                ]
            else:
                # Create summary dataframe without date details
                display_df = filtered_df[[
                    'Nama', 'Role', 'Performance',
                    'Tidak Absen', 'Absen Tidak Lengkap', 'Hari Absen >2x',
                    'Telat Masuk', 'Pulang Cepat'
                ]].copy()
                
                # Rename columns for better display
                display_df.columns = [
                    'Nama', 'Role', 'Performance',
                    'Absent Days', 'Incomplete Records', 'Multiple Check-ins',
                    'Late Arrivals', 'Early Departures'
                ]
            
            # Style the dataframe based on performance
            def highlight_performance(row):
                if row['Performance'] == 'Excellent':
                    return ['background-color: #d4edda'] * len(row)
                elif row['Performance'] == 'Good':
                    return ['background-color: #d1ecf1'] * len(row)
                elif row['Performance'] == 'Needs Attention':
                    return ['background-color: #fff3cd'] * len(row)
                elif row['Performance'] == 'Poor':
                    return ['background-color: #f8d7da'] * len(row)
                else:
                    return [''] * len(row)
            
            # Display the styled dataframe
            styled_df = display_df.style.apply(highlight_performance, axis=1)
            st.dataframe(styled_df, use_container_width=True, height=600)
            
            # Add legend
            st.markdown("""
            **Performance Legend:**
            - 🟢 **Excellent**: No attendance issues
            - 🔵 **Good**: ≤10% issue rate
            - 🟡 **Needs Attention**: 10-30% issue rate  
            - 🔴 **Poor**: >30% issue rate
            """)
        
        with tab2:
            st.markdown("### 🔍 **Individual Employee Details**")
            
            # Simple filter section for detailed view
            col1, col2 = st.columns(2)
            with col1:
                role_filter_detail = st.multiselect(
                    "👥 Filter by Role", 
                    options=sorted(df_hasil['Role'].unique()),
                    default=sorted(df_hasil['Role'].unique()),
                    key="role_filter_detail"
                )
            with col2:
                performance_filter_detail = st.multiselect(
                    "🎯 Filter by Performance",
                    options=sorted(df_hasil['Performance'].unique()),
                    default=sorted(df_hasil['Performance'].unique()),
                    key="performance_filter_detail"
                )
            
            # Apply filters for detailed view
            filtered_df_detail = df_hasil[
                (df_hasil['Role'].isin(role_filter_detail)) & 
                (df_hasil['Performance'].isin(performance_filter_detail))
            ]
            
            # Show results count
            st.info(f"👥 Showing **{len(filtered_df_detail)}** of **{len(df_hasil)}** employees")
            
            # Sort by performance severity (Poor first)
            performance_order = {'Poor': 0, 'Needs Attention': 1, 'Good': 2, 'Excellent': 3}
            filtered_df_detail['Performance_Order'] = filtered_df_detail['Performance'].map(performance_order)
            filtered_df_detail = filtered_df_detail.sort_values(['Performance_Order', 'Nama'])
            
            # Display results with enhanced styling
            for _, row in filtered_df_detail.iterrows():
                # Performance color coding
                if row['Performance'] == 'Excellent':
                    status_color = "#155724"
                    bg_color = "#d4edda"
                elif row['Performance'] == 'Good':
                    status_color = "#0c5460"
                    bg_color = "#d1ecf1"
                elif row['Performance'] == 'Needs Attention':
                    status_color = "#856404"
                    bg_color = "#fff3cd"
                else:
                    status_color = "#721c24"
                    bg_color = "#f8d7da"
                
                with st.expander(f"👤 **{row['Nama']}** - {row['Role']} | Performance: {row['Performance']}", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("**📊 Attendance Issues**")
                        st.metric("Absent Days", row['Tidak Absen'])
                        if row['Tanggal Tidak Absen']:
                            st.caption(f"📅 Dates: {row['Tanggal Tidak Absen']}")
                        
                        st.metric("Incomplete Records", row['Absen Tidak Lengkap'])
                        if row['Tanggal Absen Kurang']:
                            st.caption(f"📅 Dates: {row['Tanggal Absen Kurang']}")
                        
                        st.metric("Multiple Check-ins", row['Hari Absen >2x'])
                        if row['Tanggal Absen >2x']:
                            st.caption(f"📅 Dates: {row['Tanggal Absen >2x']}")
                    
                    with col2:
                        st.markdown("**⏰ Punctuality Issues**")
                        st.metric("Late Arrivals", row['Telat Masuk'])
                        if row['Tanggal Telat Masuk']:
                            st.caption(f"📅 Dates: {row['Tanggal Telat Masuk']}")
                        
                        st.metric("Early Departures", row['Pulang Cepat'])
                        if row['Tanggal Pulang Cepat']:
                            st.caption(f"📅 Dates: {row['Tanggal Pulang Cepat']}")
                        
                    with col3:
                        st.markdown("**🎯 Performance Summary**")
                        st.markdown(f"""
                        <div style="background-color: {bg_color}; color: {status_color}; padding: 1rem; border-radius: 8px; text-align: center; margin: 1rem 0;">
                            <h3 style="margin: 0; color: {status_color};">{row['Performance']}</h3>
                            <p style="margin: 0.5rem 0; color: {status_color};">Overall Rating</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        total_issues = row['Tidak Absen'] + row['Absen Tidak Lengkap'] + row['Telat Masuk'] + row['Pulang Cepat']
                        st.metric("Total Issues", total_issues)
        
        # Download section with modern styling
        st.markdown("---")
        st.markdown("## 💾 **Export Results**")
        
        # Prepare clean DataFrame for export (remove styling columns)
        export_df = df_hasil.drop(['Badge_Class'], axis=1)
        csv = export_df.to_csv(index=False).encode("utf-8")
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📥 Download Full Report (CSV)",
                csv,
                f"attendance_report_{bulan_awal}_{bulan_akhir}_{tahun}.csv",
                "text/csv",
                help="Download complete attendance analysis report"
            )
        
        with col2:
            # Create summary CSV
            summary_data = {
                'Metric': ['Total Employees', 'Total Absences', 'Total Late Arrivals', 'Total Early Departures'],
                'Value': [
                    len(df_hasil),
                    df_hasil['Tidak Absen'].sum(),
                    df_hasil['Telat Masuk'].sum(),
                    df_hasil['Pulang Cepat'].sum()
                ]
            }
            summary_csv = pd.DataFrame(summary_data).to_csv(index=False).encode("utf-8")
            st.download_button(
                "📊 Download Summary (CSV)",
                summary_csv,
                f"attendance_summary_{bulan_awal}_{bulan_akhir}_{tahun}.csv",
                "text/csv",
                help="Download summary statistics only"
            )
            
else:
    # Welcome message with instructions
    st.markdown("""
    <div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white; margin: 2rem 0;">
        <h2>🚀 Ready to Analyze Attendance?</h2>
        <p style="font-size: 1.1rem; margin: 1rem 0;">
            Upload your Excel attendance file to get started with intelligent analysis
        </p>
        <div style="margin-top: 2rem;">
            <p><strong>📋 File Requirements:</strong></p>
            <ul style="text-align: left; display: inline-block;">
                <li>Excel format (.xlsx)</li>
                <li>Standard attendance template</li>
                <li>Employee names, roles, and daily records</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature highlights
    st.markdown("## ✨ **Key Features**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🎯 **Smart Analysis**
        - Automatic role detection
        - Intelligent time parsing
        - Performance scoring
        """)
    
    with col2:
        st.markdown("""
        ### 📊 **Rich Insights**
        - Visual performance metrics
        - Detailed breakdowns
        - Trend analysis
        """)
    
    with col3:
        st.markdown("""
        ### 💫 **Modern Interface**
        - Responsive design
        - Interactive filters
        - Easy exports
        """)
