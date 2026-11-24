import os
import glob
import json
import hashlib
import torch
import torch.nn as nn

# =====================================================================
# MÓDULO 1: EXTRACTOR DE ESPECTRO LOCAL (SIN DEPENDENCIA DE INTERNET)
# =====================================================================
class LocalAudioExtractor:
    def __init__(self, extensions=("*.wav", "*.mp3", "*.m4a", "*.flac", "*.ogg")):
        self.extensions = extensions

    def scan_directory(self, folder_path="."):
        files = []
        for ext in self.extensions:
            files.extend(glob.glob(os.path.join(folder_path, "**", ext), recursive=True))
        return sorted(files)

    def extract_features(self, file_path, target_len=64):
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            raw_bytes = f.read()
            sha256.update(raw_bytes)
        file_hash = sha256.hexdigest()

        try:
            import torchaudio
            waveform, _ = torchaudio.load(file_path)
            mono = waveform.mean(dim=0)
            fft_mag = torch.abs(torch.fft.rfft(mono))
        except Exception:
            byte_tensor = torch.tensor(list(raw_bytes[:65536]), dtype=torch.float32)
            if byte_tensor.numel() == 0:
                byte_tensor = torch.zeros(target_len)
            fft_mag = torch.abs(torch.fft.rfft(byte_tensor))

        spectrum = nn.functional.adaptive_avg_pool1d(
            fft_mag.view(1, 1, -1), target_len
        ).squeeze(0)
        
        spectrum = (spectrum - spectrum.mean()) / (spectrum.std() + 1e-8)
        return spectrum, file_hash


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
        
        # Matrices de Pauli completas y válidas
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
# EJECUCIÓN Y GENERACIÓN DE INVENTARIO PARA REGISTRO
# =====================================================================
if __name__ == "__main__":
    CARPETA_MUSICA = "."
    
    print(f"[+] Escaneando catálogo local en: {os.path.abspath(CARPETA_MUSICA)}")
    extractor = LocalAudioExtractor()
    model = QuantumAudioFingerprint(feature_dim=64, num_qubits=4)
    model.eval()

    archivos = extractor.scan_directory(CARPETA_MUSICA)
    print(f"[+] Archivos de audio detectados: {len(archivos)}")

    inventario = []
    with torch.no_grad():
        for ruta in archivos:
            espectro, sha256 = extractor.extract_features(ruta)
            firma_cuantica = model(espectro).squeeze(0).tolist()
            
            registro = {
                "archivo": os.path.basename(ruta),
                "ruta": ruta,
                "sha256_integridad": sha256,
                "firma_hilbert_16d": [round(v, 6) for v in firma_cuantica]
            }
            inventario.append(registro)
            print(f"    - Procesado: {registro['archivo']} | SHA256: {sha256[:12]}...")

    with open("inventario_catalogo_cuantico.json", "w", encoding="utf-8") as f:
        json.dump(inventario, f, indent=4, ensure_ascii=False)

    print("\n[+] Reporte guardado en 'inventario_catalogo_cuantico.json'.")
