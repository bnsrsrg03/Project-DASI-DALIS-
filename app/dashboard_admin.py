"""Panel admin diare balita. Jalankan: python -m streamlit run app/dashboard_admin.py"""
import base64, mimetypes
from pathlib import Path
import itertools, json, numpy as np, pandas as pd, plotly.express as px, plotly.graph_objects as go, plotly.io as pio, streamlit as st

st.set_page_config("SI-Diare Balita", ":material/water_drop:", layout="wide")
BLN = ["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agu","Sep","Okt","Nov","Des"]
USIA = ["0-11 bln","12-23 bln","24-35 bln","36-47 bln","48-59 bln"]
BIRU = "#0f766e"
SKALA = ["#fdf3e1","#f3b45a","#c2410c"]
_n = itertools.count()
pio.templates["diare"] = go.layout.Template(layout=dict(
    font=dict(family="Plus Jakarta Sans, Segoe UI, sans-serif", size=12, color="#3a5350"),
    colorway=[BIRU,"#d97706","#475569","#14a094","#b42318","#94a3b8"], paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=False, linecolor="#cfdad7", tickcolor="#cfdad7"), yaxis=dict(gridcolor="#e6eeec", zeroline=False),
    hoverlabel=dict(bgcolor="white", font_size=12), legend=dict(orientation="h", y=1.1, x=0, title_text="")))
px.defaults.template = "diare"
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
html, body, .stApp, button, input, textarea, select { font-family:'Plus Jakarta Sans','Segoe UI',sans-serif; }
.block-container { padding:2.6rem 2.2rem 2rem 2.2rem; max-width:100% !important; }
.stApp:has([data-testid="stSidebar"][aria-expanded="false"]) .block-container { padding-left:4.6rem; }
[data-testid="stHeader"] { background:transparent; height:3rem; }
[data-testid="stVerticalBlock"] { gap:.9rem; }
[data-testid="stSidebarUserContent"] { padding-top:0; }
[data-testid="stSidebarNav"], [data-testid="stSidebarNavItems"] { padding-top:0; margin-top:0; }
[data-testid="stSidebarCollapseButton"] { opacity:1 !important; visibility:visible !important; }
[data-testid="stSidebarCollapseButton"] button { color:#fff; background:rgba(255,255,255,.10); border-radius:10px; }
[data-testid="stSidebarCollapseButton"] button:hover { background:rgba(255,255,255,.22); }
[data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapsedControl"] button { background:#0f766e !important; color:#fff !important;
  border-radius:12px !important; width:2.5rem; height:2.5rem; box-shadow:0 4px 12px rgba(15,118,110,.35); }
[data-testid="stExpandSidebarButton"] svg, [data-testid="stSidebarCollapsedControl"] svg { color:#fff !important; fill:#fff !important; }
h1,h2,h3,h4 { font-weight:650; letter-spacing:-0.01em; color:#10302d; }
h2 { font-size:1.55rem; margin-bottom:0; padding-bottom:0; }
[data-testid="stCaptionContainer"] { color:#5f7370; }
[class*="st-key-kartu_"] { background:#fff; border:1px solid #e1e8e6 !important; border-radius:12px; box-shadow:0 1px 2px rgba(16,48,45,.05); }
[data-testid="stMetricLabel"] p { font-size:.74rem; text-transform:uppercase; letter-spacing:.07em; color:#5f7370; font-weight:600; }
[data-testid="stMetricValue"] { font-size:1.9rem; font-weight:650; color:#10302d; font-variant-numeric:tabular-nums; }
[data-testid="stMetricDelta"] { font-size:.8rem; }
button[data-baseweb="tab"] p { font-weight:600; }
[data-testid="stSidebar"] { border-right:0; }
[data-testid="stSidebar"] h3 { color:#fff; letter-spacing:.01em; }
[data-testid="stSidebarNavLink"] { border-radius:8px; margin:2px 6px; }
[data-testid="stSidebarNavLink"][aria-current="page"] { background:rgba(255,255,255,.12); font-weight:600; }
.stApp { background:linear-gradient(180deg,#e9f2f0 0,#f4f7f6 340px); }
.st-key-hero { background:linear-gradient(115deg,#0b5f58 0%,#0f766e 45%,#2aa89a 100%); border-radius:16px; padding:1.3rem 1.6rem 1rem; margin-bottom:.4rem;
  box-shadow:0 8px 24px rgba(15,118,110,.22); }
.st-key-hero h2, .st-key-hero p { color:#fff !important; }
.st-key-hero [data-testid="stCaptionContainer"] p { color:rgba(255,255,255,.82) !important; }
[class*="st-key-kartu_"] { transition:box-shadow .2s, transform .2s; }
[class*="st-key-kartu_"]:hover { box-shadow:0 8px 22px rgba(16,48,45,.10); }
[class*="st-key-kartu_kpi"] { position:relative; overflow:hidden; --acc:#0f766e; padding-top:.35rem; }
[class*="st-key-kartu_kpi"]::before { content:""; position:absolute; left:0; right:0; top:0; height:4px; background:var(--acc); }
.st-key-kartu_kpi1 { --acc:#d97706; } .st-key-kartu_kpi2 { --acc:#14a094; } .st-key-kartu_kpi3 { --acc:#475569; }
.st-key-kartu_filter { padding:1rem 1.25rem .5rem !important; margin-bottom:.3rem; }
.st-key-kartu_filter label p { font-size:.78rem; font-weight:600; color:#4a6360; }
</style>""", unsafe_allow_html=True)
LOGO_TINGGI = 72    # px: ubah angka ini untuk memperbesar/memperkecil logo
LOGO_LEBAR = 230    # px: lebar maksimum logo
_ada = sorted(x for x in Path(__file__).resolve().parent.iterdir() if x.suffix.lower() in (".png",".jpg",".jpeg",".svg",".webp"))
LOGO = next((x for x in _ada if "logo" in x.stem.lower()), _ada[0] if _ada else None)
if LOGO:
    _b64 = base64.b64encode(LOGO.read_bytes()).decode(); _mime = mimetypes.guess_type(LOGO.name)[0] or "image/png"
    st.markdown(f"""<style>
[data-testid="stSidebarHeader"] {{ height:auto !important; min-height:{LOGO_TINGGI+20}px; padding:14px 14px 4px 16px !important; align-items:center; justify-content:space-between; }}
[data-testid="stSidebarHeader"]::before {{ content:""; display:block; width:{LOGO_LEBAR}px; max-width:calc(100% - 52px); height:{LOGO_TINGGI}px;
  background:#fff url("data:{_mime};base64,{_b64}") no-repeat center/contain; border-radius:10px; }}
img[data-testid="stLogo"], [data-testid="stLogoSpacer"] {{ display:none !important; }}
</style>""", unsafe_allow_html=True)
FAKTOR = {"jamban_sehat":"Jamban sehat","air_bersih":"Akses air bersih","cuci_tangan":"Cuci tangan pakai sabun",
          "asi_eksklusif":"ASI eksklusif","imunisasi_lengkap":"Imunisasi lengkap","gizi_kurang":"Gizi kurang"}

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
F_DATA, F_WIL = DATA_DIR/"data_kasus.csv", DATA_DIR/"wilayah.csv"
KOLOM = ["kabupaten","kecamatan","lat","lon","tahun","bulan","usia","balita","kasus","jamban","air","cuci","asi"]
NUM = ["lat","lon","tahun","bulan","balita","kasus","jamban","air","cuci","asi"]
KUNCI = ["kabupaten","kecamatan","tahun","bulan","usia"]
def baca(p, cols): return pd.read_csv(p) if p.exists() else pd.DataFrame(columns=cols)
def simpan(x, p): DATA_DIR.mkdir(exist_ok=True); x.to_csv(p, index=False)
def load():
    x = baca(F_DATA, KOLOM)
    for k in NUM: x[k] = pd.to_numeric(x[k], errors="coerce")
    x = x.dropna(subset=["kabupaten","kecamatan","usia","tahun","bulan","balita","kasus"])
    return x.astype({"tahun":int,"bulan":int}).reset_index(drop=True)
def wilayah():
    w = {}
    for x in (baca(F_WIL,["kabupaten","kecamatan","lat","lon"]), baca(F_DATA,KOLOM)[["kabupaten","kecamatan","lat","lon"]]):
        for r in x.drop_duplicates(["kabupaten","kecamatan"]).itertuples():
            k = w.setdefault(r.kabupaten,[r.lat,r.lon,[]])
            if pd.isna(k[0]) and not pd.isna(r.lat): k[0],k[1] = r.lat,r.lon
            if r.kecamatan not in k[2]: k[2].append(r.kecamatan)
    return dict(sorted(w.items()))

def prev(d, by):
    g = d.groupby(by,as_index=False).agg(kasus=("kasus","sum"),balita=("balita","sum"),jamban=("jamban","mean"),air=("air","mean"),
        cuci=("cuci","mean"),asi=("asi","mean"),lat=("lat","first"),lon=("lon","first"))
    g["prevalensi"] = g.kasus/g.balita*100
    return g
def ringkas(d):
    t = prev(d.assign(g=1),"g").iloc[0]; return dict(kasus=t.kasus,prev=t.prevalensi,jamban=t.jamban,air=t.air)
def status(p): return "Rendah" if p < 6 else ("Sedang" if p < 8 else "Tinggi")
def gambar(f, h=300, legend=False):
    f.update_layout(template="diare", height=h, margin=dict(t=34 if legend else 10,l=0,r=0,b=0), showlegend=legend)
    f.update_traces(line_width=2.8, selector=dict(type="scatter", mode="lines+markers"))
    for t in f.data:
        if t.type == "bar":
            try: t.marker.cornerradius = 6
            except Exception: pass
    st.plotly_chart(f, width="stretch", config={"displayModeBar": False})
WARNA_KPI = ["#0f766e","#d97706","#14a094","#475569"]
def mini(y, warna):
    r,g,b = (int(warna[i:i+2],16) for i in (1,3,5)); lo,hi = min(y),max(y); pad = (hi-lo)*.15 or 1
    f = go.Figure(go.Scatter(y=y,mode="lines",line=dict(color=warna,width=2.4,shape="spline"),fill="tozeroy",fillcolor=f"rgba({r},{g},{b},.14)",hoverinfo="skip"))
    f.update_layout(height=62,margin=dict(t=4,l=0,r=0,b=0),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",showlegend=False,
                    xaxis=dict(visible=False),yaxis=dict(visible=False,range=[lo-pad,hi+pad]))
    st.plotly_chart(f, width="stretch", config={"displayModeBar":False,"staticPlot":True})
def kartu(judul, sub=None):
    c = st.container(border=True, key=f"kartu_{next(_n)}"); c.markdown(f"**{judul}**")
    if sub: c.caption(sub)
    return c

def topbar(judul, sub):
    with st.container(key="hero"):
        st.markdown(f"## {judul}"); st.caption(sub)
    w = load()
    if w.empty:
        st.info("**Belum ada data.** Buka menu **Kelola Data** untuk menambah data manual atau mengimpor CSV."); st.stop()
    with st.container(key="kartu_filter"):
        b,c,e = st.columns(3)
    kab = b.selectbox("Wilayah",["Semua wilayah"]+sorted(w.kabupaten.unique()),key="f_kab")
    thn = c.selectbox("Tahun",sorted(w.tahun.unique().tolist(),reverse=True)+["Semua tahun"],key="f_thn")
    usia = e.selectbox("Usia balita",["Semua usia"]+[u for u in USIA if u in set(w.usia)],key="f_usia")
    if kab != "Semua wilayah": w = w[w.kabupaten == kab]
    if usia != "Semua usia": w = w[w.usia == usia]
    d = w if thn == "Semua tahun" else w[w.tahun == thn]
    if d.empty: st.warning("Tidak ada data untuk filter ini. Ubah filter di atas."); st.stop()
    return d, w, thn

def p_dash():
    d,w,thn = topbar("Dashboard","Ringkasan kejadian diare akut pada balita")
    cur = ringkas(d); yr = thn if isinstance(thn,int) else None
    pv = ringkas(w[w.tahun == yr-1]) if yr and (w.tahun == yr-1).any() else None
    s = prev(d,["tahun","bulan"]).sort_values(["tahun","bulan"])
    spec = [("Total kasus","kasus","{:,.0f}","pct",s.kasus),("Prevalensi (%)","prev","{:.1f}","poin",s.prevalensi),
            ("Jamban sehat (%)","jamban","{:.0f}","poin",s.jamban),("Air bersih (%)","air","{:.0f}","poin",s.air)]
    for i_,(c,(lbl,k,fmt,mode,ser)) in enumerate(zip(st.columns(4),spec)):
        dl = None
        if pv: dl = f"{(cur[k]-pv[k])/pv[k]*100:+.1f}% vs {yr-1}" if mode=="pct" else f"{cur[k]-pv[k]:+.1f} poin vs {yr-1}"
        with c.container(border=True, key=f"kartu_kpi{i_}"):
            st.metric(lbl,fmt.format(cur[k]),dl,delta_color="inverse" if k in ("kasus","prev") else "normal")
            mini(ser.tolist(), WARNA_KPI[i_])
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
        gambar(px.treemap(prev(d,["kabupaten","kecamatan"]),path=["kabupaten","kecamatan"],values="kasus",color="prevalensi",color_continuous_scale=SKALA),380)
    with b, kartu("Peta sebaran kasus"):
        pk = prev(d,"kabupaten").dropna(subset=["lat","lon"])
        if pk.empty: st.caption("Koordinat belum diisi. Isi latitude/longitude saat menambah daerah atau di CSV.")
        else: gambar(px.scatter_map(pk,lat="lat",lon="lon",size="kasus",color="prevalensi",hover_name="kabupaten",zoom=7,color_continuous_scale=SKALA,map_style="carto-positron"),380)
    a,b = st.columns(2)
    with a, kartu("Variasi prevalensi antar kecamatan-bulan"):
        gambar(px.box(prev(d,["kabupaten","kecamatan","tahun","bulan"]),x="kabupaten",y="prevalensi",color="kabupaten",labels={"prevalensi":"Prevalensi (%)","kabupaten":""}),340)
    with b, kartu("Peta panas usia × bulan"):
        hm = prev(d,["usia","bulan"]).pivot(index="usia",columns="bulan",values="prevalensi"); hm.columns = [BLN[i-1] for i in hm.columns]
        gambar(px.imshow(hm,text_auto=".1f",aspect="auto",color_continuous_scale=SKALA),340)

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
        gambar(px.parallel_coordinates(prev(d,["kabupaten","kecamatan"]),dimensions=["jamban","air","cuci","asi","prevalensi"],color="prevalensi",color_continuous_scale=SKALA,
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
            "steps":[{"range":[0,30],"color":"#d5ebe7"},{"range":[30,60],"color":"#f7e4b5"},{"range":[60,100],"color":"#f1c6bd"}]}))
        gambar(f,260)
        (st.error if p >= .5 else st.success)(f"**{'Berisiko diare' if p >= .5 else 'Risiko rendah'}** · probabilitas {p*100:.1f}%")
    st.caption("Koefisien model.json masih placeholder. Ganti dengan hasil training (notebooks/train.py).")

def p_data():
    d,_,_ = topbar("Data & Laporan","Telusuri, ekspor, dan impor data")
    t1,t2 = st.tabs(["Data","Statistik ringkas"])
    with t1:
        st.dataframe(d.drop(columns=["lat","lon"]),hide_index=True,width="stretch",height=380)
        c = st.columns(2)
        c[0].download_button("Unduh data (CSV)",d.to_csv(index=False),"diare_data.csv",width="stretch")
        c[1].download_button("Unduh laporan per kecamatan (CSV)",prev(d,["kabupaten","kecamatan"]).drop(columns=["lat","lon"]).to_csv(index=False),"laporan_kecamatan.csv",width="stretch")
    with t2: st.dataframe(d[["balita","kasus","jamban","air","cuci","asi"]].describe().T,width="stretch")

def p_kelola():
    st.markdown("## Kelola Data"); st.caption("Semua data aplikasi berasal dari input di sini. Tersimpan di folder data/ (data_kasus.csv, wilayah.csv).")
    if "pesan" in st.session_state: st.success(st.session_state.pop("pesan"))
    W = wilayah(); wajib = [k for k in KOLOM if k not in ("lat","lon")]
    t1,t2,t3,t4 = st.tabs(["Tambah data kasus","Tambah daerah","Impor CSV","Data tersimpan"])
    with t1:
        if not W: st.info("Belum ada daerah. Tambahkan dulu di tab **Tambah daerah**, atau langsung impor CSV.")
        else:
            c = st.columns(2); kab = c[0].selectbox("Kabupaten",list(W),key="d_kab"); kec = c[1].selectbox("Kecamatan",W[kab][2])
            with st.form("f_data"):
                a = st.columns(4)
                thn = a[0].number_input("Tahun",2015,2040,2026); bln = a[1].selectbox("Bulan",range(1,13),format_func=lambda i: BLN[i-1])
                usia = a[2].selectbox("Kelompok usia",USIA); balita = a[3].number_input("Balita diperiksa",1,100000,100)
                kasus = st.number_input("Kasus diare",0,100000,0); s_ = st.columns(4)
                v = [s_[i].slider(n,0,100,50) for i,n in enumerate(["Jamban sehat (%)","Air bersih (%)","Cuci tangan (%)","ASI eksklusif (%)"])]
                if st.form_submit_button("Simpan data",type="primary"):
                    L = load()
                    if kasus > balita: st.error("Kasus tidak boleh lebih besar dari jumlah balita.")
                    elif not L[(L.kabupaten==kab)&(L.kecamatan==kec)&(L.tahun==thn)&(L.bulan==bln)&(L.usia==usia)].empty:
                        st.error("Data untuk kombinasi ini sudah ada. Pilih bulan/tahun/usia lain, atau hapus dulu di tab Data tersimpan.")
                    else:
                        r = dict(kabupaten=kab,kecamatan=kec,lat=W[kab][0],lon=W[kab][1],tahun=int(thn),bulan=int(bln),usia=usia,balita=int(balita),kasus=int(kasus),jamban=v[0],air=v[1],cuci=v[2],asi=v[3])
                        simpan(pd.concat([baca(F_DATA,KOLOM),pd.DataFrame([r])],ignore_index=True),F_DATA)
                        st.session_state["pesan"] = f"Data {kec}, {BLN[bln-1]} {thn} tersimpan."; st.rerun()
    with t2:
        pilih = st.selectbox("Kabupaten",list(W)+["+ Kabupaten baru…"],key="w_kab"); baru = pilih.startswith("+")
        with st.form("f_wil",clear_on_submit=True):
            kab = st.text_input("Nama kabupaten baru").strip() if baru else pilih
            if baru: g = st.columns(2); lat = g[0].number_input("Latitude",-90.0,90.0,2.5,format="%.4f"); lon = g[1].number_input("Longitude",-180.0,180.0,99.0,format="%.4f")
            else: lat, lon = W[pilih][:2]
            kec = st.text_input("Nama kecamatan baru").strip()
            if st.form_submit_button("Simpan daerah",type="primary"):
                if not kab or not kec: st.error("Nama kabupaten dan kecamatan wajib diisi.")
                elif kec.lower() in [x.lower() for x in W.get(kab,[0,0,[]])[2]]: st.error("Kecamatan itu sudah ada di kabupaten tersebut.")
                else:
                    simpan(pd.concat([baca(F_WIL,["kabupaten","kecamatan","lat","lon"]),pd.DataFrame([dict(kabupaten=kab,kecamatan=kec,lat=lat,lon=lon)])],ignore_index=True),F_WIL)
                    st.session_state["pesan"] = f"Daerah {kec} ({kab}) ditambahkan. Sekarang isi data kasusnya di tab ‘Tambah data kasus’."; st.rerun()
    with t3:
        st.caption("Kolom wajib: "+", ".join(wajib)+". Kolom opsional: lat, lon (untuk peta). Daerah baru di CSV otomatis terdaftar.")
        st.download_button("Unduh template CSV (header saja)",",".join(wajib+["lat","lon"])+"\n","template_data.csv")
        f = st.file_uploader("Unggah CSV (hanya data berizin dan sudah dianonimkan)",type="csv")
        if f:
            x = pd.read_csv(f); hilang = [k for k in wajib if k not in x.columns]
            if hilang: st.error("Kolom belum ada: "+", ".join(hilang))
            else:
                for k in ("lat","lon"):
                    if k not in x: x[k] = np.nan
                for k in NUM: x[k] = pd.to_numeric(x[k],errors="coerce")
                ok = (x.kabupaten.notna()&x.kecamatan.notna()&x.usia.isin(USIA)&x.bulan.between(1,12)&x.tahun.between(2000,2100)&(x.balita>0)&(x.kasus>=0)
                      &(x.kasus<=x.balita)&x[["jamban","air","cuci","asi"]].apply(lambda c: c.between(0,100)).all(axis=1))
                st.write(f"**{int(ok.sum())}** baris valid, **{int((~ok).sum())}** ditolak (usia di luar daftar, angka tidak valid, atau kasus > balita).")
                st.dataframe(x.head(20),hide_index=True,width="stretch")
                if ok.any() and st.button("Tambahkan ke data",type="primary"):
                    gab = pd.concat([baca(F_DATA,KOLOM),x[ok][KOLOM]],ignore_index=True).drop_duplicates(KUNCI,keep="last")
                    simpan(gab,F_DATA); st.session_state["pesan"] = f"{int(ok.sum())} baris ditambahkan (duplikat diperbarui)."; st.rerun()
    with t4:
        for judul,p_,cols in [("Data kasus",F_DATA,KOLOM),("Daerah terdaftar",F_WIL,["kabupaten","kecamatan","lat","lon"])]:
            x = baca(p_,cols); st.markdown(f"**{judul}** · {len(x)} baris")
            ev = st.dataframe(x,hide_index=True,width="stretch",height=220,on_select="rerun",selection_mode="multi-row",key="t_"+judul)
            if ev.selection.rows and st.button(f"Hapus {len(ev.selection.rows)} baris terpilih",key="h_"+judul):
                simpan(x.drop(index=ev.selection.rows),p_); st.session_state["pesan"] = "Baris dihapus."; st.rerun()
        with st.expander("Hapus semua data"):
            if st.checkbox("Saya yakin ingin mengosongkan semua data") and st.button("Kosongkan data",type="primary"):
                for p_ in (F_DATA,F_WIL): p_.unlink(missing_ok=True)
                st.session_state["pesan"] = "Semua data dikosongkan."; st.rerun()

st.sidebar.markdown("### SI-Diare Balita"); st.sidebar.caption("Surveilans diare akut balita")
nav = st.navigation([st.Page(p_dash,title="Dashboard",icon=":material/dashboard:",default=True),
    st.Page(p_wilayah,title="Analisis Wilayah",icon=":material/map:"),st.Page(p_sanitasi,title="Sanitasi",icon=":material/water_drop:"),
    st.Page(p_prediksi,title="Prediksi",icon=":material/psychology:"),st.Page(p_data,title="Data & Laporan",icon=":material/table_chart:"),
    st.Page(p_kelola,title="Kelola Data",icon=":material/edit_note:")])
nav.run()