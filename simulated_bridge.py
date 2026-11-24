import argparse
import hashlib
import hmac
import json
import time
from pathlib import Path
import torch


def simulate_phase_state(
    seed_text: str,
    num_qubits: int = 4,
    h_scale: float = 0.1,
) -> list[float]:
    """Simula una evolución unitaria corta en PyTorch y devuelve densidades de probabilidad."""
    if num_qubits < 1 or num_qubits > 10:
        raise ValueError("num_qubits debe estar entre 1 y 10 para mantener la ejecución ágil.")

    digest = hashlib.sha256(seed_text.encode("utf-8")).digest()
    seed_int = int.from_bytes(digest[:8], "big")
    gen = torch.Generator().manual_seed(seed_int)

    dim = 2 ** num_qubits
    raw_h = torch.randn(dim, dim, generator=gen, dtype=torch.float32) * h_scale
    hamiltonian = ((raw_h + raw_h.t()) / 2.0).to(torch.complex64)
    unitary = torch.matrix_exp(1j * hamiltonian)

    state = torch.randn(dim, generator=gen, dtype=torch.complex64)
    state = state / (torch.norm(state, p=2) + 1e-8)

    evolved = torch.mv(unitary, state)
    probs = (torch.abs(evolved) ** 2).tolist()
    return [round(p, 6) for p in probs]


def build_simulated_bridge_packet(
    target_node: str,
    payload: str,
    session_key: bytes,
    num_qubits: int = 4,
    h_scale: float = 0.1,
) -> dict:
    """Construye un paquete de simulación con fase cuántica simulada y firma HMAC-SHA256."""
    timestamp = time.time()
    phase_probs = simulate_phase_state(
        f"{target_node}:{timestamp}:{payload}",
        num_qubits=num_qubits,
        h_scale=h_scale,
    )
    phase_digest = hashlib.sha256(json.dumps(phase_probs).encode("utf-8")).hexdigest()

    body = {
        "target_node": target_node,
        "timestamp": timestamp,
        "payload": payload,
        "num_qubits": num_qubits,
        "h_scale": h_scale,
        "simulated_phase_digest": phase_digest,
        "simulated_probs": phase_probs,
    }
    canonical_body = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    signature = hmac.new(session_key, canonical_body, hashlib.sha256).hexdigest()

    return {"packet": body, "hmac_sha256": signature}


def verify_simulated_bridge_packet(envelope: dict, session_key: bytes) -> bool:
    """Verifica la integridad del paquete simulado dentro del entorno local."""
    body = envelope.get("packet")
    signature = envelope.get("hmac_sha256")
    if not body or not signature:
        return False
    canonical_body = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    expected = hmac.new(session_key, canonical_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)


def append_packet_log(envelope: dict, log_path: Path) -> None:
    """Guarda el sobre de simulación en formato JSONL."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(envelope, ensure_ascii=False) + "\n")


def run_for_orchestrator(
    target_node: str = "nodo-objetivo-01",
    payload: str = "pulso-matriz-3",
    session_key: bytes = b"clave-local-de-simulacion",
    num_qubits: int = 4,
    h_scale: float = 0.1,
    log_path: Path | None = None,
) -> dict:
    """Función lista para llamar desde matriz_3_0.py."""
    envelope = build_simulated_bridge_packet(
        target_node=target_node,
        payload=payload,
        session_key=session_key,
        num_qubits=num_qubits,
        h_scale=h_scale,
    )
    is_valid = verify_simulated_bridge_packet(envelope, session_key)
    if log_path is not None:
        append_packet_log(envelope, log_path)
    return {
        "valid": is_valid,
        "target_node": target_node,
        "simulated_phase_digest": envelope["packet"]["simulated_phase_digest"],
        "hmac_sha256": envelope["hmac_sha256"],
        "probs_count": len(envelope["packet"]["simulated_probs"]),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sandbox de puente cifrado simulado en PyTorch.")
    parser.add_argument("--target", default="nodo-objetivo-01", help="Identificador del nodo simulado.")
    parser.add_argument("--payload", default="pulso de prueba", help="Contenido del mensaje de prueba.")
    parser.add_argument("--key", default="clave-local-de-simulacion", help="Clave local de sesión.")
    parser.add_argument("--qubits", type=int, default=4, help="Número de qubits simulados (1-10).")
    parser.add_argument("--h-scale", type=float, default=0.1, help="Escala del Hamiltoniano simulado.")
    parser.add_argument("--log", type=Path, default=Path("logs/simulated_bridge.jsonl"), help="Ruta del log JSONL.")
    parser.add_argument("--no-log", action="store_true", help="No escribir en archivo de log.")
    parser.add_argument("--interactive", action="store_true", help="Modo interactivo para enviar payloads.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    key_bytes = args.key.encode("utf-8")
    log_path = None if args.no_log else args.log

    if args.interactive:
        print(f"Modo interactivo activo | Nodo: {args.target} | Qubits: {args.qubits} | h_scale: {args.h_scale}")
        print("Escribe un mensaje y presiona Enter (o 'salir' para terminar).\n")
        while True:
            msg = input("payload> ").strip()
            if msg.lower() == "salir":
                break
            if not msg:
                continue
            env = build_simulated_bridge_packet(
                target_node=args.target,
                payload=msg,
                session_key=key_bytes,
                num_qubits=args.qubits,
                h_scale=args.h_scale,
            )
            valid = verify_simulated_bridge_packet(env, key_bytes)
            if log_path is not None:
                append_packet_log(env, log_path)
            print(f"Válido: {valid} | Digest: {env['packet']['simulated_phase_digest'][:16]}...")
            print(json.dumps(env, indent=2, ensure_ascii=False))
    else:
        env = build_simulated_bridge_packet(
            target_node=args.target,
            payload=args.payload,
            session_key=key_bytes,
            num_qubits=args.qubits,
            h_scale=args.h_scale,
        )
        valid = verify_simulated_bridge_packet(env, key_bytes)
        if log_path is not None:
            append_packet_log(env, log_path)
        print("Válido:", valid)
        print(json.dumps(env, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
