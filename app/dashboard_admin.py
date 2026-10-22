"""Panel admin diare balita. Jalankan: python -m streamlit run app/dashboard_admin.py
DATA DUMMY (seed tetap). Ganti load() dengan data asli."""
import json, numpy as np, pandas as pd, plotly.express as px, plotly.graph_objects as go, streamlit as st

st.set_page_config("SI-Diare Balita", "💧", layout="wide")
BLN = ["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agu","Sep","Okt","Nov","Des"]
USIA = ["0-11 bln","12-23 bln","24-35 bln","36-47 bln","48-59 bln"]
KAB = {"Toba":(2.33,99.07,["Balige","Laguboti","Porsea"]),"Samosir":(2.58,98.73,["Pangururan","Simanindo","Harian"]),
       "Simalungun":(2.95,99.0,["Raya","Siantar Kota","Bandar"]),"Humbang Hasundutan":(2.25,98.5,["Doloksanggul","Lintong Nihuta","Pakkat"]),
       "Tapanuli Utara":(2.0,99.0,["Tarutung","Siborongborong","Pahae"]),"Dairi":(2.75,98.25,["Sidikalang","Sumbul","Parbuluan"])}
BIRU = "#2563eb"
FAKTOR = {"jamban_sehat":"Jamban sehat","air_bersih":"Akses air bersih","cuci_tangan":"Cuci tangan pakai sabun",
          "asi_eksklusif":"ASI eksklusif","imunisasi_lengkap":"Imunisasi lengkap","gizi_kurang":"Gizi kurang"}

@st.cache_data
def load():
    rng = np.random.default_rng(42); rows = []
    for k,(lat,lon,kecs) in KAB.items():
        for kc in kecs:
            san = rng.uniform(50,92)
            for t in pd.period_range("2023-01","2025-12",freq="M"):
                musim = 1+0.35*np.cos((t.month-1)/12*2*np.pi)
                for u,f in zip(USIA,[1.0,1.35,0.9,0.6,0.4]):
                    n = int(rng.integers(80,160)); p = 0.11*f*musim*(1.55-san/100)*(1-0.04*(t.year-2023))
                    rows.append(dict(kabupaten=k,kecamatan=kc,lat=lat,lon=lon,tahun=t.year,bulan=t.month,usia=u,balita=n,kasus=rng.binomial(n,min(p,.9)),
                        jamban=np.clip(san+rng.normal(0,4),0,100),air=np.clip(san+8+rng.normal(0,4),0,100),
                        cuci=np.clip(san-10+rng.normal(0,5),0,100),asi=np.clip(55+rng.normal(0,8),0,100)))
    return pd.DataFrame(rows)

def prev(d, by):
    g = d.groupby(by,as_index=False).agg(kasus=("kasus","sum"),balita=("balita","sum"),jamban=("jamban","mean"),air=("air","mean"),
        cuci=("cuci","mean"),asi=("asi","mean"),lat=("lat","first"),lon=("lon","first"))
    g["prevalensi"] = g.kasus/g.balita*100
    return g
def ringkas(d):
    t = prev(d.assign(g=1),"g").iloc[0]; return dict(kasus=t.kasus,prev=t.prevalensi,jamban=t.jamban,air=t.air)
def status(p): return "🟢 Rendah" if p < 6 else ("🟡 Sedang" if p < 8 else "🔴 Tinggi")
def gambar(f, h=300, legend=False):
    f.update_layout(template="plotly_white",height=h,margin=dict(t=10,l=0,r=0,b=0),showlegend=legend,legend=dict(orientation="h",y=-.2),paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(f, width="stretch")
def kartu(judul, sub=None):
    c = st.container(border=True); c.markdown(f"**{judul}**")
    if sub: c.caption(sub)
    return c

def topbar(judul, sub):
    a,b,c,e = st.columns([3,1.5,1.1,1.4], vertical_alignment="bottom")
    a.markdown(f"## {judul}"); a.caption(sub)
    kab = b.selectbox("Wilayah",["Semua wilayah"]+list(KAB),key="f_kab")
    thn = c.selectbox("Tahun",[2025,2024,2023,"Semua tahun"],key="f_thn")
    usia = e.selectbox("Usia balita",["Semua usia"]+USIA,key="f_usia")
    w = load()
    if kab != "Semua wilayah": w = w[w.kabupaten == kab]
    if usia != "Semua usia": w = w[w.usia == usia]
    d = w if thn == "Semua tahun" else w[w.tahun == thn]
    return d, w, thn

def p_dash():
    d,w,thn = topbar("Dashboard","Ringkasan kejadian diare akut pada balita")
    cur = ringkas(d); yr = thn if isinstance(thn,int) else None
    pv = ringkas(w[w.tahun == yr-1]) if yr and yr > 2023 else None
    s = prev(d,["tahun","bulan"]).sort_values(["tahun","bulan"])
    spec = [("Total kasus","kasus","{:,.0f}","pct",s.kasus),("Prevalensi (%)","prev","{:.1f}","poin",s.prevalensi),
            ("Jamban sehat (%)","jamban","{:.0f}","poin",s.jamban),("Air bersih (%)","air","{:.0f}","poin",s.air)]
    for c,(lbl,k,fmt,mode,ser) in zip(st.columns(4),spec):
        dl = None
        if pv: dl = f"{(cur[k]-pv[k])/pv[k]*100:+.1f}% vs {yr-1}" if mode=="pct" else f"{cur[k]-pv[k]:+.1f} poin vs {yr-1}"
        with c.container(border=True):
            st.metric(lbl,fmt.format(cur[k]),dl,delta_color="inverse" if k in ("kasus","prev") else "normal",chart_data=ser.tolist(),chart_type="area")
    a,b = st.columns([2,1])
    t = prev(d,["tahun","bulan"]); t["Bulan"] = [BLN[i-1] for i in t.bulan]; t["Tahun"] = t.tahun.astype(str)
    with a:
        with kartu("Tren prevalensi bulanan","Garis per tahun; puncak biasanya di musim hujan"):
            gambar(px.line(t,x="Bulan",y="prevalensi",color="Tahun",markers=True,category_orders={"Bulan":BLN},labels={"prevalensi":"Prevalensi (%)","Bulan":""}),320,True)
    with b:
        with kartu("Kasus menurut usia"):
            gambar(px.pie(prev(d,"usia"),names="usia",values="kasus",hole=.55,color_discrete_sequence=px.colors.sequential.Blues_r[:5]),320,True)
    a,b = st.columns(2)
    with a:
        with kartu("Prevalensi per kabupaten"):
            k = prev(d,"kabupaten").sort_values("prevalensi")
            gambar(px.bar(k,y="kabupaten",x="prevalensi",orientation="h",color_discrete_sequence=[BIRU],labels={"prevalensi":"Prevalensi (%)","kabupaten":""}),320)
    with b:
        with kartu("Kecamatan dengan risiko tertinggi"):
            kc = prev(d,["kabupaten","kecamatan"]).sort_values("prevalensi",ascending=False).head(8)
            tb = pd.DataFrame({"Status":kc.prevalensi.map(status),"Kecamatan":kc.kecamatan,"Kabupaten":kc.kabupaten,"Kasus":kc.kasus,"Prevalensi (%)":kc.prevalensi})
            st.dataframe(tb,hide_index=True,width="stretch",height=320,column_config={"Prevalensi (%)":st.column_config.ProgressColumn(min_value=0,max_value=15,format="%.1f")})

def p_wilayah():
    d,_,_ = topbar("Analisis Wilayah","Sebaran kasus menurut kabupaten, kecamatan, dan usia")
    a,b = st.columns(2)
    with a, kartu("Treemap kasus & prevalensi","Ukuran = kasus, warna = prevalensi"):
        gambar(px.treemap(prev(d,["kabupaten","kecamatan"]),path=["kabupaten","kecamatan"],values="kasus",color="prevalensi",color_continuous_scale="YlOrRd"),380)
    with b, kartu("Peta sebaran kasus"):
        gambar(px.scatter_map(prev(d,"kabupaten"),lat="lat",lon="lon",size="kasus",color="prevalensi",hover_name="kabupaten",zoom=7,color_continuous_scale="YlOrRd",map_style="carto-positron"),380)
    a,b = st.columns(2)
    with a, kartu("Variasi prevalensi antar kecamatan-bulan"):
        gambar(px.box(prev(d,["kabupaten","kecamatan","tahun","bulan"]),x="kabupaten",y="prevalensi",color="kabupaten",labels={"prevalensi":"Prevalensi (%)","kabupaten":""}),340)
    with b, kartu("Peta panas usia × bulan"):
        hm = prev(d,["usia","bulan"]).pivot(index="usia",columns="bulan",values="prevalensi"); hm.columns = [BLN[i-1] for i in hm.columns]
        gambar(px.imshow(hm,text_auto=".1f",aspect="auto",color_continuous_scale="YlOrRd"),340)

def p_sanitasi():
    d,_,_ = topbar("Sanitasi & Faktor Risiko","Hubungan indikator lingkungan dan keluarga dengan kejadian diare")
    a,b = st.columns([3,2])
    with a, kartu("Jamban sehat vs prevalensi","Gelembung = kecamatan, animasi per tahun"):
        g = prev(load()[lambda x: x.kabupaten.isin(d.kabupaten.unique()) & x.usia.isin(d.usia.unique())],["kabupaten","kecamatan","tahun"])
        gambar(px.scatter(g,x="jamban",y="prevalensi",size="balita",color="kabupaten",animation_frame="tahun",hover_name="kecamatan",size_max=35,
            range_x=[40,100],range_y=[0,15],labels={"jamban":"Jamban sehat (%)","prevalensi":"Prevalensi (%)"}),420,True)
    with b, kartu("Korelasi dengan prevalensi","Negatif = melindungi"):
        c = prev(d,["kabupaten","kecamatan","tahun","bulan"])[["prevalensi","jamban","air","cuci","asi"]].corr().prevalensi.drop("prevalensi")
        c.index = ["Jamban","Air bersih","Cuci tangan","ASI"]
        gambar(px.bar(c.reset_index(),x="prevalensi",y="index",orientation="h",color_discrete_sequence=[BIRU],labels={"prevalensi":"r","index":""}),420)
    with kartu("Profil sanitasi tiap kecamatan"):
        gambar(px.parallel_coordinates(prev(d,["kabupaten","kecamatan"]),dimensions=["jamban","air","cuci","asi","prevalensi"],color="prevalensi",color_continuous_scale="YlOrRd",
            labels={"jamban":"Jamban","air":"Air bersih","cuci":"Cuci tangan","asi":"ASI","prevalensi":"Prevalensi"}),340)

def p_prediksi():
    st.markdown("## Prediksi Status Diare"); st.caption("Klasifikasi risiko diare balita dari kondisi keluarga dan lingkungan")
    try: m = json.load(open("model.json"))
    except Exception: m = {"intercept":-2.2,"coef":{"jamban_sehat":-.6,"air_bersih":-.7,"cuci_tangan":-.5,"asi_eksklusif":-.4,"imunisasi_lengkap":-.3,"gizi_kurang":.8}}
    a,b = st.columns([3,2])
    with a, kartu("Input data balita"):
        u = st.selectbox("Usia balita",USIA); x = {}
        c1,c2 = st.columns(2)
        for i,(k,v) in enumerate(FAKTOR.items()): x[k] = int((c1 if i%2==0 else c2).toggle(v,value=k!="gizi_kurang"))
    z = m["intercept"]+sum(m["coef"].get(k,0)*v for k,v in x.items())+(0.5 if u in USIA[:2] else 0)
    p = 1/(1+np.exp(-z))
    with b, kartu("Hasil klasifikasi"):
        f = go.Figure(go.Indicator(mode="gauge+number",value=p*100,number={"suffix":"%"},gauge={"axis":{"range":[0,100]},"bar":{"color":BIRU},
            "steps":[{"range":[0,30],"color":"#bbf7d0"},{"range":[30,60],"color":"#fde68a"},{"range":[60,100],"color":"#fecaca"}]}))
        gambar(f,260)
        (st.error if p >= .5 else st.success)(f"**{'Berisiko diare' if p >= .5 else 'Risiko rendah'}** · probabilitas {p*100:.1f}%")
    st.caption("⚠ Koefisien model.json masih placeholder. Ganti dengan hasil training (notebooks/train.py).")

def p_data():
    d,_,_ = topbar("Data & Laporan","Telusuri, ekspor, dan impor data")
    t1,t2,t3 = st.tabs(["📋 Data","📊 Statistik ringkas","⬆ Impor data"])
    with t1:
        st.dataframe(d.drop(columns=["lat","lon"]),hide_index=True,width="stretch",height=380)
        c = st.columns(2)
        c[0].download_button("⬇ Unduh data (CSV)",d.to_csv(index=False),"diare_data.csv",width="stretch")
        c[1].download_button("⬇ Unduh laporan per kecamatan (CSV)",prev(d,["kabupaten","kecamatan"]).drop(columns=["lat","lon"]).to_csv(index=False),"laporan_kecamatan.csv",width="stretch")
    with t2: st.dataframe(d[["balita","kasus","jamban","air","cuci","asi"]].describe().T,width="stretch")
    with t3:
        f = st.file_uploader("Unggah file CSV (hanya data yang berizin dan sudah dianonimkan)",type="csv")
        if f: st.dataframe(pd.read_csv(f).head(50),width="stretch"); st.info("Pratinjau 50 baris. Hubungkan ke etl/etl.py untuk memuat ke data warehouse.")

st.sidebar.markdown("### 💧 SI-Diare Balita"); st.sidebar.caption("Panel Admin · Data dummy")
nav = st.navigation([st.Page(p_dash,title="Dashboard",icon=":material/dashboard:",default=True),
    st.Page(p_wilayah,title="Analisis Wilayah",icon=":material/map:"),st.Page(p_sanitasi,title="Sanitasi",icon=":material/water_drop:"),
    st.Page(p_prediksi,title="Prediksi",icon=":material/psychology:"),st.Page(p_data,title="Data & Laporan",icon=":material/table_chart:")])
nav.run()