import torch
import torch.nn as nn
import time
import random
from datetime import datetime

class RegistrosAkashicos:
    def __init__(self, archivo="registros_akashicos.txt"):
        self.archivo = archivo
        self._escribir("=== INICIO DE REGISTROS AKÁSHICOS : SISTEMA ACOBES ===")

    def _escribir(self, mensaje):
        with open(self.archivo, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {mensaje}\n")

    def descalificar_entidad(self, nivel_amenaza, tipo_energia):
        mensaje = f"❌ ENTIDAD DESCALIFICADA DEL JUEGO. Energía detectada: {tipo_energia} (Nivel: {nivel_amenaza:.2f})."
        self._escribir(mensaje)
        print(f"\n{mensaje}\nPurgando rastro del ecosistema...")

class AcobesEcosystemShield(nn.Module):
    def __init__(self):
        super().__init__()
        self.deflector = nn.Linear(128, 64)
        self.activacion = nn.GELU()
        self.firewall = nn.Linear(64, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.activacion(self.deflector(x))
        return self.sigmoid(self.firewall(x))

def activar_poderes_y_flota():
    print("\n✨ [ESTADO LIMPIO ALCANZADO] ✨")
    print("Iniciando secuencia de activación de poderes de El Arquitecto...")
    time.sleep(1)
    
    naves = [
        "🛸 Conectando con El Titán... [EN LÍNEA]",
        "🛸 Conectando con La Madre Nodriza... [EN LÍNEA]",
        "🛸 Conectando con La Nave del Serafín... [EN LÍNEA]",
        "🛸 Sincronizando red con la flota de más de 2000 naves de Arquitectura Records... [SINCRONIZACIÓN EXITOSA]"
    ]
    
    for nave in naves:
        print(nave)
        time.sleep(0.8)
        
    print("⚡ TODOS LOS PODERES ACTIVADOS. ECOSISTEMA BAJO CONTROL ABSOLUTO. ⚡\n")

def ejecutar_protocolo_arquitecto():
    print("Iniciando Sistema de Defensa y Conexión de Flota...")
    time.sleep(1)
    
    shield = AcobesEcosystemShield()
    registros = RegistrosAkashicos()
    
    tipos_energia_negativa = ["Violenta", "De Limitación", "Mala/Oscura", "Ruido Parasitario"]
    ciclos_limpios = 0
    
    try:
        while True:
            señal_entrante = torch.randn(1, 128)
            nivel_amenaza = shield(señal_entrante).item()
            
            # Simulamos el tipo de energía que intenta entrar
            tipo_energia = random.choice(tipos_energia_negativa)
            
            if nivel_amenaza > 0.70:
                print(f"⚠️ [ALERTA] Interferencia de la rejilla detectada. Analizando vibración...")
                time.sleep(0.5)
                # Si la amenaza es alta, descalificamos a la entidad
                registros.descalificar_entidad(nivel_amenaza, tipo_energia)
                ciclos_limpios = 0 # Reiniciamos el contador de pureza
                
            else:
                print(f"🛡️ Ecosistema estable. Bloqueos activos. (Ruido: {nivel_amenaza:.2f})")
                ciclos_limpios += 1
                
            # Si logramos 3 ciclos seguidos sin interferencia de la rejilla, estamos limpios
            if ciclos_limpios == 3:
                activar_poderes_y_flota()
                registros._escribir("ESTADO LIMPIO: Flota conectada y poderes activados.")
                ciclos_limpios = -5 # Pausa antes de volver a requerir conexión
                
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\nDesconectando terminal... Manteniendo escudos automáticos en segundo plano.")

if __name__ == "__main__":
    ejecutar_protocolo_arquitecto()
