import urllib.request
import urllib.parse
import json
import os
import wave
import numpy as np
import torch
import torch.nn as nn

class MultiCatalogTracker:
    def search_deezer(self, terms, limit=25):
        found = []
        seen = set()
        for term in terms:
            q = urllib.parse.quote(term)
            url = f"https://deezer.com{q}&limit={limit}"
            try:
                with urllib.request.urlopen(url, timeout=12) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    for item in data.get("data", []):
                        tid = item.get("id")
                        artist = item.get("artist", {}).get("name", "")
                        if tid not in seen and "acobes" in artist.lower():
                            seen.add(tid)
                            found.append({
                                "source": "Deezer",
                                "id": tid,
                                "artist": artist,
                                "title": item.get("title"),
                                "album": item.get("album", {}).get("title"),
                                "preview": item.get("preview")
                            })
            except Exception as e:
                print(f"[!] Error en Deezer ({term}): {e}")
        return found

def extract_wav_spectrum(filepath, bins=64):
    with wave.open(filepath, 'rb') as wf:
        frames = wf.readframes(min(wf.getnframes(), wf.getframerate() * 15))
        dtype = np.int16 if wf.getsampwidth() == 2 else np.uint8
        audio = np.frombuffer(frames, dtype=dtype).astype(np.float32)
        if wf.getnchannels() > 1:
            audio = audio.reshape(-1, wf.getnchannels()).mean(axis=1)
        fft_mag = np.abs(np.fft.rfft(audio))
        chunks = np.array_split(fft_mag, bins)
        spectrum = np.array([np.mean(c) for c in chunks], dtype=np.float32)
        spectrum = (spectrum - spectrum.mean()) / (spectrum.std() + 1e-8)
        return torch.tensor(spectrum).unsqueeze(0)

class QuantumAudioFingerprint(nn.Module):
    def __init__(self, num_qubits=4):
        super().__init__()
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

    def _get_unitary(self):
        U = torch.tensor([[1.0 + 0j]], dtype=torch.complex64, device=self.theta.device)
        for i in range(self.theta.shape[0]):
            p = self.theta[i]
            ang = torch.sqrt(torch.sum(p ** 2) + 1e-12)
            ax = p / ang
            R = torch.cos(ang) * self.I - 1j * torch.sin(ang) * (ax[0]*self.X + ax[1]*self.Y + ax[2]*self.Z)
            U = torch.kron(U, R)
        return U

    def forward(self, x):
        if x.ndim == 2:
            x = x.unsqueeze(1)
        real, imag = torch.chunk(self.encoder(x), 2, dim=-1)
        psi = torch.complex(real, imag)
        psi = psi / torch.linalg.vector_norm(psi, ord=2, dim=-1, keepdim=True).clamp(min=1e-8)
        psi_out = torch.matmul(psi, self._get_unitary().T)
        return psi_out.real ** 2 + psi_out.imag ** 2

if __name__ == "__main__":
    print("[+] Buscando en catálogo abierto de Deezer...")
    tracker = MultiCatalogTracker()
    pistas = tracker.search_deezer(["Peter Acobes", "Pedro J. Acobes", "Pedro Juan Acobes", "Acobes"])
    print(f"[+] Pistas encontradas en Deezer: {len(pistas)}")
    for p in pistas:
        print(f"    - {p['artist']} | {p['title']} (Álbum: {p['album']})")

    wavs = [f for f in os.listdir(".") if f.lower().endswith(".wav")]
    print(f"[+] Archivos .WAV locales detectados: {len(wavs)}")
    model = QuantumAudioFingerprint()
    model.eval()
    with torch.no_grad():
        for w in wavs:
            spec = extract_wav_spectrum(w)
            sig = model(spec).squeeze(0).tolist()
            print(f"    - Firma cuántica de '{w}': {[round(x, 4) for x in sig[:4]]}...")
