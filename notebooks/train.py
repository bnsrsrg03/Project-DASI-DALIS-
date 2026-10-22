"""Latih 3 model, bandingkan, simpan. Jalankan: python notebooks/train.py"""
import sqlite3, json, joblib, pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import f1_score, roc_auc_score
X_COLS = ["jamban_sehat","air_bersih","cuci_tangan","asi_eksklusif","imunisasi_lengkap","gizi_kurang"]
df = pd.read_sql("SELECT * FROM fact_bali   ta", sqlite3.connect("diare.db"))
Xtr,Xte,ytr,yte = train_test_split(df[X_COLS],df["diare"],test_size=.2,stratify=df["diare"],random_state=42)
M = {"LogReg (baseline)":LogisticRegression(max_iter=1000,class_weight="balanced"),
     "RandomForest":RandomForestClassifier(300,random_state=42,class_weight="balanced"),
     "GradientBoosting":GradientBoostingClassifier(random_state=42)}
best,bs=None,-1
for n,m in M.items():
    m.fit(Xtr,ytr); p=m.predict_proba(Xte)[:,1]
    f1,auc=f1_score(yte,p>=.5),roc_auc_score(yte,p); print(f"{n}: F1={f1:.3f} AUC={auc:.3f}")
    if auc>bs: best,bs=n,auc
print("Terbaik:",best); joblib.dump(M[best],"model.joblib")
lr=M["LogReg (baseline)"]   # dipakai Go lewat model.json
json.dump({"intercept":float(lr.intercept_[0]),"coef":dict(zip(X_COLS,map(float,lr.coef_[0])))},open("model.json","w"),indent=1)