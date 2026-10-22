package main

import (
	"database/sql"
	"encoding/json"
	"log"
	"math"
	"math/rand"
	"net/http"
	"os"
	"strings"

	_ "modernc.org/sqlite"
)

var db *sql.DB

const from = ` FROM fact_balita f JOIN dim_waktu w ON w.id=f.waktu_id
 JOIN dim_wilayah k ON k.id=f.wilayah_id JOIN dim_usia u ON u.id=f.usia_id `

var dims = map[string]string{"usia": "u.kelompok", "bulan": "printf('%02d',w.bulan)", "tahun": "w.tahun", "kecamatan": "k.kecamatan", "kabupaten": "k.kabupaten"}
var factors = map[string]bool{"jamban_sehat": true, "air_bersih": true, "cuci_tangan": true, "asi_eksklusif": true, "imunisasi_lengkap": true, "gizi_kurang": true}

func where(r *http.Request) (string, []any) {
	c, a := []string{"1=1"}, []any{}
	if v := r.URL.Query().Get("kab"); v != "" {
		c, a = append(c, "k.kabupaten=?"), append(a, v)
	}
	if v := r.URL.Query().Get("tahun"); v != "" {
		c, a = append(c, "w.tahun=?"), append(a, v)
	}
	return strings.Join(c, " AND "), a
}

func js(w http.ResponseWriter, v any) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(v)
}

func agg(expr string, r *http.Request) []map[string]any {
	wh, a := where(r)
	rows, err := db.Query("SELECT "+expr+" AS k, COUNT(*), SUM(f.diare)"+from+"WHERE "+wh+" GROUP BY k ORDER BY k", a...)
	if err != nil {
		log.Println(err)
		return nil
	}
	defer rows.Close()
	out := []map[string]any{}
	for rows.Next() {
		var k any
		var n, d int
		rows.Scan(&k, &n, &d)
		out = append(out, map[string]any{"label": k, "n": n, "kasus": d, "rate": float64(d) / float64(n) * 100})
	}
	return out
}

func main() {
	var err error
	db, err = sql.Open("sqlite", "diare.db")
	if err != nil {
		log.Fatal(err)
	}
	initSchema()

	http.HandleFunc("/api/filters", func(w http.ResponseWriter, r *http.Request) {
		js(w, map[string]any{"kabupaten": agg("k.kabupaten", r), "tahun": agg("w.tahun", r)})
	})
	http.HandleFunc("/api/summary", func(w http.ResponseWriter, r *http.Request) {
		wh, a := where(r)
		var n, d, nAll, dAll int
		db.QueryRow("SELECT COUNT(*),COALESCE(SUM(f.diare),0)"+from+"WHERE "+wh, a...).Scan(&n, &d)
		db.QueryRow("SELECT COUNT(*),COALESCE(SUM(diare),0) FROM fact_balita").Scan(&nAll, &dAll)
		var jb, ab float64
		db.QueryRow("SELECT COALESCE(AVG(jamban_sehat),0)*100,COALESCE(AVG(air_bersih),0)*100"+from+"WHERE "+wh, a...).Scan(&jb, &ab)
		js(w, map[string]any{"balita": n, "kasus": d, "prevalensi": pct(d, n), "prevalensi_semua": pct(dAll, nAll), "jamban": jb, "air": ab})
	})
	http.HandleFunc("/api/by", func(w http.ResponseWriter, r *http.Request) {
		e, ok := dims[r.URL.Query().Get("dim")]
		if !ok {
			http.Error(w, "dim tidak valid", 400)
			return
		}
		js(w, agg(e, r))
	})
	http.HandleFunc("/api/risk", func(w http.ResponseWriter, r *http.Request) {
		out := map[string]any{}
		for f := range factors {
			out[f] = agg("f."+f, r)
		}
		js(w, out)
	})
	http.HandleFunc("/api/predict", predict)
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) { js(w, map[string]string{"status": "ok"}) })

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	log.Println("listen :" + port)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}

func pct(a, b int) float64 {
	if b == 0 {
		return 0
	}
	return float64(a) / float64(b) * 100
}

// Scoring logistic regression dari model.json (hasil training Python).
func predict(w http.ResponseWriter, r *http.Request) {
	var req struct{ Features map[string]float64 }
	if json.NewDecoder(r.Body).Decode(&req) != nil {
		http.Error(w, "json tidak valid", 400)
		return
	}
	var m struct {
		Intercept float64
		Coef      map[string]float64
	}
	b, err := os.ReadFile("model.json")
	if err != nil || json.Unmarshal(b, &m) != nil {
		http.Error(w, "model.json tidak terbaca", 500)
		return
	}
	z := m.Intercept
	for k, c := range m.Coef {
		z += c * req.Features[k]
	}
	p := 1 / (1 + math.Exp(-z))
	kelas := "Tidak Diare"
	if p >= 0.5 {
		kelas = "Diare"
	}
	js(w, map[string]any{"probabilitas": p, "kelas": kelas})
}

func initSchema() {
	db.Exec(`CREATE TABLE IF NOT EXISTS dim_wilayah(id INTEGER PRIMARY KEY, kabupaten TEXT, kecamatan TEXT);
CREATE TABLE IF NOT EXISTS dim_waktu(id INTEGER PRIMARY KEY, tahun INT, bulan INT);
CREATE TABLE IF NOT EXISTS dim_usia(id INTEGER PRIMARY KEY, kelompok TEXT);
CREATE TABLE IF NOT EXISTS fact_balita(id INTEGER PRIMARY KEY, wilayah_id INT, waktu_id INT, usia_id INT,
 diare INT, jamban_sehat INT, air_bersih INT, cuci_tangan INT, asi_eksklusif INT, imunisasi_lengkap INT, gizi_kurang INT);`)
	var c int
	db.QueryRow("SELECT COUNT(*) FROM fact_balita").Scan(&c)
	if c > 0 {
		return
	}
	log.Println("DB kosong -> seed data DUMMY. Ganti dengan ETL data asli.")
	tx, _ := db.Begin()
	kab := []string{"Toba", "Samosir", "Simalungun", "Humbang Hasundutan"}
	id := 1
	for _, k := range kab {
		for i := 1; i <= 3; i++ {
			tx.Exec("INSERT INTO dim_wilayah VALUES(?,?,?)", id, k, k+" Kec-"+string(rune('A'+i-1)))
			id++
		}
	}
	id = 1
	for t := 2023; t <= 2025; t++ {
		for b := 1; b <= 12; b++ {
			tx.Exec("INSERT INTO dim_waktu VALUES(?,?,?)", id, t, b)
			id++
		}
	}
	for i, u := range []string{"0-11 bln", "12-23 bln", "24-35 bln", "36-47 bln", "48-59 bln"} {
		tx.Exec("INSERT INTO dim_usia VALUES(?,?)", i+1, u)
	}
	bin := func(p float64) int {
		if rand.Float64() < p {
			return 1
		}
		return 0
	}
	for i := 0; i < 6000; i++ {
		jb, ab, ct, as, im, gz := bin(.7), bin(.75), bin(.6), bin(.5), bin(.65), bin(.2)
		u := rand.Intn(5) + 1
		z := -1.6 - .6*float64(jb) - .7*float64(ab) - .5*float64(ct) - .4*float64(as) - .3*float64(im) + .8*float64(gz)
		if u <= 2 {
			z += .5
		}
		d := bin(1 / (1 + math.Exp(-z)))
		tx.Exec("INSERT INTO fact_balita(wilayah_id,waktu_id,usia_id,diare,jamban_sehat,air_bersih,cuci_tangan,asi_eksklusif,imunisasi_lengkap,gizi_kurang) VALUES(?,?,?,?,?,?,?,?,?,?)",
			rand.Intn(12)+1, rand.Intn(36)+1, u, d, jb, ab, ct, as, im, gz)
	}
	tx.Commit()
}