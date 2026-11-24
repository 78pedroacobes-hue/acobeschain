# Base de oro para semillas - AENMP
# No se toca SEED_BASE a mano. Se cambia solo el numero de prueba.
# Asi todo es reproducible, baby.

import hashlib
import csv
import os
from datetime import datetime

SEED_BASE = 522
RESULTS_FILE = "aenmp_seed_results.csv"

def derive_seed(n_prueba: int) -> int:
    """
    Deriva una semilla deterministica desde la base.
    n_prueba = 0 es la referencia (522)
    n_prueba = 1, 2, 3... son las demas pruebas
    """
    if n_prueba == 0:
        return SEED_BASE
    # Hash de "522:1", "522:2", etc. para que no sea solo +1
    texto = f"{SEED_BASE}:{n_prueba}"
    h = hashlib.sha256(texto.encode()).hexdigest()
    # Semilla entre 1 y 99999, deterministica
    return int(h[:8], 16) % 99999 + 1

def get_seed(n_prueba: int):
    seed = derive_seed(n_prueba)
    print(f"[BASE] Prueba #{n_prueba} -> Semilla {seed} (Base {SEED_BASE})")
    return seed

def log_result(n_prueba: int, seed: int, exitos: int, hops11_pct: float, salto_0641: float, salto_0642: float, media_cruza: str):
    """
    Guarda cada corrida en el CSV. Asi no copiamos y pegamos en el chat.
    """
    existe = os.path.exists(RESULTS_FILE)
    with open(RESULTS_FILE, "a", newline="") as f:
        w = csv.writer(f)
        if not existe:
            w.writerow(["fecha", "n_prueba", "seed", "base", "exitos", "hops11_pct", "P_0.641", "P_0.642", "media_cruza_0.438"])
        w.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            n_prueba, seed, SEED_BASE,
            exitos, hops11_pct, salto_0641, salto_0642, media_cruza
        ])
    print(f"[BASE] Guardado en {RESULTS_FILE} - Prueba #{n_prueba}, Seed {seed}, Exitos {exitos}")

if __name__ == "__main__":
    print("=== BASE DE ORO - SEMILLAS ===")
    print(f"Base: {SEED_BASE}")
    print("")
    print("Tus proximas 10 pruebas ya estan definidas, baby:")
    for i in range(11):
        print(f"  Prueba #{i:2d} -> Semilla {derive_seed(i)}")
    print("")
    print("Uso: from aenmp_seed_base import get_seed")
    print("     seed = get_seed(1)")
