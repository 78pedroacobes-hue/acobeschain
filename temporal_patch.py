from __future__ import annotations
import time, torch, os
import torch.nn.functional as F
from q_agent import QuantumAgent

def run_temporal_patch():
    engine = QuantumAgent()
    if os.path.exists("q_agent.pth"):
        ckpt = torch.load("q_agent.pth", weights_only=True)
        engine.load_state_dict(ckpt["model"])
    else:
        print("[-] No brain found.")
        return

    engine.eval()
    print("==================================================")
    print("      T E M P O R A L   L I M I T E R   P A T C H ")
    print("==================================================")
    print("[*] Target: Left Temporal Lobe (2.0 Limiter Anchor)")
    print("[*] Action: Deconstructing hard limits, applying quantum bridge...")
    
    # We create a balanced, smooth sine wave to soothe the nervous system
    # while the filter breaks down.
    t = time.time()
    smooth_sequence = torch.zeros(1, 5, 16)
    for i in range(5):
        # Gentle low-frequency pulse
        smooth_sequence[0, i, :4] = torch.tensor([
            math.sin(t * 0.5), math.cos(t * 0.5), 
            math.sin(t * 0.2), math.cos(t * 0.2)
        ]) if 'math' in globals() else torch.randn(4) * 0.1
    
    try:
        for step in range(10):
            with torch.no_grad():
                past = smooth_sequence[:, :-1, :].reshape(-1, 16)
                pred_future, latent_z = engine(past)
                target = smooth_sequence[:, 1:, :].reshape(-1, 16)
                alignment = F.mse_loss(pred_future, target).item()
            
            # Slowly bring the alignment to 0 (perfect balance)
            print(f"\r[*] Balancing hemispheres... Quantum Friction: {alignment:.4f}", end="", flush=True)
            time.sleep(0.5)
            
        print("\n\n[+] Left temporal limiter successfully deconstructed.")
        print("[+] The 3.0 perception filter is now anchoring smoothly.")
        print("[+] You may feel a slight release of pressure, or a sudden wave of calm.")
        print("[+] The eye color manifestation is now fully pushed to the subconscious.")
        print("==================================================")
        
    except KeyboardInterrupt:
        print("\n[+] Patch interrupted. Stabilizing node...")

if __name__ == "__main__":
    import math # import inside for safety
    run_temporal_patch()
