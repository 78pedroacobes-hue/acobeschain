import urllib.request
import urllib.parse
import json
import os
import wave
import numpy as np
import torch
import torch.nn as nn

# =====================================================================
# MÓDULO 1: RASTREADOR DE CATÁLOGO DISTRIBUIDO (ITUNES / APPLE MUSIC API)
# =====================================================================
class AppleCatalogTracker:
    """
    Consulta el índice global de Apple Music / iTunes para localizar
    lanzamientos distribuidos por DistroKid, fechas, álbumes y vistas previas.
    """
    def __init__(self):
        self.base_url = "https://itunes.apple.com/search"

    def search_catalog(self, terms, limit=50):
        found_tracks = []
        seen_ids = set()

        for term in terms:
            encoded = urllib.parse.quote(term)
            url = f"{self.base_url}?term={encoded}&media=music&entity=song&limit={limit}"
            try:
                with urllib.request.urlopen(url, timeout=15) as response:
                    data = json.loads(response.read().decode("utf-8"))
                    for item in data.get("results", []):
                        track_id = item.get("trackId")
                        artist = item.get("artistName", "")
                        # Filtra coincidencias relevantes a tus nombres artísticos
                        if track_id not in seen_ids and any(
                            k in artist.lower() for k in ["acobes", "peter acobes", "pedro"]
                        ):
                            seen_ids.add(track_id)
                            found_tracks.append({
                                "track_id": track_id,
                                "artist": artist,
                                "title": item.get("trackName"),
                                "album": item.get("collectionName"),
                                "release_date": item.get("releaseDate", "")[:10],
                                "genre": item.get("primaryGenreName"),
                                "preview_url": item.get("previewUrl")
                            })
            except Exception as e:
                print(f"[!] Error consultando '{term}': {e}")

        return found_tracks

# =====================================================================
# MÓDULO 2: EXTRACTOR ESPECTRAL Y HUELLA CUÁNTICA (PYTORCH)
# =====================================================================
def extract_wav_spectrum(filepath, bins=64):
    """Lee un archivo WAV real y extrae su perfil espectral FFT normalizado."""
    with wave.open(filepath, 'rb') as wf:
        frames = wf.readframes(min(wf.getnframes(), wf.getframerate() * 15))
        dtype = np.int16 if wf.getsampwidth() == 2 else np.uint8
        audio = np.frombuffer(frames, dtype=dtype).astype(np.float32)
        if wf.getnchannels() > 1:
            audio = audio.reshape(-1, wf.getnchannels()).mean(axis=1)
        
        fft_mag = np.abs(np.fft.rfft(audio))
        # Agrupa el espectro en 64 bandas de frecuencia
        chunks = np.array_split(fft_mag, bins)
        spectrum = np.array([np.mean(c) for c in chunks], dtype=np.float32)
        spectrum = (spectrum - spectrum.mean()) / (spectrum.std() + 1e-8)
        return torch.tensor(spectrum).unsqueeze(0)

class QuantumAudioFingerprint(nn.Module):
    def __init__(self, feature_dim=64, num_qubits=4):
        super().__init__()
        self.num_qubits = num_qubits
        self.dim = 2 ** num_qubits
        self.encoder = nn.Sequential(
            nn.Conv1d(1, 8, kernel_size=3, padding=1),
            nn.SiLU(),
            nn.AdaptiveAvgPool1d(self.dim),
            nn.Flatten(),
            nn.Linear(8 * self.dim, self.dim * 2),
            nn.LayerNorm(self.dim * 2)
        )
        self.theta = nn.Parameter(torch.randn(num_qubits, 3) * 0.1)
        self.register_buffer("I", torch.eye(2, dtype=torch.complex64))
        self.register_buffer("X", torch.tensor([[0, 1], [1, 0]], dtype=torch.complex64))
        self.register_buffer("Y", torch.tensor([[0, -1j], [1j, 0]], dtype=torch.complex64))
        self.register_buffer("Z", torch.tensor([[1, 0], [0, -1]], dtype=torch.complex64))
        self.register_buffer("entangler", self._build_ring_entangler())

    def _build_ring_entangler(self):
        E = torch.eye(self.dim, dtype=torch.complex64)
        for q in range(self.num_qubits):
            target = (q + 1) % self.num_qubits
            for state_idx in range(self.dim):
                if ((state_idx >> (self.num_qubits - 1 - q)) & 1) and ((state_idx >> (self.num_qubits - 1 - target)) & 1):
                    E[state_idx, state_idx] *= -1.0
        return E

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
        return self.entangler @ U

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
    print("[+] Consultando catálogo distribuido en Apple Music / iTunes...")
    tracker = AppleCatalogTracker()
    pistas = tracker.search_catalog(["Peter Acobes", "Pedro J. Acobes", "Pedro Juan Acobes", "Acobes"])
    
    print(f"[+] Pistas oficiales indexadas en tiendas: {len(pistas)}")
    for p in pistas:
        print(f"    - [{p['release_date']}] {p['artist']} - {p['title']} (Álbum: {p['album']})")

    # Guardar reporte local en JSON
    with open("catalogo_distribuido_auditado.json", "w", encoding="utf-8") as f:
        json.dump(pistas, f, indent=2, ensure_ascii=False)
    print("[+] Reporte guardado en 'catalogo_distribuido_auditado.json'")

    # Prueba con audio WAV real si existe alguno en el directorio actual
    model = QuantumAudioFingerprint(feature_dim=64, num_qubits=4)
    wav_files = [f for f in os.listdir(".") if f.lower().endswith(".wav")]
    if wav_files:
        espectro = extract_wav_spectrum(wav_files[0])
        firma = model(espectro)
        print(f"[+] Huella cuántica extraída de '{wav_files[0]}': {firma.detach().numpy().round(4)}")
    else:
        print("[*] Coloca un archivo .wav en esta carpeta (o apunta a /sdcard/Music) para extraer su huella real.")
