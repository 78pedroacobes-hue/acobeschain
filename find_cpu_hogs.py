import os

def get_processes():
    processes = []
    # Iterate through the /proc directory (where Linux stores process info)
    for pid in os.listdir('/proc'):
        if pid.isdigit():
            try:
                # Read the command name
                with open(f'/proc/{pid}/comm', 'r') as f:
                    name = f.read().strip()
                
                # Read the CPU usage (in clock ticks)
                with open(f'/proc/{pid}/stat', 'r') as f:
                    stat = f.read().split()
                    utime = int(stat[13])
                    stime = int(stat[14])
                    total_time = utime + stime
                
                # Read memory usage
                with open(f'/proc/{pid}/status', 'r') as f:
                    status = f.read().split('\n')
                    vmrss = 0
                    for line in status:
                        if line.startswith('VmRSS:'):
                            vmrss = int(line.split()[1]) # in kB
                            break
                
                processes.append({
                    'pid': pid,
                    'name': name,
                    'cpu_time': total_time,
                    'mem_kb': vmrss
                })
            except (FileNotFoundError, ProcessLookupError):
                # Process died while we were reading it
                pass
                
    # Sort by CPU time (descending)
    processes.sort(key=lambda x: x['cpu_time'], reverse=True)
    return processes

if __name__ == "__main__":
    print(f"{'PID':<8} | {'NAME':<20} | {'CPU TICKS':<12} | {'MEMORY (MB)'}")
    print("-" * 55)
    
    procs = get_processes()
    # Show the top 15 heaviest processes
    for p in procs[:15]:
        mem_mb = p['mem_kb'] / 1024
        print(f"{p['pid']:<8} | {p['name']:<20} | {p['cpu_time']:<12} | {mem_mb:.2f} MB")
        
    print("\n[*] If you see 'python' or 'python3' at the top with a massive CPU TICK count,")
    print("    that is your rogue script. Kill it using: kill -9 <PID>")
