import pandas as pd
import os

DATA_FILE = "data.csv"
USER_FILE = "users.csv"


# ==============================
# LOAD DATA KEUANGAN
# ==============================
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["nim", "tanggal", "jenis", "kategori", "nominal", "keterangan"])


# ==============================
# SIMPAN DATA KEUANGAN
# ==============================
def simpan_data(nim, tanggal, jenis, kategori, nominal, keterangan):
    df = load_data()

    data_baru = {
        "nim": nim,
        "tanggal": tanggal,
        "jenis": jenis,
        "kategori": kategori,
        "nominal": nominal,
        "keterangan": keterangan
    }

    df = pd.concat([df, pd.DataFrame([data_baru])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)


# ==============================
# CEK USER LOGIN
# ==============================
def cek_user(nim, nama):
    try:
        df = pd.read_csv(USER_FILE)
        user = df[
            (df["nim"].astype(str) == str(nim)) &
            (df["nama"].str.lower() == nama.lower())
        ]
        return not user.empty
    except FileNotFoundError:
        return False


# ==============================
# REGISTER USER BARU
# ==============================
def register_user(nim, nama):
    # Jika file users belum ada → buat dulu
    if not os.path.exists(USER_FILE):
        df = pd.DataFrame(columns=["nim", "nama"])
        df.to_csv(USER_FILE, index=False)

    df = pd.read_csv(USER_FILE)

    # Cek apakah NIM sudah terdaftar
    if nim in df["nim"].astype(str).values:
        return False

    new_user = pd.DataFrame([[nim, nama]], columns=["nim", "nama"])
    df = pd.concat([df, new_user], ignore_index=True)
    df.to_csv(USER_FILE, index=False)

    return True
