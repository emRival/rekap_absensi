
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.title("📊 Rekapitulasi Absensi Guru & Musyrif")

uploaded_file = st.file_uploader("Upload file absensi (.xlsx)", type=["xlsx"])

asrama_names = [
    "Andri", "Ikhsan Abror Siregar", "Juldan Ocean D", "Prasetyo Renanda Wijaya",
    "Azzam Zia Ul Haq", "Habil Dimas Ibrahim", "Muhammad Fauzan Bukhori",
    "Muhammad Sadar", "Muhammad Ikhsan Abdillah", "Hanan Abdurrahman"
]

def parse_jam(cell):
    if pd.isna(cell): return []
    cell = str(cell).lower()
    if 'l' in cell: return ['L']  # tanda libur
    jam = cell.replace('\n', '\n').split('\n')
    return [j.strip() for j in jam if ':' in j]

def valid_jam_masuk_pulang_smpsmk(jam_list):
    masuk = None
    pulang = None
    for jam in jam_list:
        if jam >= "07:00" and masuk is None:
            masuk = jam
        if jam <= "15:00":
            pulang = jam
    return masuk, pulang

def evaluate_asrama_absen(jam_hari_ini, jam_besok):
    masuk = any(jam >= "15:00" for jam in jam_hari_ini if jam != 'L')
    pulang = any(jam <= "07:00" for jam in jam_besok if jam != 'L')
    return masuk and pulang

if uploaded_file:
    df = pd.read_excel(uploaded_file, header=None)
    tanggal_awal = datetime(2025, 6, 17)
    tanggal_final = [tanggal_awal + timedelta(days=i) for i in range(30)]  # 30 hari
    nama_guru = df.iloc[5:, 0].dropna().tolist()
    data_absensi = df.iloc[5:, 1:1+len(tanggal_final)].values.tolist()

    hasil = []

    for idx, (nama, baris_absen) in enumerate(zip(nama_guru, data_absensi)):
        role = "ASRAMA" if any(asrama in nama for asrama in asrama_names) else "SMPSMK"
        tdk_absen, absen_kurang, absen_bermasalah = [], [], []

        for i, (tgl, isi) in enumerate(zip(tanggal_final, baris_absen)):
            jam_list = parse_jam(isi)
            if 'L' in jam_list:
                continue  # libur

            if role == "SMPSMK":
                if len(jam_list) == 0:
                    tdk_absen.append(tgl)
                else:
                    masuk, pulang = valid_jam_masuk_pulang_smpsmk(jam_list)
                    if not masuk or not pulang:
                        absen_kurang.append(tgl)
                    if len(jam_list) > 2:
                        absen_bermasalah.append(tgl)

            elif role == "ASRAMA":
                jam_besok = parse_jam(data_absensi[idx][i+1]) if i+1 < len(baris_absen) else []
                if len(jam_list) == 0 and len(jam_besok) == 0:
                    tdk_absen.append(tgl)
                elif not evaluate_asrama_absen(jam_list, jam_besok):
                    absen_kurang.append(tgl)
                if len(jam_list) + len(jam_besok) > 2:
                    absen_bermasalah.append(tgl)

        hasil.append({
            "Nama": nama,
            "Role": role,
            "Tidak Absen": len(tdk_absen),
            "Tanggal Tidak Absen": ", ".join([d.strftime("%d-%b") for d in tdk_absen]),
            "Absen Tidak Lengkap": len(absen_kurang),
            "Tanggal Absen Kurang": ", ".join([d.strftime("%d-%b") for d in absen_kurang]),
            "Hari Absen >2x": len(absen_bermasalah),
            "Tanggal Absen >2x": ", ".join([d.strftime("%d-%b") for d in absen_bermasalah])
        })

    df_hasil = pd.DataFrame(hasil)
    st.success("📋 Rekap Berhasil Diproses!")
    st.dataframe(df_hasil)

    # Optional: download hasil sebagai CSV
    csv = df_hasil.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Rekap CSV", csv, "rekap_absensi.csv", "text/csv")
