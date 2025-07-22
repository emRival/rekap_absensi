
import streamlit as st
import pandas as pd
from datetime import datetime

st.title("📊 Rekapitulasi Absensi Guru & Musyrif")

uploaded_file = st.file_uploader("Upload file absensi (.xlsx)", type=["xlsx"])

def parse_jam(cell):
    if pd.isna(cell): return []
    cell = str(cell).lower()
    if 'l' in cell: return ['L']
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

    tanggal_header = df.iloc[4, 2:].tolist()
    tanggal_final = []
    for i, val in enumerate(tanggal_header):
        try:
            tgl = int(val)
            bulan = datetime.now().month
            tahun = datetime.now().year
            if i > 0 and int(tanggal_header[i]) < int(tanggal_header[i-1]):
                bulan += 1
            tanggal_final.append(datetime(tahun, bulan, tgl))
        except:
            tanggal_final.append(None)

    nama_guru = df.iloc[5:, 0].dropna().tolist()
    role_guru = df.iloc[5:, 1].tolist()
    data_absensi = df.iloc[5:, 2:2+len(tanggal_final)].values.tolist()

    hasil = []

    for idx, (nama, role, baris_absen) in enumerate(zip(nama_guru, role_guru, data_absensi)):
        role = role.strip().upper() if isinstance(role, str) else "SMPSMK"
        tdk_absen, absen_kurang, absen_bermasalah = [], [], []

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
                    masuk, pulang = valid_jam_masuk_pulang_smpsmk(jam_list)
                    if not masuk or not pulang:
                        absen_kurang.append(tgl)
                    if len(jam_list) > 2:
                        absen_bermasalah.append(tgl)

            elif role == "ASRAMA" or role == "MUSYRIF":
                jam_besok = parse_jam(data_absensi[idx][i+1]) if i+1 < len(baris_absen) else []
                jam_hari_ini = parse_jam(isi)

                masuk = None
                pulang = None

                for jam in jam_hari_ini[::-1]:  # ambil jam dari bawah (masuk)
                    if jam >= "15:00":
                        masuk = jam
                        break
                for jam in jam_besok:  # ambil jam dari atas (pulang)
                    if jam <= "08:00":
                        pulang = jam
                        break

                if not jam_hari_ini and not jam_besok:
                    tdk_absen.append(tgl)
                elif not masuk or not pulang:
                    absen_kurang.append(tgl)
                if len(jam_hari_ini) + len(jam_besok) > 2:
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

    csv = df_hasil.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Rekap CSV", csv, "rekap_absensi.csv", "text/csv")
