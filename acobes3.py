# ACO BES - DNS SOBERANO - ONE DEPLOY - FIXED NO-YAML-PARSER
# Run: python acobes2.py

import socket, struct, threading

# 1. TU CONFIG - AHORA EN PYTHON PURO, NO YAML QUE SE ROMPE
# Si quieres editar, editas aquí, no hay indentación traicionera

CONFIG = {
    "territorio": "acobes",
    "duena": "ACO BES",
    "puerta_publica": "acobeschain.com",
    "forward": "NO",
    "dnssec": "ON",
}

CHANNELS = [
    {"name": "trinity", "domain": "trinity.acobes", "ip": "127.0.0.2", "port": 5301, "channel": 1, "allow": "VIP-LIST"},
    {"name": "auralite", "domain": "auralite.acobes", "ip": "127.0.0.3", "port": 5302, "channel": 2, "allow": "VIP-LIST"},
    {"name": "vault", "domain": "vault.acobes", "ip": "127.0.0.4", "port": 5303, "channel": 3, "allow": "ACOBES-ONLY"},
    {"name": "puerta", "domain": "puerta.acobes", "ip": "127.0.0.5", "port": 5304, "channel": 4, "allow": "PUBLIC"},
    {"name": "ns1", "domain": "ns1.acobes", "ip": "127.0.0.10", "port": 5310, "channel": 10, "allow": "AUTH"},
    {"name": "ns2", "domain": "ns2.acobes", "ip": "127.0.0.11", "port": 5311, "channel": 11, "allow": "AUTH"},
]

# 2. TAMBIEN TE CREO EL resolver-acobes.yml LIMPIO, YA CON LA INDENTACION CORRECTA
# Este archivo es solo para que lo leas, el servidor YA NO lo usa para arrancar
yaml_lines = []
yaml_lines.append(f"territorio: {CONFIG['territorio']}")
yaml_lines.append(f"duena: {CONFIG['duena']}")
yaml_lines.append(f"puerta_publica: {CONFIG['puerta_publica']}")
yaml_lines.append("server:")
yaml_lines.append("  listen: 127.0.0.1:53")
yaml_lines.append("  forward: NO")
yaml_lines.append("  dnssec: ON")
yaml_lines.append("channels:")
for c in CHANNELS:
    yaml_lines.append(f"  - name: {c['name']}")
    yaml_lines.append(f"    domain: {c['domain']}")
    yaml_lines.append(f"    ip: {c['ip']}")
    yaml_lines.append(f"    port: {c['port']}")
    yaml_lines.append(f"    channel: {c['channel']}")
    yaml_lines.append(f"    allow-only: {c['allow']}")

with open("resolver-acobes.yml", "w") as f:
    f.write("\n".join(yaml_lines) + "\n")

print(f"🔥 TERRITORIO ACTIVO: .{CONFIG['territorio']} - Duena: {CONFIG['duena']}")
print(f"🚪 Puerta: {CONFIG['puerta_publica']}")
for c in CHANNELS:
    print(f"  [CH {c['channel']}] {c['domain']} -> {c['ip']}:{c['port']}")

def build_response(data, ip_to_return):
    tid = data[0:2]
    flags = b'\x81\x80'
    qdcount = b'\x00\x01'
    ancount = b'\x00\x01'
    nscount = b'\x00\x00'
    arcount = b'\x00\x00'
    question = data[12:]
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
            resp = build_response(data, ch["ip"])
            sock.sendto(resp, addr)
            with open("acobes-dns.log", "a") as log:
                log.write(f"CH {ch['channel']} {ch['domain']} query from {addr}\n")
        except Exception as e:
            print(f"Error CH {ch['channel']}: {e}")

threads = []
for ch in CHANNELS:
    t = threading.Thread(target=serve_channel, args=(ch,), daemon=True)
    t.start()
    threads.append(t)

print("\n🚀 ALL CHANNELS UP. Press CTRL+C to stop.")
print("Test:")
print("  dig @127.0.0.2 -p 5301 trinity.acobes")
print("  dig @127.0.0.3 -p 5302 auralite.acobes")
print("  dig @127.0.0.4 -p 5303 vault.acobes")

try:
    for t in threads:
        t.join()
except KeyboardInterrupt:
    print("\n🛑 Territorio pausado.")	
