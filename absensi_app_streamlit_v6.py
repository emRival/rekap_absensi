import streamlit as st
import pandas as pd
from datetime import datetime

st.title("🚀 DASHBOARD SMART ATTENDANCE MONITORING SYSTEM")
st.markdown("### 📊 Analisis Kehadiran & Ketepatan Waktu dengan Toleransi Dinamis")

# Role and time settings - removed MANAGEMENT and added next day indicator for ASRAMA and MUSYRIF
role_settings = {
    "SMPSMK": {"jam_masuk": "07:00", "jam_pulang": "15:00", "pulang_next_day": False},
    "ASRAMA": {"jam_masuk": "15:00", "jam_pulang": "07:00", "pulang_next_day": True},
    "MUSYRIF": {"jam_masuk": "15:00", "jam_pulang": "07:00", "pulang_next_day": True}
}

# Role time configuration UI
with st.expander("⚙️ Konfigurasi Jam Kerja"):
    st.subheader("Pengaturan Jam Kerja per Role")
    for role in role_settings:
        col1, col2 = st.columns(2)
        with col1:
            role_settings[role]["jam_masuk"] = st.text_input(
                f"Jam Masuk {role}", value=role_settings[role]["jam_masuk"], key=f"masuk_{role}"
            )
        with col2:
            role_settings[role]["jam_pulang"] = st.text_input(
                f"Jam Pulang {role}" + (" (H+1)" if role_settings[role]["pulang_next_day"] else ""), 
                value=role_settings[role]["jam_pulang"], 
                key=f"pulang_{role}"
            )

bulan_map = {
    "Januari": 1, "Februari": 2, "Maret": 3, "April": 4,
    "Mei": 5, "Juni": 6, "Juli": 7, "Agustus": 8,
    "September": 9, "Oktober": 10, "November": 11, "Desember": 12
}

col1, col2 = st.columns(2)
with col1:
    bulan_awal = st.selectbox("📅 Pilih Bulan Awal", list(bulan_map.keys()), index=5)
with col2:
    bulan_akhir = st.selectbox("📅 Pilih Bulan Akhir", list(bulan_map.keys()), index=6)

tahun = st.number_input("🗓️ Tahun", value=datetime.now().year, step=1)

uploaded_file = st.file_uploader("Upload file absensi (.xlsx)", type=["xlsx"])

def parse_jam(cell):
    if pd.isna(cell): return []
    cell = str(cell).lower()
    if 'l' in cell: return ['L']
    jam = cell.replace('\n', '\n').split('\n')
    return [j.strip() for j in jam if ':' in j]

def valid_jam_smpsmk(jam_list):
    masuk = None
    pulang = None
    for jam in jam_list:
        if jam >= "00:00" and masuk is None:
            masuk = jam
        pulang = jam  # ambil jam terakhir
    return masuk, pulang

if uploaded_file:
    df = pd.read_excel(uploaded_file, header=None)

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

    for idx, (nama, role, baris_absen) in enumerate(zip(nama_guru, role_guru, data_absensi)):
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
                if len(jam_list) == 0:
                    tdk_absen.append(tgl)
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
                jam_besok = parse_jam(data_absensi[idx][i+1]) if i+1 < len(baris_absen) else []
                jam_hari_ini = parse_jam(isi)

                masuk = next((jam for jam in reversed(jam_hari_ini) if jam >= "00:00"), None)
                pulang = next((jam for jam in jam_besok if jam >= "00:00"), None)

                jam_masuk_batas = role_settings[role]["jam_masuk"]
                jam_pulang_batas = role_settings[role]["jam_pulang"]

                if not jam_hari_ini and not jam_besok:
                    tdk_absen.append(tgl)
                elif not masuk or not pulang:
                    absen_kurang.append(tgl)
                else:
                    if masuk > jam_masuk_batas:
                        telat_masuk.append(tgl)
                    if pulang < jam_pulang_batas:
                        pulang_cepat.append(tgl)
                # Allow 2 entries per day (instead of 2 total across both days)
                if len(jam_hari_ini) > 2 or len(jam_besok) > 2:
                    absen_bermasalah.append(tgl)

        hasil.append({
            "Nama": nama,
            "Role": role,
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

    df_hasil = pd.DataFrame(hasil)
    st.success("📋 Rekap Berhasil Diproses!")
    st.dataframe(df_hasil)

    csv = df_hasil.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Rekap CSV", csv, "rekap_absensi.csv", "text/csv")
