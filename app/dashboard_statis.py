"""Dashboard statis diare balita. Jalankan: python -m streamlit run app/dashboard_statis.py
DATA DI SINI DUMMY (seed tetap) - ganti fungsi load() dengan data asli nanti."""
import numpy as np, pandas as pd, plotly.express as px, streamlit as st

st.set_page_config("Dashboard Diare Balita", "💧", layout="wide")
BLN = ["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agu","Sep","Okt","Nov","Des"]
USIA = ["0-11 bln","12-23 bln","24-35 bln","36-47 bln","48-59 bln"]
KAB = {"Toba":(2.33,99.07,["Balige","Laguboti","Porsea"]), "Samosir":(2.58,98.73,["Pangururan","Simanindo","Harian"]),
       "Simalungun":(2.95,99.0,["Raya","Siantar Kota","Bandar"]), "Humbang Hasundutan":(2.25,98.5,["Doloksanggul","Lintong Nihuta","Pakkat"]),
       "Tapanuli Utara":(2.0,99.0,["Tarutung","Siborongborong","Pahae"]), "Dairi":(2.75,98.25,["Sidikalang","Sumbul","Parbuluan"])}

@st.cache_data
def load():
    rng = np.random.default_rng(42); rows = []
    for k,(lat,lon,kecs) in KAB.items():
        for kc in kecs:
            san = rng.uniform(50,92)
            for t in pd.period_range("2023-01","2025-12",freq="M"):
                musim = 1+0.35*np.cos((t.month-1)/12*2*np.pi)
                for u,f in zip(USIA,[1.0,1.35,0.9,0.6,0.4]):
                    n = int(rng.integers(80,160))
                    p = 0.11*f*musim*(1.55-san/100)*(1-0.04*(t.year-2023))
                    rows.append(dict(kabupaten=k,kecamatan=kc,lat=lat,lon=lon,tanggal=t.to_timestamp(),tahun=t.year,bulan=t.month,usia=u,
                        balita=n,kasus=rng.binomial(n,min(p,.9)),jamban=np.clip(san+rng.normal(0,4),0,100),
                        air_bersih=np.clip(san+8+rng.normal(0,4),0,100),cuci_tangan=np.clip(san-10+rng.normal(0,5),0,100),
                        asi=np.clip(55+rng.normal(0,8),0,100)))
    return pd.DataFrame(rows)

def prev(d, by):
    g = d.groupby(by, as_index=False).agg(kasus=("kasus","sum"), balita=("balita","sum"), jamban=("jamban","mean"),
        air=("air_bersih","mean"), cuci=("cuci_tangan","mean"), asi=("asi","mean"), lat=("lat","first"), lon=("lon","first"))
    g["prevalensi"] = g.kasus/g.balita*100
    return g

def tampil(fig, h=380):
    fig.update_layout(template="plotly_white", height=h, margin=dict(t=60,l=10,r=10,b=10), title_font_size=15)
    st.plotly_chart(fig, use_container_width=True)

df = load()
st.sidebar.header("Filter")
kab = st.sidebar.multiselect("Kabupaten", list(KAB), default=list(KAB))
thn = st.sidebar.multiselect("Tahun", [2023,2024,2025], default=[2023,2024,2025])
usia = st.sidebar.multiselect("Kelompok usia", USIA, default=USIA)
d = df[df.kabupaten.isin(kab) & df.tahun.isin(thn) & df.usia.isin(usia)]
if d.empty: st.warning("Pilih minimal satu nilai di tiap filter."); st.stop()
st.sidebar.download_button("⬇ Unduh data terfilter (CSV)", d.to_csv(index=False), "diare_terfilter.csv")
st.sidebar.caption("⚠ Data dummy untuk demo tampilan.")

st.title("💧 Dashboard Kejadian Diare Akut pada Balita")
st.caption("Kawasan Danau Toba dan sekitarnya · 2023–2025 · data statis")
tot, base = prev(d.assign(g=1),"g").iloc[0], prev(df.assign(g=1),"g").iloc[0]
c = st.columns(4)
c[0].metric("Total kasus", f"{int(tot.kasus):,}")
c[1].metric("Prevalensi", f"{tot.prevalensi:.1f}%", f"{tot.prevalensi-base.prevalensi:+.1f} vs seluruh data", delta_color="inverse")
c[2].metric("Jamban sehat", f"{tot.jamban:.0f}%", f"{tot.jamban-base.jamban:+.1f} vs seluruh data")
c[3].metric("Air bersih", f"{tot.air:.0f}%", f"{tot.air-base.air:+.1f} vs seluruh data")

t1,t2,t3,t4 = st.tabs(["📈 Tren & Pola","🗺 Wilayah & Usia","🚰 Sanitasi","📖 Cerita Data"])
with t1:
    ts = prev(d,"tanggal"); pk = ts.loc[ts.prevalensi.idxmax()]
    f = px.line(ts,x="tanggal",y="prevalensi",markers=True,color_discrete_sequence=["#1f6f78"],
                title="Prevalensi diare memuncak di musim hujan (akhir/awal tahun)",labels={"prevalensi":"Prevalensi (%)","tanggal":""})
    f.add_annotation(x=pk.tanggal,y=pk.prevalensi,text=f"Puncak {pk.prevalensi:.1f}%",showarrow=True,arrowhead=2,bgcolor="#fde8d8")
    tampil(f)
    hm = prev(d,["usia","bulan"]).pivot(index="usia",columns="bulan",values="prevalensi"); hm.columns = [BLN[i-1] for i in hm.columns]
    tampil(px.imshow(hm,text_auto=".1f",aspect="auto",color_continuous_scale="YlOrRd",title="Heatmap: balita 12–23 bulan paling rentan sepanjang tahun"),340)
with t2:
    a,b = st.columns(2)
    with a: tampil(px.treemap(prev(d,["kabupaten","kecamatan"]),path=["kabupaten","kecamatan"],values="kasus",color="prevalensi",
                color_continuous_scale="YlOrRd",title="Treemap: ukuran = kasus, warna = prevalensi"),420)
    with b: tampil(px.sunburst(prev(d,["kabupaten","usia"]),path=["kabupaten","usia"],values="kasus",color="prevalensi",
                color_continuous_scale="YlOrRd",title="Sunburst: sebaran kasus per kabupaten dan usia"),420)
    a,b = st.columns(2)
    with a: tampil(px.scatter_map(prev(d,"kabupaten"),lat="lat",lon="lon",size="kasus",color="prevalensi",hover_name="kabupaten",zoom=7,
                color_continuous_scale="YlOrRd",map_style="carto-positron",title="Peta sebaran kasus per kabupaten"),420)
    with b: tampil(px.box(prev(d,["kabupaten","kecamatan","tanggal"]),x="kabupaten",y="prevalensi",color="kabupaten",
                title="Box plot: variasi prevalensi antar kecamatan-bulan",labels={"prevalensi":"Prevalensi (%)"}).update_layout(showlegend=False),420)
with t3:
    g = prev(d,["kabupaten","kecamatan","tahun"])
    fb = px.scatter(g,x="jamban",y="prevalensi",size="balita",color="kabupaten",animation_frame="tahun",hover_name="kecamatan",size_max=40,
        range_x=[df.jamban.min()-3,100],range_y=[0,df.kasus.div(df.balita).max()*60],
        title="Bubble animasi: kecamatan dengan jamban sehat lebih tinggi cenderung berprevalensi rendah",
        labels={"jamban":"Jamban sehat (%)","prevalensi":"Prevalensi (%)"})
    tampil(fb,460)
    kc = prev(d,["kabupaten","kecamatan"])
    tampil(px.parallel_coordinates(kc,dimensions=["jamban","air","cuci","asi","prevalensi"],color="prevalensi",color_continuous_scale="YlOrRd",
        labels={"jamban":"Jamban","air":"Air bersih","cuci":"Cuci tangan","asi":"ASI","prevalensi":"Prevalensi"},title="Parallel coordinates: profil sanitasi tiap kecamatan"),400)
with t4:
    kk = prev(d,"kabupaten").sort_values("prevalensi"); kcm = prev(d,["kabupaten","kecamatan","tanggal"])
    cr = kcm[["prevalensi","jamban","air","cuci","asi"]].corr().prevalensi.drop("prevalensi")
    us = prev(d,"usia").sort_values("prevalensi").iloc[-1]; ts = prev(d,"bulan").sort_values("prevalensi").iloc[-1]
    st.subheader("Pertanyaan keputusan: wilayah dan kelompok mana yang harus diprioritaskan?")
    st.markdown(f"""
1. **Wilayah:** prevalensi tertinggi di **{kk.iloc[-1].kabupaten}** ({kk.iloc[-1].prevalensi:.1f}%), terendah di **{kk.iloc[0].kabupaten}** ({kk.iloc[0].prevalensi:.1f}%).
2. **Usia:** kelompok **{us.usia}** paling rentan ({us.prevalensi:.1f}%) → prioritas edukasi ASI dan imunisasi.
3. **Waktu:** puncak kasus di bulan **{BLN[int(ts.bulan)-1]}** → siapkan oralit dan penyuluhan sebelum musim hujan.
4. **Sanitasi:** korelasi terkuat dengan prevalensi adalah **{cr.abs().idxmax()}** (r = {cr[cr.abs().idxmax()]:.2f}).
""")
    tampil(px.bar(cr.rename({"jamban":"Jamban","air":"Air bersih","cuci":"Cuci tangan","asi":"ASI"}).reset_index(),x="prevalensi",y="index",orientation="h",
        title="Korelasi indikator dengan prevalensi (negatif = melindungi)",labels={"prevalensi":"Korelasi (r)","index":""},color_discrete_sequence=["#1f6f78"]),300)
    st.info("Rekomendasi: fokuskan intervensi sanitasi pada kecamatan dengan cakupan jamban terendah dan mulai penyuluhan 1–2 bulan sebelum puncak musim hujan.")