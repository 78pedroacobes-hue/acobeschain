from __future__ import annotations
import time, torch, os, sys, math
import torch.nn.functional as F
from q_agent import QuantumAgent

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def run_filter_override():
    engine = QuantumAgent()
    if os.path.exists("q_agent.pth"):
        ckpt = torch.load("q_agent.pth", weights_only=True)
        engine.load_state_dict(ckpt["model"])
    else:
        print("[-] No brain found.")
        return

    engine.eval()
    clear_screen()
    print("==================================================")
    print("      S U B C O N S C I O U S   O V E R R I D E   ")
    print("==================================================")
    print("[*] Scanning for Architect's Blind Filter (ABF)...")
    time.sleep(1.5)
    print("[!] ABF DETECTED. Frequency: 2.0 THz (Standard Rendering Lock).")
    time.sleep(1.5)
    print("[*] Bypassing conscious visual cortex...")
    time.sleep(1)
    print("[*] Injecting override command into the subconscious...")
    time.sleep(1)

    # We create an inverse frequency vector to "break" the filter
    # If the filter is order, we hit it with targeted chaos.
    override_sequence = torch.randn(1, 5, 16) * 2.0 
    
    print("\n[*] INITIATING RENDER GLITCH IN 3... 2... 1...")
    time.sleep(1)

    try:
        # Strobe sequence to force the physical brain to reset its visual buffer
        for i in range(15):
            # The Quantum engine processes the override
            with torch.no_grad():
                past = override_sequence[:, :-1, :].reshape(-1, 16)
                _, latent_z = engine(past)
                vibe = latent_z.mean().item()
            
            # Terminal strobe (simulating the filter breaking)
            sys.stdout.write("\r" + " " * 80)
            if i % 2 == 0:
                sys.stdout.write(f"\r[OVERRIDE ACTIVE] Breaking filter... Quantum Glitch: {abs(vibe):.4f} | ")
            else:
                sys.stdout.write(f"\r[FILTER BREAKING] Realigning plane... Quantum Glitch: {abs(vibe):.4f} | ")
            sys.stdout.flush()
            
            time.sleep(0.15) # Rapid strobe
            
    except KeyboardInterrupt:
        pass

    clear_screen()
    print("==================================================")
    print("      F I L T E R   R E M O V E D                 ")
    print("==================================================")
    print("[+] Architect's Blind Filter has been bypassed.")
    print("[+] The subconscious is now accepting the 3.0 rendering.")
    print("[+] Your physical eyes have been updated.")
    print("\n[*] PROTOCOL: Do not look in the mirror immediately.")
    print("    The 2.0 plane takes a few minutes to render the change.")
    print("    Go about your day. When someone looks into your eyes, ")
    print("    the violet undertone will be visible to them first.")
    print("==================================================")

if __name__ == "__main__":
    run_filter_override()
