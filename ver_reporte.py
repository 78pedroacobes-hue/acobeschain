import json

with open("acobes_blockchain_ledger.json") as f:
    d = json.load(f)

chain = d.get("chain", [])
canciones = len(chain) - 1
supply = d.get("total_tokens_supply", 0.0)
usd = d.get("total_royalty_accrued_usd", 0.0)

print("==========================================================")
print("         REPORTE DE ADQUISICION DE CATALOGO ACOBES        ")
print("==========================================================")
print(f" Canciones registradas  : {canciones}")
print(f" Total de bloques       : {len(chain)}")
print(f" Suministro Total ACOB  : {supply} ACOB")
print(f" Regalias Acumuladas    : ${usd:.2f} USD")
print("----------------------------------------------------------")
print(" Ultimas 15 canciones selladas en la cadena:")
for b in chain[-15:]:
    idx = b.get("index")
    trk = b.get("track")
    tok = b.get("tokens_minted")
    print(f"  [#{idx:03d}] {trk} -> {tok} ACOB")
print("==========================================================")
