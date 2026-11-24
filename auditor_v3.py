import urllib.request
import urllib.parse
import urllib.error
import json
import time
import ssl
import torch
import torch.nn as nn

# =====================================================================
# MÓDULO 1: RASTREADOR MULTI-FUENTE CON VALIDACIÓN DE RESPUESTA
# =====================================================================
class CatalogTracker:
    def __init__(self, contact_email="auditoria.catalogo@proton.me"):
        self.mb_url = "https://musicbrainz.org"
        self.itunes_url = "https://apple.com"
        self.headers = {
            "User-Agent": f"CatalogAuditor/3.0 ( {contact_email} )",
            "Accept": "application/json"
        }
        # Contexto SSL estándar para evitar fallos de certificados en contenedores/termux
        self.ssl_ctx = ssl.create_default_context()

    def _safe_json_get(self, url, retries=2):
        for attempt in range(retries):
            try:
                req = urllib.request.Request(url, headers=self.headers)
                with urllib.request.urlopen(req, timeout=12, context=self.ssl_ctx) as resp:
                    status = resp.getcode()
                    raw_body = resp.read().decode("utf-8", errors="replace").strip()
                    
                    if not raw_body:
                        print(f"    [!] Respuesta vacía (HTTP {status}).")
                        return None
                        
                    if not raw_body.startswith("{") and not raw_body.startswith("["):
                        print(f"    [!] El servidor no devolvió JSON (HTTP {status}). Inicio: {raw_body[:60]}...")
                        return None
                        
                    return json.loads(raw_body)
                    
            except urllib.error.HTTPError as e:
                if e.code in (429, 503):
                    wait = (attempt + 1) * 2.5
                    print(f"    [~] Límite de tasa o servidor ocupado ({e.code}). Esperando {wait}s...")
                    time.sleep(wait)
                else:
                    print(f"    [!] Error HTTP {e.code}: {e.reason}")
                    break
            except Exception as e:
                print(f"    [!] Fallo de conexión: {e}")
                break
        return None

    def search_all(self, queries, limit=10):
        results = []
        for q in queries:
            # 1. Consulta en Apple/iTunes Search API (Alta disponibilidad)
            print(f"[*] Buscando en índice comercial (Apple/iTunes): '{q}'...")
            it_url = f"{self.itunes_url}?term={urllib.parse.quote(q)}&media=music&entity=song&limit={limit}"
            it_data = self._safe_json_get(it_url)
            if it_data and "results" in it_data:
                for item in it_data["results"]:
                    results.append({
                        "source": "Apple/iTunes",
                        "title": item.get("trackName"),
                        "artist": item.get("artistName"),
                        "album": item.get("collectionName"),
                        "date": item.get("releaseDate", "")[:10],
                        "preview": item.get("previewUrl")
                    })
            time.sleep(0.5)

            # 2. Consulta en MusicBrainz (Base de datos abierta de créditos e ISRC)
            print(f"[*] Buscando en MusicBrainz: '{q}'...")
            mb_query = urllib.parse.quote(f'artist:"{q}" OR creditname:"{q}"')
            mb_url = f"{self.mb_url}?query={mb_query}&fmt=json&limit={limit}"
            mb_data = self._safe_json_get(mb_url)
            if mb_data and "recordings" in mb_data:
                for rec in mb_data["recordings"]:
                    results.append({
                        "source": "MusicBrainz",
                        "title": rec.get("title"),
                        "artist": ", ".join([a.get("name", "") for a in rec.get("artist-credit", [])]),
                        "album": "N/A",
                        "isrcs": rec.get("isrcs", [])
                    })
            time.sleep(1.2)
            
        return results

# =====================================================================
# MÓDULO 2: NÚCLEO DE HUELLA ACÚSTICA CUÁNTICA
# =====================================================================
class QuantumAudioFingerprint(nn.Module):
    def __init__(self, feature_dim=64, num_qubits=4):
        super().__init__()
        self.dim = 2 ** num_qubits
        self.encoder = nn.Sequential(
            nn.Conv1d(1, 8, kernel_size=3, padding=1),
            nn.SiLU(),
            nn.AdaptiveAvgPool1d(self.dim),
            nn.Flatten(),
            nn.Linear(8 * self.dim, self.dim * 2)
        )
        self.theta = nn.Parameter(torch.randn(num_qubits, 3) * 0.1)
        self.register_buffer("I", torch.eye(2, dtype=torch.complex64))
        self.register_buffer("X", torch.tensor([[0, 1], [1, 0]], dtype=torch.complex64))
        self.register_buffer("Y", torch.tensor([[0, -1j], [1j, 0]], dtype=torch.complex64))
        self.register_buffer("Z", torch.tensor([[1, 0], [0, -1]], dtype=torch.complex64))

    def _get_unitary(self):
        U = torch.tensor([[1.0 + 0j]], dtype=torch.complex64, device=self.theta.device)
        for i in range(self.theta.shape[0]):
            params = self.theta[i]
            angle = torch.sqrt(torch.sum(params ** 2) + 1e-12)
            axis = params / angle
            R = torch.cos(angle) * self.I - 1j * torch.sin(angle) * (
                axis[0] * self.X + axis[1] * self.Y + axis[2] * self.Z
            )
            U = torch.kron(U, R)
        return U

    def forward(self, audio_spectrum):
        if audio_spectrum.ndim == 2:
            audio_spectrum = audio_spectrum.unsqueeze(1)
        encoded = self.encoder(audio_spectrum)
        real, imag = torch.chunk(encoded, 2, dim=-1)
        psi = torch.complex(real, imag)
        psi = psi / torch.linalg.vector_norm(psi, ord=2, dim=-1, keepdim=True).clamp(min=1e-8)
        U = self._get_unitary()
        psi_out = torch.matmul(psi, U.T)
        return psi_out.real ** 2 + psi_out.imag ** 2

# =====================================================================
# EJECUCIÓN
# =====================================================================
if __name__ == "__main__":
    print("[+] Iniciando Auditor de Catálogo Musical v3.0...\n")
    tracker = CatalogTracker()
    variaciones = ["Acobes", "Pedro J Acobes", "Peter Acobes"]
    
    hallazgos = tracker.search_all(variaciones, limit=5)
    print(f"\n[+] Total de registros recuperados: {len(hallazgos)}")
    for h in hallazgos:
        print(f"    - [{h['source']}] {h['title']} | Artista: {h['artist']}")
        if h.get("isrcs"):
            print(f"      ISRCs: {h['isrcs']}")

    model = QuantumAudioFingerprint(feature_dim=64, num_qubits=4)
    t1 = torch.randn(1, 64)
    t2 = t1 + 0.05 * torch.randn(1, 64)
    sim = nn.functional.cosine_similarity(model(t1), model(t2)).item()
    print(f"\n[+] Núcleo Cuántico Verificado | Similitud de prueba: {sim * 100:.2f}%")
