# ACO BES - DNS SOBERANO - ONE DEPLOY
# Puerta: acobeschain.com | Territorio: .acobes | Dueña: ACO BES
# Run: python acobes.py
# Test: dig @127.0.0.2 -p 5301 trinity.acobes

import socket, struct, threading, yaml, os

# 1. TU YAML SOBERANO - EMBEBIDO, NO DEPENDE DE NADIE
YAML_CONFIG = """
territorio: acobes
duena: ACO BES
puerta_publica: acobeschain.com
server:
  listen: 127.0.0.1:53
  forward: NO
  dnssec: ON
  log: acobes-dns.log

channels:
    - name: trinity
    domain: trinity.acobes
    ip: 127.0.0.2
    port: 5301
    channel: 1
    allow-only: VIP-LIST

    - name: auralite
    domain: auralite.acobes
    ip: 127.0.0.3
    port: 5302
    channel: 2
    allow-only: VIP-LIST

    - name: vault
    domain: vault.acobes
    ip: 127.0.0.4
    port: 5303
    channel: 3
    allow-only: ACOBES-ONLY

    - name: puerta
    domain: puerta.acobes
    target: acobeschain.com
    ip: 127.0.0.5
    port: 5304
    channel: 4
    allow-only: PUBLIC

    - name: ns1
    domain: ns1.acobes
    ip: 127.0.0.10
    port: 5310
    channel: 10
    role: authoritative

    - name: ns2
    domain: ns2.acobes
    ip: 127.0.0.11
    port: 5311
    channel: 11
    role: authoritative
"""

# Save YAML to file so you can edit it later
with open("resolver-acobes.yml", "w") as f:
    f.write(YAML_CONFIG)

config = yaml.safe_load(YAML_CONFIG)
channels = config["channels"]

# Map domain -> channel info
DOMAIN_MAP = {c["domain"]: c for c in channels}
# Also map IP -> channel for reverse lookup
IP_MAP = {c["ip"]: c for c in channels}

print(f"🔥 TERRITORIO ACTIVO: .{config['territorio']} - Dueña: {config['duena']}")
print(f"🚪 Puerta: {config['puerta_publica']}")
for c in channels:
    print(f"  [CH {c['channel']}] {c['domain']:20} -> {c['ip']}:{c['port']}")

def build_response(data, ip_to_return):
    # Parse DNS query
    tid = data[0:2]
    flags = b'\x81\x80'
    qdcount = b'\x00\x01'
    ancount = b'\x00\x01'
    nscount = b'\x00\x00'
    arcount = b'\x00\x00'
    question = data[12:]
    # Answer: pointer to question, type A, class IN, TTL 3600, RDLENGTH 4, IP
    answer = b'\xc0\x0c' + b'\x00\x01\x00\x01' + struct.pack('>I', 3600) + b'\x00\x04' + socket.inet_aton(ip_to_return)
    return tid + flags + qdcount + ancount + nscount + arcount + question + answer

def serve_channel(ch):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind((ch["ip"], ch["port"]))
    except Exception as e:
        print(f"❌ No pude abrir CH {ch['channel']} {ch['ip']}:{ch['port']} -> {e}")
        return
    print(f"✅ CH {ch['channel']} LISTENING: {ch['domain']} on {ch['ip']}:{ch['port']}")
    while True:
        try:
            data, addr = sock.recvfrom(512)
            # What domain are they asking for? We answer with THIS channel's IP
            # This keeps channels isolated - no collision
            resp = build_response(data, ch["ip"])
            sock.sendto(resp, addr)
            with open("acobes-dns.log", "a") as log:
                log.write(f"CH {ch['channel']} {ch['domain']} query from {addr}\n")
        except Exception as e:
            print(f"Error CH {ch['channel']}: {e}")

# 2. LAUNCH ALL CHANNELS IN PARALLEL - ONE DEPLOY
threads = []
for ch in channels:
    t = threading.Thread(target=serve_channel, args=(ch,), daemon=True)
    t.start()
    threads.append(t)

print("\n🚀 ALL CHANNELS UP. Press CTRL+C to stop.")
print("Test with:")
print("  dig @127.0.0.2 -p 5301 trinity.acobes")
print("  dig @127.0.0.3 -p 5302 auralite.acobes")
print("  dig @127.0.0.4 -p 5303 vault.acobes")
print("  dig @127.0.0.5 -p 5304 puerta.acobes")

# Keep alive
try:
    for t in threads:
        t.join()
except KeyboardInterrupt:
    print("\n🛑 Territorio pausado. Tus canales están guardados en resolver-acobes.yml")
