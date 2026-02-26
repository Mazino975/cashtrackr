import streamlit as st
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta
from fpdf import FPDF
from streamlit_option_menu import option_menu
from model import load_data, simpan_data, cek_user, register_user

# ===== CUSTOM STYLING =====
st.set_page_config(page_title="Keuangan Mahasiswa", layout="wide")

st.markdown("""
    <style>
        .stButton>button {
            background-color: #0d6efd;
            color: white;
            font-weight: bold;
            width: 100%;
        }
        .stButton>button:hover {
            background-color: #0b5ed7;
        }
        h1, h2, h3 {
            color: #0d6efd;
        }
        .sidebar .sidebar-content {
            background-color: #f8f9fa;
        }
    </style>
""", unsafe_allow_html=True)

# ===== LOGIN & REGISTRASI =====
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.title("🔐 Sistem Keuangan Mahasiswa")

    menu_auth = st.radio("Pilih Menu", ["Login", "Registrasi"])

    with st.form("form_auth"):
        nim = st.text_input("Masukkan NIM")
        nama = st.text_input("Masukkan Nama")
        submit = st.form_submit_button(
            "Login" if menu_auth == "Login" else "Daftar"
        )

    if submit:
        if menu_auth == "Login":
            if cek_user(nim, nama):
                st.session_state.login = True
                st.session_state.nim = nim
                st.session_state.nama = nama
                st.rerun()
            else:
                st.error("Akun tidak ditemukan. Silakan registrasi.")

        else:  # Registrasi
            if nim and nama:
                if register_user(nim, nama):
                    st.success("Registrasi berhasil! Silakan login.")
                else:
                    st.warning("NIM sudah terdaftar.")
            else:
                st.warning("Semua field harus diisi.")

    st.stop()

# ===== HITUNG SALDO GLOBAL =====
df_global = load_data()
df_global = df_global[df_global["nim"] == st.session_state["nim"]]
df_global["tanggal"] = pd.to_datetime(df_global["tanggal"], errors="coerce")

pemasukan_global = df_global[df_global["jenis"] == "Pemasukan"]["nominal"].sum()
pengeluaran_global = df_global[df_global["jenis"] == "Pengeluaran"]["nominal"].sum()
saldo = pemasukan_global - pengeluaran_global

now = datetime.now().hour
auto_theme = "Terang" if 6 <= now <= 18 else "Gelap"

# Sidebar Navigasi
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4205/4205992.png", width=80)  # Ganti dengan URL gambar yang valid
    st.markdown("###  <span style='color:#0d6efd'>CashTrackr</span>", unsafe_allow_html=True)

    selected = option_menu(
        menu_title=None,
        options=["Beranda", "Catat", "Riwayat", "Laporan", "Fitur Tambahan", "Tentang"],
        icons=["house", "plus-circle", "folder", "bar-chart", "stars", "info-circle"],
        default_index=0
    )

    st.markdown("---")
    st.text(f"👤 Login: {st.session_state['nama']}")
    tema = st.radio(" Tema Warna", ["Terang", "Gelap"], horizontal=True)

    if st.button("🚪 Logout"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

background_color = "#ffffff" if tema == "Terang" else "#1e1e1e"
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {background_color};
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ===== Fungsi Export PDF =====
def export_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Laporan Keuangan Mahasiswa", ln=True, align="C")
    pdf.set_font("Arial", size=10)
    for idx, row in data.iterrows():
        baris = f"{row['tanggal']} | {row['jenis']} | {row['kategori']} | {row['keterangan']} | Rp{int(row['nominal']):,}"
        pdf.cell(200, 8, txt=baris, ln=True)
    filepdf = "laporan_keuangan.pdf"
    pdf.output(filepdf)
    return filepdf

# ===== BERANDA =====
if selected == "Beranda":
    st.title(" Manajemen Keuangan Mahasiswa")
    st.subheader(f"Halo, {st.session_state['nama']}! ")
    df = load_data()
    df = df[df["nim"] == st.session_state["nim"]]

    if df.empty:
        st.info("Belum ada data.")
    else:
        df["tanggal"] = pd.to_datetime(df["tanggal"])
        pemasukan = df[df["jenis"] == "Pemasukan"]["nominal"].sum()
        pengeluaran = df[df["jenis"] == "Pengeluaran"]["nominal"].sum()
        saldo = pemasukan - pengeluaran

        col1, col2, col3 = st.columns(3)
        col1.metric("Pemasukan", f"Rp {pemasukan:,.0f}")
        col2.metric("Pengeluaran", f"Rp {pengeluaran:,.0f}")
        col3.metric("Saldo", f"Rp {saldo:,.0f}")

        chart = alt.Chart(df[df["jenis"] == "Pengeluaran"]).mark_bar().encode(
            x=alt.X("kategori", title="Kategori"),
            y=alt.Y("nominal", title="Jumlah"),
            color="kategori"
        ).properties(height=300)

        st.altair_chart(chart, use_container_width=True)

# ===== CATAT =====
elif selected == "Catat":
    st.title(" Catat Transaksi Baru")
    with st.form("form_input"):
        tanggal = st.date_input("Tanggal")
        jenis = st.selectbox("Jenis", ["Pemasukan", "Pengeluaran"])
        kategori = st.selectbox("Kategori", ["Makanan", "Transport", "Internet", "Listrik", "Lainnya"])
        nominal = st.number_input("Nominal", min_value=0)
        keterangan = st.text_input("Keterangan (Opsional)")
        simpan = st.form_submit_button("Simpan")

        if simpan:
            if not tanggal or not jenis or not kategori or nominal <= 0:
                st.warning("Semua field harus diisi dengan benar.")
            else:
                simpan_data(
                    st.session_state["nim"],
                    tanggal,
                    jenis,
                    kategori,
                    nominal,
                    keterangan
                )
                st.success("✅ Transaksi berhasil disimpan!")

# ===== RIWAYAT =====
elif selected == "Riwayat":
    st.title(" Riwayat Transaksi")
    df = load_data()
    df = df[df["nim"] == st.session_state["nim"]]

    if df.empty:
        st.info("Belum ada data.")
    else:
        df["tanggal"] = pd.to_datetime(df["tanggal"])
        cari = st.text_input("Cari transaksi")
        if cari:
            df = df[df.apply(lambda row: cari.lower() in str(row).lower(), axis=1)]
        st.dataframe(df.sort_values(by="tanggal", ascending=False))
        st.download_button("⬇️ Download CSV", df.to_csv(index=False).encode("utf-8"), "keuangan.csv", "text/csv")
        if st.button("🗑️ Hapus Semua Data"):
            if os.path.exists("data.csv"):
                os.remove("data.csv")
                st.success("Semua data telah dihapus.")
                st.rerun()

# ===== LAPORAN =====
elif selected == "Laporan":
    st.title(" Laporan Keuangan Mahasiswa")
    df = load_data()
    df = df[df["nim"] == st.session_state["nim"]]

    if df.empty:
        st.info("Belum ada data.")
        st.stop()

    df["tanggal"] = pd.to_datetime(df["tanggal"])
    df["bulan"] = df["tanggal"].dt.strftime("%B %Y")

    st.subheader(" Laporan Bulanan")
    laporan_bulanan = df.groupby(["bulan", "jenis"])["nominal"].sum().unstack(fill_value=0).reset_index()
    laporan_bulanan["Saldo"] = laporan_bulanan.get("Pemasukan", 0) - laporan_bulanan.get("Pengeluaran", 0)
    st.dataframe(laporan_bulanan)

    st.subheader(" Ringkasan 7 Hari Terakhir")
    minggu_ini = df[df["tanggal"] >= pd.Timestamp.today() - pd.Timedelta(days=6)]
    ringkas = minggu_ini.groupby(["tanggal", "jenis"])["nominal"].sum().unstack(fill_value=0).reset_index()
    ringkas = ringkas.reindex(columns=["tanggal", "Pemasukan", "Pengeluaran"], fill_value=0)
    ringkas["Saldo"] = ringkas["Pemasukan"] - ringkas["Pengeluaran"]
    st.bar_chart(ringkas.set_index("tanggal")[["Pemasukan", "Pengeluaran"]])

    col1, col2, col3 = st.columns(3)
    col1.metric("Pemasukan", f"Rp {ringkas['Pemasukan'].sum():,.0f}")
    col2.metric("Pengeluaran", f"Rp {ringkas['Pengeluaran'].sum():,.0f}")
    col3.metric("Saldo", f"Rp {ringkas['Saldo'].sum():,.0f}")

    st.subheader(" Filter Kategori dan Tanggal")
    kategori_terpilih = st.selectbox("Pilih Kategori", options=["Semua"] + sorted(df["kategori"].unique()))
    if kategori_terpilih != "Semua":
        df = df[df["kategori"] == kategori_terpilih]

    start_date = st.date_input("Tanggal Mulai", df["tanggal"].min().date())
    end_date = st.date_input("Tanggal Akhir", df["tanggal"].max().date())
    df = df[(df["tanggal"] >= pd.to_datetime(start_date)) & (df["tanggal"] <= pd.to_datetime(end_date))]

    st.subheader(" Pengeluaran Terbesar dan Terkecil")
    pengeluaran = df[df["jenis"] == "Pengeluaran"]
    if not pengeluaran.empty:
        max_row = pengeluaran.loc[pengeluaran["nominal"].idxmax()]
        min_row = pengeluaran.loc[pengeluaran["nominal"].idxmin()]
        st.write(f"🔺 Terbesar: Rp{max_row['nominal']:,} untuk **{max_row['keterangan']}** ({max_row['kategori']}) pada {max_row['tanggal'].date()}")
        st.write(f"🔻 Terkecil: Rp{min_row['nominal']:,} untuk **{min_row['keterangan']}** ({min_row['kategori']}) pada {min_row['tanggal'].date()}")
    else:
        st.info("Belum ada data pengeluaran untuk analisis.")

    if not pengeluaran.empty:
        st.subheader(" Persentase Pengeluaran per Kategori")
        pie_data = pengeluaran.groupby("kategori")["nominal"].sum()
        fig, ax = plt.subplots()
        ax.pie(pie_data, labels=pie_data.index, autopct="%1.1f%%", startangle=140)
        ax.axis("equal")
        st.pyplot(fig)

    st.subheader(" Rekomendasi Keuangan")
    pemasukan_total = df[df["jenis"] == "Pemasukan"]["nominal"].sum()
    pengeluaran_total = df[df["jenis"] == "Pengeluaran"]["nominal"].sum()

    if pengeluaran_total > pemasukan_total:
        st.error("⚠️ Pengeluaran kamu melebihi pemasukan! Coba kurangi pengeluaran harian.")
    elif pengeluaran_total > 0.8 * pemasukan_total:
        st.warning("🔄 Pengeluaran sudah mendekati batas aman. Pertimbangkan untuk menabung.")
    else:
        st.success("✅ Kondisi keuangan kamu sehat! Tetap pertahankan kebiasaan baik ini.")

    st.subheader(" Reminder Harian")
    if datetime.now().hour < 12:
        st.info("Jangan lupa catat pemasukan & pengeluaran hari ini ya! 📅")
    else:
        st.info("Sudahkah kamu mencatat transaksi hari ini? Yuk review kembali sebelum malam! 🌙")

    st.subheader("📤 Export ke PDF")
    if st.button("📥 Download PDF"):
        if df.empty:
            st.error("Data kosong.")
        else:
            filename = export_pdf(df)
            st.success(f"PDF berhasil dibuat: {filename}")
            with open(filename, "rb") as f:
                st.download_button("📄 Klik di sini untuk Unduh PDF", data=f, file_name=filename, mime="application/pdf")

# ===== FITUR TAMBAHAN =====
elif selected == "Fitur Tambahan":
    st.title(" Fitur Tambahan Keuangan Mahasiswa")
    df = load_data()
    df = df[df["nim"] == st.session_state["nim"]]
    df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")

    pemasukan = df[df["jenis"] == "Pemasukan"]["nominal"].sum()
    pengeluaran = df[df["jenis"] == "Pengeluaran"]["nominal"].sum()
    saldo = pemasukan - pengeluaran

    st.subheader(" Target Tabungan")
    target_nama = st.text_input("Nama Target Tabungan", value=st.session_state.get("target_nama", ""))
    target_nominal = st.number_input("Nominal Target", min_value=0, value=st.session_state.get("target_nominal", 0))
    if st.button("Simpan Target"):
        st.session_state.target_nama = target_nama
        st.session_state.target_nominal = target_nominal
        st.success("✅ Target disimpan!")

# ===== TARGET TABUNGAN =====
if st.session_state.get("target_nama"):
    progress = 0

    if st.session_state["target_nominal"] > 0:
        progress = max(
            0,
            min(saldo / st.session_state["target_nominal"], 1.0)
        )

    st.write(
        f"Target: **{st.session_state['target_nama']}** - Rp {st.session_state['target_nominal']:,.0f}"
    )
    st.progress(progress)

    if saldo >= st.session_state["target_nominal"] and st.session_state["target_nominal"] > 0:
        st.success("🎉 Target Tercapai!")
        st.balloons()
    else:
        sisa = max(0, st.session_state["target_nominal"] - saldo)
        st.info(f"🪙 Sisa: Rp {sisa:,.0f}")


# ===== NOTIFIKASI SALDO =====
st.subheader(" Notifikasi Saldo")

if saldo < 50000:
    st.error("⚠️ Saldo sangat rendah!")
elif saldo < 200000:
    st.warning("🔄 Saldo mulai menipis.")
else:
    st.success("✅ Saldo aman.")
    st.subheader(" Rata-rata Pengeluaran Harian")
    pengeluaran_df = df_global[df_global["jenis"] == "Pengeluaran"]
    if not pengeluaran_df.empty:
        hari = (pengeluaran_df["tanggal"].max() - pengeluaran_df["tanggal"].min()).days + 1
        rata = pengeluaran_df["nominal"].sum() / hari if hari > 0 else 0
        st.write(f" Rata-rata: Rp {rata:,.0f} per hari")
    else:
        st.info("Belum ada data pengeluaran.")

    if st.button("📥 Export Semua Data ke PDF"):
        if df.empty:
            st.error("Data kosong.")
        else:
            filename = export_pdf(df)
            st.success(f"PDF berhasil dibuat: {filename}")
            with open(filename, "rb") as f:
                st.download_button("📄 Klik untuk Unduh PDF", data=f, file_name=filename, mime="application/pdf")

# ===== TENTANG =====
if selected == "Tentang":
    st.title("ℹ️ Tentang Aplikasi")
    st.markdown("""
    **CashTrackr** adalah aplikasi manajemen keuangan harian berbasis web yang dirancang khusus untuk mahasiswa.  
    Aplikasi ini bertujuan untuk membantu pengguna:

    - Mencatat pemasukan dan pengeluaran secara rutin  
    - Menampilkan laporan bulanan dan mingguan  
    - Menganalisis kondisi keuangan pribadi  
    - Menetapkan target tabungan dan mengontrol kebiasaan belanja  

    Dibangun dengan Python & Streamlit, CashTrackr cocok untuk proyek Tugas Akhir atau penggunaan pribadi.

    ---
    👨‍💻 Dibuat oleh: Mahasiswa Sistem Informasi  
    📅 Tahun: 2026
    """)

# ===== FOOTER =====
st.markdown("""
    <hr style="margin-top: 3em;">
    <div style="text-align: center; font-size: 0.8em; color: gray;">
        © 2026 CashTrackr. All rights reserved.
    </div>
""", unsafe_allow_html=True)
