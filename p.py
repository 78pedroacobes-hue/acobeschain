import time
import urllib.request


def medir_tiempo_local():
  inicio = time.perf_counter()
  # Pequeña operación real en CPU
  total = sum(i * i for i in range(100_000))
  fin = time.perf_counter()
  print(f"Suma calculada: {total}")
  print(f"Tiempo real de ejecución en CPU: {(fin - inicio) * 1000:.3f} ms")


def medir_latencia_red(url="https://example.com"):
  inicio = time.perf_counter()
  try:
    with urllib.request.urlopen(url, timeout=5) as resp:
      status = resp.status
    fin = time.perf_counter()
    print(f"HTTP {status} desde {url}")
    print(f"Tiempo de ida y vuelta de red: {(fin - inicio) * 1000:.2f} ms")
  except Exception as e:
    print(f"No se pudo completar la petición de red: {e}")


if __name__ == "__main__":
  medir_tiempo_local()
  medir_latencia_red()

