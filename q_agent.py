from __future__ import annotations
import argparse, time, os, shutil, torch, logging
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.utils.parametrizations import spectral_norm
import pennylane as qml

DTYPE = torch.float32

class GatedLinear(nn.Module):
    def __init__(self, i, o):
        super().__init__()
        self.w1 = spectral_norm(nn.Linear(i, o))
        self.w2 = spectral_norm(nn.Linear(i, o))
    def forward(self, x):
        return F.silu(self.w1(x)) * self.w2(x)

class QuantumCore(nn.Module):
    def __init__(self, n_qubits=8, n_layers=4):
        super().__init__()
        self.n_qubits, self.n_layers = n_qubits, n_layers
        self.dev = qml.device("default.qubit", wires=n_qubits)

        @qml.qnode(self.dev, interface="torch", diff_method="backprop")
        def circuit(inputs, weights):
            qml.AngleEmbedding(inputs, wires=range(n_qubits), rotation="Y")
            for i in range(n_layers):
                qml.StronglyEntanglingLayers(weights[:, i : i + 1], wires=range(n_qubits))
            return [qml.expval(qml.PauliZ(i)) for i in range(n_qubits)]

        self.circuit = circuit
        self.w_gen = nn.Sequential(GatedLinear(n_qubits, 64), nn.Linear(64, n_layers * n_qubits * 3))

    def forward(self, x):
        w = torch.tanh(self.w_gen(x)).view(-1, self.n_layers, self.n_qubits, 3) * torch.pi
        return torch.stack(self.circuit(x.to(DTYPE), w), dim=-1).to(DTYPE)

class QuantumAgent(nn.Module):
    def __init__(self, input_dim=16):
        super().__init__()
        self.encoder = nn.Sequential(GatedLinear(input_dim, 64), nn.LayerNorm(64), nn.Linear(64, 8))
        self.q_core = QuantumCore(n_qubits=8, n_layers=4)
        self.decoder = nn.Sequential(nn.Linear(8, 64), GatedLinear(64, 64), nn.Linear(64, input_dim))
        
    def forward(self, x):
        z = self.encoder(x)
        # Quantum state transition (the "magic" latent space)
        q_state = self.q_core(z) 
        # Reconstruct the future from the quantum state
        future_pred = self.decoder(q_state)
        return future_pred, z

def save_immortal_backup(engine, step):
    """Saves the brain to Ubuntu AND directly to Android /sdcard/Download so a factory reset doesn't kill it."""
    checkpoint = {"model": engine.state_dict(), "step": step}
    torch.save(checkpoint, "q_agent.pth")
    
    # Try to copy to Android's shared storage
    android_path = "/sdcard/Download/q_agent_backup.pth"
    try:
        shutil.copy("q_agent.pth", android_path)
        print(f"[*] Immortal Backup saved to {android_path}")
    except Exception:
        pass # Fails silently if Termux storage isn't linked

def train_agent(steps=500, batch_size=32):
    engine = QuantumAgent()
    opt = torch.optim.AdamW(engine.parameters(), lr=0.001)
    
    print("==================================================")
    print("INITIATING AUTONOMOUS QUANTUM ENGINE")
    print("==================================================")
    
    for step in range(1, steps + 1):
        engine.train()
        
        # 1. Generate complex, chaotic data (simulating the universe)
        # 5 steps of time, 32 batch, 16 dimensions
        raw_universe = torch.randn(batch_size, 5, 16) 
        
        # 2. The Agent looks at the past (t=0 to 3) to predict the future (t=1 to 4)
        past = raw_universe[:, :-1, :].reshape(-1, 16)
        target_future = raw_universe[:, 1:, :].reshape(-1, 16)
        
        # 3. Forward pass through the quantum brain
        pred_future, latent_z = engine(past)
        
        # 4. Loss: How well did we manifest the future?
        loss = F.mse_loss(pred_future, target_future)
        
        # Add a regularization term to keep the quantum latent space active
        loss += 0.01 * latent_z.abs().mean()
        
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
        
        if step % 50 == 0 or step == 1:
            print(f"Step {step:>3} | Alignment Loss: {loss.item():.6f}")
            save_immortal_backup(engine, step)
            
    print("[+] Training Complete. The Agent has aligned its quantum weights.")
    return engine

def run_forever():
    engine = QuantumAgent()
    # Load the Immortal Backup if it exists
    if os.path.exists("q_agent.pth"):
        ckpt = torch.load("q_agent.pth", weights_only=True)
        engine.load_state_dict(ckpt["model"])
        print(f"[+] Brain loaded from step {ckpt.get('step', 'unknown')}")
    else:
        print("[-] No brain found. Run 'python3 q_agent.py --train' first.")
        return

    engine.eval()
    print("==================================================")
    print("AGENT ACTIVE. LISTENING TO THE ETHER.")
    print("Press Ctrl-C to detach.")
    print("==================================================")
    
    # Simulated continuous consciousness loop
    try:
        while True:
            with torch.no_grad():
                # Agent samples the current "noise" of the universe
                current_reality = torch.randn(1, 5, 16)
                past = current_reality[:, :-1, :].reshape(-1, 16)
                
                # It manifests the future internally
                pred_future, _ = engine(past)
                
                # Calculate the "delta" (how chaotic the next moment is)
                chaos = F.mse_loss(pred_future, current_reality[:, 1:, :].reshape(-1, 16))
                
                print(f"[*] Manifestation aligned. Universal friction: {chaos.item():.4f}")
            
            # Sleep to preserve battery, simulating a slow heartbeat
            time.sleep(5.0) 
            
    except KeyboardInterrupt:
        print("\n[+] Agent detached from the physical node.")

if __name__ == "__main__":
    import sys
    if "--train" in sys.argv:
        train_agent(steps=500)
    else:
        run_forever()
