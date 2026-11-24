import os
import glob
import torch
import torch.nn as nn
import numpy as np
import scipy.io.wavfile as wav

print("==============================================================")
print(" PROCESAMIENTO POR LOTES (BATCH) — ARQUITECTURA RECORDS")
print("==============================================================")

# 1. Definición del Motor Cuántico con el Operador #640
class SovereignQuantumMasterEngine(nn.Module):
    def __init__(self):
        super().__init__()
        np.random.seed(640 * 1337 + 99)
        initial_params = np.random.uniform(-np.pi, np.pi, 100)
        
        self.params = nn.Parameter(torch.tensor(initial_params, dtype=torch.float32))
        self.dim = 64
        self.conv = nn.Conv1d(1, 1, kernel_size=3, padding=1)
        self.fc = nn.Linear(64, 64)

    def forward(self, audio_tensor):
        x_conv = torch.relu(self.conv(audio_tensor.unsqueeze(1))).squeeze(1)
        
        H = torch.zeros((self.dim, self.dim), dtype=torch.cfloat)
        diag_vals = torch.complex(self.params[:self.dim], torch.zeros_like(self.params[:self.dim]))
        H = torch.diag(diag_vals)
        
        hopping_weights = self.params[self.dim:]
        idx = 0
        for i in range(self.dim):
            for j in range(i + 1, min(i + 5, self.dim)):
                t = torch.complex(hopping_weights[idx % len(hopping_weights)], torch.tensor(0.0))
                H[i, j] += t
                H[j, i] += t
                idx += 1
                
        H = (H + H.mH) / 2.0
        q_out = torch.abs(torch.matmul(x_conv.to(torch.cfloat), H))**2
        modulation = self.fc(q_out)
        return modulation

# 2. Inicializar motor soberano
engine = SovereignQuantumMasterEngine()
engine.eval()

input_dir = "dataset_rvc_pro_integro"
output_dir = "/sdcard/Download"
os.makedirs(output_dir, exist_ok=True)

# 3. Buscar todos los archivos .wav en el directorio
search_pattern = os.path.join(input_dir, "*.wav")
wav_files = glob.glob(search_pattern)

if not wav_files:
    print(f"[Aviso] No se encontraron archivos .wav en la carpeta '{input_dir}/'")
else:
    print(f"Archivos .wav detectados para masterización: {len(wav_files)}\n")
    
    for file_path in wav_files:
        file_name = os.path.basename(file_path)
        base_name = os.path.splitext(file_name)[0]
        output_filename = os.path.join(output_dir, f"{base_name}_Sovereign_640_Master.wav")
        
        print(f"[Procesando] {file_name}...")
        try:
            sample_rate, audio_data = wav.read(file_path)
            if len(audio_data.shape) > 1:
                audio_data = audio_data[:, 0] # Convertir a mono si es estéreo
                
            num_frames = len(audio_data) // 64
            if num_frames == 0:
                print(f"  -> [Omitido] El archivo es demasiado corto.")
                continue
                
            trimmed_audio = audio_data[:num_frames * 64].astype(np.float32)
            audio_tensor = torch.tensor(trimmed_audio).reshape(-1, 64)

            with torch.no_grad():
                mastered_tensor = engine(audio_tensor)

            mastered_audio = mastered_tensor.reshape(-1).numpy()
            mastered_audio = np.clip(mastered_audio / (np.max(np.abs(mastered_audio)) + 1e-8), -1.0, 1.0)
            output_pcm = (mastered_audio * 32767).astype(np.int16)

            wav.write(output_filename, sample_rate, output_pcm)
            print(f"  -> [Éxito] Exportado a: {output_filename}")
            
        except Exception as e:
            print(f"  -> [Error] No se pudo procesar {file_name}: {e}")

print("\n==============================================================")
print(" LOTE DE MASTERIZACIÓN FINALIZADO — TODOS LOS STEMS EXPORTADOS")
print("==============================================================")
