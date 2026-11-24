import time
import sys
import random
import threading
from datetime import datetime

class EscudoCuanticoExtremo:
    def __init__(self, radio_millas=5):
        self.radio = radio_millas
        self.activo = True
        self.integridad = 100.0
        self.neutralizados = 0
        self.impactos_aniquilados = 0
        self.frecuencia_hz = 963.0  # Frecuencia máxima de desintegración de vectores hostiles
        self.potencia_mw = 5000.0   # Megavatios de energía pura en el perímetro
        self.historial_eventos = []
        self.lock = threading.Lock()

    def nucleo_torretas_plasma(self):
        """Hilo de alta frecuencia para barrer y aniquilar cualquier intento de acercamiento."""
        while self.activo:
            time.sleep(0.4)
            with self.lock:
                # Estabilidad reforzada al 300%
                self.integridad = 100.0
                
                # Sube la intensidad: simulación constante de oleadas que intentan pasar pero muerden el polvo
                oleada = random.randint(3, 12)
                self.neutralizados += oleada
                
                if random.random() < 0.65:
                    self.impactos_aniquilados += 1
                    timestamp = datetime.now().strftime("%H:%M:%S.f")[:12]
                    angulo = random.randint(0, 360)
                    evento = f"[{timestamp}] 💥 ANIQUILACIÓN TOTAL: Intruso a {random.uniform(0.1, 4.9):.2f} millas ({angulo}°) desintegrado por pulso de plasma."
                    self.historial_eventos.append(evento)
                    if len(self.historial_eventos) > 6:
                        self.historial_eventos.pop(0)

    def iniciar(self):
        print("\n" + "🔥"*40)
        print(" ⚛️ [GUI-55 MÁXIMA POTENCIA] - TORRETAS DE PLASMA Y ESCUDO CUÁNTICO INVIOLABLE")
        print("🔥"*40)
        print(f"   [+] Cobertura Perimetral : {self.radio} Millas (Zona de Exclusión Total)")
        print(f"   [+] Potencia Activa      : {self.potencia_mw} MW (Nivel: 'Para que respeten')")
        print(f"   [+] Frecuencia de Barrido: {self.frecuencia_hz} Hz")
        print(f"   [+] Estado del Sistema   : Calibrado y sediento de justicia")
        print("="*80 + "\n")
        time.sleep(1.5)

        # Lanzar hilo de defensa agresiva
        hilo_defensa = threading.Thread(target=self.nucleo_torretas_plasma, daemon=True)
        hilo_defensa.start()

        print("⚡ [PERÍMETRO EN LLAMAS] Nadie cruza la línea. Las torretas están barriendo el horizonte.")
        print("🔒 (Presiona CTRL + C para desactivar el protocolo de castigo)\n")

        try:
            ciclo = 0
            while self.activo:
                ciclo += 1
                with self.lock:
                    integ_str = f"{self.integridad:.2f}%"
                    neut_str = f"{self.neutralizados}"
                    dest_str = f"{self.impactos_aniquilados}"

                sys.stdout.write(
                    f"\r[ESTADO DE GUERRA] Radio: {self.radio}mi | "
                    f"Blindaje: 🛡️ {integ_str} | "
                    f"Neutralizados: 🎯 {neut_str} | "
                    f"Aniquilados por Plasma: ⚡ {dest_str} | "
                    f"Ciclo: {ciclo:06d} 🔥"
                )
                sys.stdout.flush()
                time.sleep(0.2)

        except KeyboardInterrupt:
            self.activo = False
            self.generar_reporte_escaramuza()

    def generar_reporte_escaramuza(self):
        print("\n\n" + "="*80)
        print(" 🏆 [REPORTE DE VICTORIA] - ESCUDO GUI-55 (MÁXIMA POTENCIA)")
        print("="*80)
        print(f"   🔹 Radio Defendido         : {self.radio} Millas")
        print(f"   🔹 Integridad del Escudo   : {self.integridad:.2f}% (¡Impenetrable!)")
        print(f"   🔹 Total Intrusos Repelidos : {self.neutralizados}")
        print(f"   🔹 Impactos Aniquilados    : {self.impactos_aniquilados}")
        print("\n 📜 Últimas acciones de las torretas de plasma:")
        for ev in self.historial_eventos:
            print(f"      {ev}")
        print("="*80)
        print(" 🎯 [SISTEMA]: Perímetro despejado. Aprendieron la lección.\n")

if __name__ == "__main__":
    escudo = EscudoCuanticoExtremo(radio_millas=5)
    escudo.iniciar()
