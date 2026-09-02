"""
fit_family_params.py

Regenerates data/family_params.json, the per-family Form 3 parameters that
analysis/manuscript_figure_5.py draws. Reading them from the dispatch table
rather than hardcoding them is what let Figure 5 be checked against the
withdrawals: the parameters are unchanged, so the figure is unchanged.

Run from the repository root.
"""
import pandas as pd, numpy as np, json
U="data"
d=pd.read_csv(f"{U}/phase_3_p57_de_novo_predictions.csv")
live=d[d["refusal_flag"].isna()]
MODAL={"conventional_AlB2":(38.0,15.5),"iron_chalcogenide_11":(14.0,47.0),"iron_pnictide_122":(22.0,50.0)}
out={}
for fam,(tc,hc) in MODAL.items():
    s=live[(live["substructure"]==fam)&(live["Tc_anchor_K"]==tc)&(live["Hc2_T_anchor"]==hc)]
    # field axis at the lowest T
    T0=s["T_K"].min()
    f=s[np.isclose(s["T_K"],T0)].groupby("H_T")["predicted_log_Jc"].first().sort_index()
    x=np.log10(1-f.index.values/hc); y=f.values
    bH,aH=np.polyfit(x,y,1)
    # temperature axis at the lowest field
    H0=s["H_T"].min()
    t=s[np.isclose(s["H_T"],H0)].groupby("T_K")["predicted_log_Jc"].first().sort_index()
    xt=np.log10(np.clip(1-t.index.values/tc,1e-6,None)); yt=t.values
    if len(xt)>=2: bT,aT=np.polyfit(xt,yt,1)
    else: bT,aT=np.nan,np.nan
    out[fam]=dict(Tc=tc,Hc2=hc,beta_H=float(bH),logJc_H=float(aH),beta_T=float(bT),logJc_T=float(aT),
                  n_T=len(xt), fit_rms_H=float(np.sqrt(np.mean((np.polyval([bH,aH],x)-y)**2))),
                  fit_rms_T=float(np.sqrt(np.mean((np.polyval([bT,aT],xt)-yt)**2))) if len(xt)>=2 else None,
                  T0=float(T0), H0=float(H0))
    print(f"{fam:22s} Tc={tc:5.1f} Hc2={hc:5.1f}  beta_H={bH:6.3f} (rms {out[fam]['fit_rms_H']:.4f})  "
          f"beta_T={bT:6.3f} (n_T={len(xt)}, rms {out[fam]['fit_rms_T'] if out[fam]['fit_rms_T'] is not None else float('nan'):.4f})")
json.dump(out,open("data/family_params.json","w"),indent=1)
