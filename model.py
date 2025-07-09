import pandas as pd
import os

FILE = "data.csv"

def load_data():
    if os.path.exists(FILE):
        return pd.read_csv(FILE)
    else:
        return pd.DataFrame(columns=["nim", "tanggal", "jenis", "kategori", "nominal", "keterangan"])

def simpan_data(nim, tanggal, jenis, kategori, nominal, keterangan):
    df = load_data()
    data_baru = {
        "nim": nim,
        "tanggal": tanggal,
        "jenis": jenis,  # "Pemasukan" atau "Pengeluaran"
        "kategori": kategori,
        "nominal": nominal,
        "keterangan": keterangan
    }
    df = pd.concat([df, pd.DataFrame([data_baru])], ignore_index=True)
    df.to_csv(FILE, index=False)

import pandas as pd

def cek_user(nim, nama):
    try:
        df = pd.read_csv("users.csv")
        user = df[(df['nim'].astype(str) == str(nim)) & (df['nama'].str.lower() == nama.lower())]
        return not user.empty
    except FileNotFoundError:
        return False

# Contoh penggunaan langsung
if __name__ == "__main__":
    if cek_user("123456", "John Doe"):
        simpan_data("123456", "2025-07-09", "Pemasukan", "Beasiswa", 1000000, "Dana bantuan")
        print("Data berhasil disimpan.")
    else:
        print("NIM atau Nama tidak valid.")
