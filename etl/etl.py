"""ETL: data/raw.csv -> diare.db (skema bintang). Jalankan ulang kapan saja: python etl/etl.py"""
import sqlite3, pandas as pd
FAKTOR = ["jamban_sehat","air_bersih","cuci_tangan","asi_eksklusif","imunisasi_lengkap","gizi_kurang"]
df = pd.read_csv("data/raw.csv")          # SESUAIKAN nama kolom dengan data asli
print("Sebelum:", len(df), "baris, missing:", int(df.isna().sum().sum()), "duplikat:", int(df.duplicated().sum()))
df = df.drop_duplicates()
df = df.dropna(subset=["kabupaten","kecamatan","tahun","bulan","kelompok_usia","diare"])
df[FAKTOR] = df[FAKTOR].fillna(0).astype(int)
df["kabupaten"] = df["kabupaten"].str.strip().str.title()
print("Sesudah:", len(df), "baris")
dw = df[["kabupaten","kecamatan"]].drop_duplicates().reset_index(drop=True); dw["id"]=dw.index+1
dt = df[["tahun","bulan"]].drop_duplicates().reset_index(drop=True); dt["id"]=dt.index+1
du = df[["kelompok_usia"]].drop_duplicates().rename(columns={"kelompok_usia":"kelompok"}).reset_index(drop=True); du["id"]=du.index+1
f = (df.merge(dw,on=["kabupaten","kecamatan"]).rename(columns={"id":"wilayah_id"})
       .merge(dt,on=["tahun","bulan"]).rename(columns={"id":"waktu_id"})
       .merge(du,left_on="kelompok_usia",right_on="kelompok").rename(columns={"id":"usia_id"}))
f = f[["wilayah_id","waktu_id","usia_id","diare"]+FAKTOR]
con = sqlite3.connect("diare.db")
for n,t in [("dim_wilayah",dw),("dim_waktu",dt),("dim_usia",du),("fact_balita",f)]:
    t.to_sql(n,con,if_exists="replace",index=False)
print("Selesai.")