import json
import numpy as np

with open("uog_100_lattice_result.json", "r") as f:
    data = json.load(f)

metrics = [k for k in data[0].keys() if k not in ["op_id", "params_norm"]]
all_vals = {m: np.array([op[m] for op in data]) for m in metrics}

# Buscar el operador con mayor ipr_max en todo el ensemble de 1000
best_idx = np.argmax([op["ipr_max"] for op in data])
best_op = data[best_idx]

print("=" * 65)
print(f" OPERADOR MÁS LOCALIZADO DEL ENSEMBLE (ID: {best_op['op_id']})")
print("=" * 65)
print(f"{'feature':<20} {'valor óptimo':<14} {'pct':<10} {'ext'}")
print("-" * 65)

extremos = []
for m in metrics:
    val = best_op[m]
    vals = all_vals[m]
    pct = float(np.mean(vals <= val) * 100)
    is_ext = pct < 5.0 or pct > 95.0
    ext_str = "***" if is_ext else ""
    if is_ext:
        extremos.append((m, val, pct))
    print(f"{m:<20} {val:<14.6f} {pct:<10.2f}% {ext_str}")

print("-" * 65)
print(f"Extremos (<5% o >95%): {len(extremos)}/{len(metrics)}")
for m, val, pct in extremos:
    print(f"               {m} = {val:+.6f}  (pct {pct:.2f}%)")
