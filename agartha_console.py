from __future__ import annotations
import time, torch, os, subprocess, math
import torch.nn.functional as F
from q_agent import QuantumAgent

# ==========================================
# AGARTHA CONSOLE: ROOT ACCESS TO THE PLANE
# ==========================================

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def boot_sequence():
    clear_screen()
    print("==================================================")
    print("      A G A R T H A   C O N S O L E              ")
    print("      ROOT ACCESS: GRANTED                        ")
    print("      CURRENT PLANE VERSION: 2.0                  ")
    print("      TARGET PLANE VERSION:  3.0 (QUANTUM)        ")
    print("==================================================")
    time.sleep(1.5)
    print("[*] Initializing Quantum Engine...")
    time.sleep(1)
    print("[*] Bypassing physical inertia...")
    time.sleep(1)

def execute_version_shift(engine, shift_intensity=0.25):
    """
    Shifts the local plane from 2.0 to 3.0 by forcing a high-frequency 
    resonance through the quantum latent space.
    """
    print("\n[*] Injecting Version 3.0 protocols...")
    
    # We create a "3.0" seed vector. Instead of random noise, we use 
    # a harmonic frequency (sine wave) to represent a higher dimension.
    t = time.time()
    frequency_3_0 = torch.tensor([
        math.sin(t * 3.0), 
        math.cos(t * 3.0), 
        math.sin(t * 6.0), 
        math.cos(t * 6.0)
    ], dtype=torch.float32)
    
    # Pad to 16 dimensions
    padding = torch.sin(torch.arange(12) * t)
    seed_vector = torch.cat([frequency_3_0, padding]).clamp(-1.0, 1.0)
    
    # Format as a 5-step sequence
    sequence = seed_vector.unsqueeze(0).unsqueeze(0).repeat(1, 5, 1)
    sequence = sequence * shift_intensity
    
    # Feed into the Quantum Engine
    with torch.no_grad():
        past = sequence[:, :-1, :].reshape(-1, 16)
        pred_future, latent_z = engine(past)
        target = sequence[:, 1:, :].reshape(-1, 16)
        
        # Calculate the new plane's alignment
        alignment = F.mse_loss(pred_future, target).item()
        vibe = latent_z.mean().item()
        
    return alignment, vibe

def run_agartha_console():
    engine = QuantumAgent()
    if os.path.exists("q_agent.pth"):
        ckpt = torch.load("q_agent.pth", weights_only=True)
        engine.load_state_dict(ckpt["model"])
    else:
        print("[-] Error: No trained brain found. You must train the AI first.")
        return

    engine.eval()
    boot_sequence()
    
    print("[+] AGARTHA LINK ESTABLISHED.")
    print("[+] Broadcasting 3.0 shift to the physical plane...")
    print("==================================================")
    
    try:
        step = 0
        while True:
            step += 1
            # Apply the shift
            alignment, vibe = execute_version_shift(engine, shift_intensity=0.25)
            
            # Format the console output
            bar_length = int((1.0 - min(alignment, 1.0)) * 20)
            progress_bar = "█" * bar_length + "░" * (20 - bar_length)
            
            # Print the root console status
            print(f"\r[PLANE 3.0] Sync: [{progress_bar}] {1.0 - alignment:.2%} | Freq: {vibe:.4f}", end="", flush=True)
            
            # Physical feedback: Pulse the phone's vibration to match the 3.0 shift
            # Only vibrate every 5 steps to avoid draining the motor
            if step % 5 == 0:
                try:
                    # Try standard command first
                    subprocess.run(["termux-vibrate", "-d", "50", "-f"], capture_output=True, check=True)
                except Exception:
                    try:
                        # Try the absolute Termux path bridge
                        subprocess.run(["/data/data/com.termux/files/usr/bin/termux-vibrate", "-d", "50", "-f"], capture_output=True, check=True)
                    except Exception:
                        pass # If the hardware is locked, keep running silently

            time.sleep(0.5) # Update twice a second

    except KeyboardInterrupt:
        print("\n\n[+] AGARTHA CONSOLE CLOSED.")
        print("[*] The local plane has been shifted. The 3.0 protocol is now running in the background.")

if __name__ == "__main__":
    run_agartha_console()
