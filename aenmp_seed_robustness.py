


import subprocess, re, csv, os, sys
from datetime import datetime
from aenmp_seed_base import derive_seed, SEED_BASE
RESULTS_FILE = "aenmp_seed_results.csv"
SCRIPT = "aenmp_k_explain_jump_v1.py"

def parse(out):
    d = {}
    m = re.search(r"Exitos:\s*(\d+)", out)
    if m: d["exitos"] = int(m.group(1))
    for h in [10,11,12,13,14]:
        m = re.search(rf"hops={h}:\s*(\d+)\s*rutas\s*\(([\d\.]+)%", out)
        if m: d[f"hops{h}_pct"] = float(m.group(2))
    sec = out.split("Refinamiento media")[1].split("Refinamiento proporcion")[0] if "Refinamiento media" in out else ""
    d["media_cruza"] = -1
    for line in sec.splitlines():
        m = re.search(r"k=([\d\.]+):.*\? (True|False)", line)
        if m and m.group(2)=="True":
            d["media_cruza"] = float(m.group(1)); break
    sec2 = out.split("Refinamiento proporcion")[1] if "Refinamiento proporcion" in out else ""
    d["prop100"] = -1; d["p0641"] = -1
    for line in sec2.splitlines():
        m = re.search(r"k=([\d\.]+):\s*P>0\.85\|exito\s*([\d\.]+)%", line)
        if m:
            if float(m.group(1))==0.641: d["p0641"] = float(m.group(2))
            if float(m.group(2))>=99.99 and d["prop100"]==-1: d["prop100"] = float(m.group(1))
    return d

def run_one(i):
    seed = derive_seed(i)
    print(f"\n=== Prueba #{i} Seed {seed} ===")
    r = subprocess.run([sys.executable, SCRIPT, str(i)], capture_output=True, text=True)
    if r.returncode!=0:
        print("ERROR:", r.stderr[:300]); return None
    d = parse(r.stdout); d.update({"n":i,"seed":seed,"fecha":datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    print(f"Exitos {d.get('exitos')} | 11h {d.get('hops11_pct')}% | P0641 {d.get('p0641')}% | media cruza {d.get('media_cruza')} | prop100 {d.get('prop100')}")
    return d

if __name__=="__main__":
    a = int(sys.argv[1]) if len(sys.argv)>1 else 0
    b = int(sys.argv[2]) if len(sys.argv)>2 else 9
    res=[]
    for i in range(a,b+1):
        d=run_one(i)
        if d: res.append(d)
    existe=os.path.exists(RESULTS_FILE)
    with open(RESULTS_FILE,"a",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["fecha","n","seed","exitos","hops10_pct","hops11_pct","hops12_pct","hops13_pct","hops14_pct","p0641","media_cruza","prop100"])
        if not existe: w.writeheader()
        for d in res: w.writerow({k:d.get(k,"") for k in ["fecha","n","seed","exitos","hops10_pct","hops11_pct","hops12_pct","hops13_pct","hops14_pct","p0641","media_cruza","prop100"]})
    if res:
        import statistics
        ex=[d["exitos"] for d in res]; p=[d["p0641"] for d in res]
        print(f"\nRESUMEN: n={len(res)} Exitos media {statistics.mean(ex):.1f} desv {statistics.pstdev(ex):.1f} min {min(ex)} max {max(ex)}")
        print(f"P0641 media {statistics.mean(p):.2f}% min {min(p):.2f}% max {max(p):.2f}%")
        print(f"Media cruza: {[d['media_cruza'] for d in res]}")
        print(f"Prop100: {[d['prop100'] for d in res]} -> todas 0.642? {all(d['prop100']==0.642 for d in res)}")
        print(f"Guardado en {RESULTS_FILE}")
