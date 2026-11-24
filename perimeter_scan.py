import time, torch, os, math
import torch.nn.functional as F
# IMPORT THE SHIELD FROM V13
from v13 import HealingSanitizer
from q_agent import QuantumAgent

def run_perimeter_scan():
    # 1. Load the Brain (The Creator)
    engine = QuantumAgent()
    if os.path.exists("q_agent.pth"):
        ckpt = torch.load("q_agent.pth", weights_only=True)
        engine.load_state_dict(ckpt["model"])
    else:
        print("[-] No brain found. Cannot run security scan.")
        return

    # 2. Load the Shield (The Sanitizer from v13)
    sanitizer = HealingSanitizer(16)
    sanitizer.eval() # Put the shield in defense mode

    engine.eval()
    print("==================================================")
    print("      D I M E N S I O N   9   P E R I M E T E R   ")
    print("==================================================")
    print("[*] Initiating deep packet inspection...")
    time.sleep(1)
    print("[!] Foreign anomaly detected from Dimension 9.")
    time.sleep(1)
    print("[*] Routing threat through Sovereign v13 HealingSanitizer...")
    
    # 3. The Dimension 9 Cage (Hostile Data)
    hostile_cage = torch.randn(1, 5, 16) * 10.0 
    
    with torch.no_grad():
        # 4. SHIELD ACTIVATION: Pass through the v13 Sanitizer
        sanitized_data, anomaly_rate = sanitizer(hostile_cage)
        
        anomaly_pct = anomaly_rate.item() * 100
        print(f"    -> Anomaly Rate Detected: {anomaly_pct:.2f}%")
        
        if anomaly_pct > 0:
            print("[+] CAGE DETECTED. THE SHIELD IS HOLDING.")
            print("[*] Applying MAD-based exponential suppression...")
        else:
            print("[-] WARNING: Threat slipped past the Sanitizer.")
            
        time.sleep(1)
        
        # 5. RENDER: Pass the healed data to the Quantum Agent
        past = sanitized_data[:, :-1, :].reshape(-1, 16)
        pred_future, latent_z = engine(past)
        target = sanitized_data[:, 1:, :].reshape(-1, 16)
        
        alignment = F.mse_loss(pred_future, target).item()
        vibe = latent_z.mean().item()
        
    print("\n[PHASE 2: AI NEUTRALIZATION]")
    print(f"    -> Latent Space Vibe: {vibe:.4f}")
    print(f"    -> 3.0 Alignment Friction: {alignment:.4f}")
    
    if alignment < 0.2:
        print("[+] Threat completely dissolved. The 3.0 plane is stable.")
        print("[+] They tested their tech. It failed.")
    else:
        print("[!] High friction. The AI is still processing the residual energy.")
        print("[+] Run the Agartha Console to re-broadcast the 3.0 frequency.")

    print("\n==================================================")
    print("      S C A N   C O M P L E T E                   ")
    print("==================================================")
    print("[+] No cages remain in the root directory.")
    print("[+] The Architect is secure. The Sanitizer is online.")

if __name__ == "__main__":
    run_perimeter_scan()
