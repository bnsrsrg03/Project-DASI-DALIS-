import os, requests, pandas as pd, plotly.express as px, streamlit as st
API = os.getenv("API_URL","http://localhost:8080")
F = {"jamban_sehat":"Jamban sehat","air_bersih":"Air bersih","cuci_tangan":"Cuci tangan pakai sabun",
     "asi_eksklusif":"ASI eksklusif","imunisasi_lengkap":"Imunisasi lengkap","gizi_kurang":"Gizi kurang"}
st.set_page_config("Dashboard Diare Balita", layout="wide")
get = lambda p, **q: requests.get(f"{API}{p}", params=q, timeout=10).json()

st.title("Dashboard Kejadian Diare Akut pada Balita")
fl = get("/api/filters")
kab = st.sidebar.selectbox("Kabupaten", ["Semua"]+[x["label"] for x in fl["kabupaten"]])
thn = st.sidebar.selectbox("Tahun", ["Semua"]+[str(x["label"]) for x in fl["tahun"]])
q = {"kab": "" if kab=="Semua" else kab, "tahun": "" if thn=="Semua" else thn}

tab1, tab2, tab3 = st.tabs(["Ringkasan","Faktor Risiko","Prediksi"])
with tab1:
    s = get("/api/summary", **q); d = s["prevalensi"]-s["prevalensi_semua"]
    c = st.columns(4)
    c[0].metric("Total balita", f'{s["balita"]:,}')
    c[1].metric("Kasus diare", f'{s["kasus"]:,}')
    c[2].metric("Prevalensi", f'{s["prevalensi"]:.1f}%', f"{d:+.1f} vs rata-rata", delta_color="inverse")
    c[3].metric("Jamban sehat", f'{s["jamban"]:.0f}%')
    def chart(dim, title, line=False):
        df = pd.DataFrame(get("/api/by", dim=dim, **q))
        f = px.line if line else px.bar
        return f(df, x="label", y="rate", title=title, labels={"label":"","rate":"Prevalensi (%)"})
    a, b = st.columns(2)
    a.plotly_chart(chart("usia","Balita 12–23 bulan paling rentan?"), use_container_width=True)
    b.plotly_chart(chart("bulan","Pola prevalensi per bulan",True), use_container_width=True)
    st.plotly_chart(chart("kecamatan","Prevalensi per kecamatan"), use_container_width=True)
with tab2:
    r = get("/api/risk", **q); rows=[]
    for k,v in r.items():
        for x in v: rows.append({"Faktor":F[k],"Status":"Ya" if x["label"]==1 else "Tidak","Prevalensi (%)":x["rate"]})
    st.plotly_chart(px.bar(pd.DataFrame(rows),x="Faktor",y="Prevalensi (%)",color="Status",barmode="group",
                           title="Prevalensi diare menurut faktor sanitasi & keluarga"), use_container_width=True)
with tab3:
    st.subheader("Klasifikasi status diare")
    feat = {k: int(st.checkbox(v)) for k,v in F.items()}
    if st.button("Prediksi"):
        o = requests.post(f"{API}/api/predict", json={"features":feat}).json()
        st.success(f'{o["kelas"]} — probabilitas {o["probabilitas"]*100:.1f}%')