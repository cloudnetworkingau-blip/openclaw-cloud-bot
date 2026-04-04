#!/usr/bin/env python3
"""
Manage both PCs: 192.168.0.200 and 192.168.0.190
"""

import subprocess
import time
import sys
from pathlib import Path

# Add skill scripts to path
skill_dir = Path(__file__).parent / "skills" / "wake-on-lan" / "scripts"
sys.path.insert(0, str(skill_dir))

try:
    from wake_pc import send_wol_packet, wake_by_ip
except ImportError:
    print("Error: Could not import wake_pc module")
    sys.exit(1)

# PC configurations
PCS = {
    "pc-200": {
        "name": "PC 200",
        "ip": "192.168.0.200",
        "mac": "e0:4f:43:e6:5b:54",
        "broadcast": "192.168.0.255",
        "port": 9
    },
    "pc-190": {
        "name": "PC 190", 
        "ip": "192.168.0.190",
        "mac": "e0:4f:43:e6:50:d6",
        "broadcast": "192.168.0.255",
        "port": 9
    }
}

def check_status(ip):
    """Check if PC is online"""
    try:
        result = subprocess.run(
            ['ping', '-c', '1', '-W', '2', ip],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False

def wake_pc(pc_config, method="mac"):
    """Wake a PC using specified method"""
    name = pc_config["name"]
    ip = pc_config["ip"]
    mac = pc_config["mac"]
    broadcast = pc_config["broadcast"]
    port = pc_config["port"]
    
    print(f"\nWaking {name} ({ip})...")
    
    if method == "mac":
        print(f"  Using MAC: {mac}")
        success = send_wol_packet(mac, broadcast, port)
    elif method == "ip":
        print(f"  Using IP: {ip}")
        success = wake_by_ip(ip, broadcast, port)
    else:
        print(f"  Unknown method: {method}")
        return False
    
    if success:
        print(f"  ✓ WoL packet sent successfully")
    else:
        print(f"  ✗ Failed to send WoL packet")
    
    return success

def monitor_wake(pc_config, timeout=60):
    """Monitor if PC wakes up after WoL packet"""
    name = pc_config["name"]
    ip = pc_config["ip"]
    
    print(f"\nMonitoring {name} for wake-up...")
    print(f"  Will check for {timeout} seconds")
    
    for i in range(timeout // 5):
        time.sleep(5)
        if check_status(ip):
            print(f"  ✓ {name} is now ONLINE! (after {i*5 + 5} seconds)")
            return True
        print(f"  ... still waiting ({i*5 + 5}/{timeout} seconds)")
    
    print(f"  ✗ {name} did not wake up within {timeout} seconds")
    return False

def create_config_file():
    """Create configuration file for both PCs"""
    config_content = """# PC Configuration for Wake-on-LAN
# Save as: ~/.openclaw/workspace/pc_config.json

{
  "pcs": {
    "pc-200": {
      "name": "PC 200",
      "ip": "192.168.0.200",
      "mac": "e0:4f:43:e6:5b:54",
      "broadcast": "192.168.0.255",
      "port": 9,
      "description": "First PC"
    },
    "pc-190": {
      "name": "PC 190",
      "ip": "192.168.0.190",
      "mac": "e0:4f:43:e6:50:d6",
      "broadcast": "192.168.0.255",
      "port": 9,
      "description": "Second PC"
    }
  }
}
"""
    
    config_path = Path.home() / ".openclaw" / "workspace" / "pc_config.json"
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    print(f"Configuration file created: {config_path}")
    return config_path

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Manage PCs 192.168.0.200 and 192.168.0.190",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check status of both PCs
  %(prog)s --status
  
  # Wake both PCs
  %(prog)s --wake-all
  
  # Wake specific PC
  %(prog)s --wake pc-200
  %(prog)s --wake pc-190
  
  # Wake and monitor
  %(prog)s --wake pc-190 --monitor
  
  # Create configuration file
  %(prog)s --create-config
        """
    )
    
    parser.add_argument(
        '--status',
        action='store_true',
        help="Check status of all PCs"
    )
    
    parser.add_argument(
        '--wake',
        choices=['pc-200', 'pc-190', 'all'],
        help="Wake specific PC or all PCs"
    )
    
    parser.add_argument(
        '--wake-all',
        action='store_true',
        help="Wake all PCs"
    )
    
    parser.add_argument(
        '--monitor',
        action='store_true',
        help="Monitor after waking (wait for boot)"
    )
    
    parser.add_argument(
        '--create-config',
        action='store_true',
        help="Create configuration file"
    )
    
    parser.add_argument(
        '--method',
        choices=['mac', 'ip'],
        default='mac',
        help="Wake method (mac or ip, default: mac)"
    )
    
    args = parser.parse_args()
    
    if args.create_config:
        create_config_file()
        return
    
    if args.status or not any([args.wake, args.wake_all]):
        print("Current Status of PCs:")
        print("=" * 60)
        for pc_id, config in PCS.items():
            status = "ONLINE" if check_status(config["ip"]) else "OFFLINE"
            print(f"{config['name']} ({config['ip']}): {status}")
            print(f"  MAC: {config['mac']}")
            print()
    
    if args.wake_all or args.wake == 'all':
        for pc_id, config in PCS.items():
            wake_pc(config, args.method)
            if args.monitor:
                monitor_wake(config)
    
    elif args.wake:
        pc_id = args.wake
        if pc_id in PCS:
            wake_pc(PCS[pc_id], args.method)
            if args.monitor:
                monitor_wake(PCS[pc_id])
        else:
            print(f"Unknown PC: {pc_id}")
    
    if not any([args.status, args.wake, args.wake_all, args.create_config]):
        print("\nQuick commands:")
        print("  Check status: python3 manage_pcs.py --status")
        print("  Wake PC 200:  python3 manage_pcs.py --wake pc-200")
        print("  Wake PC 190:  python3 manage_pcs.py --wake pc-190")
        print("  Wake all:     python3 manage_pcs.py --wake-all")
        print("  Create config: python3 manage_pcs.py --create-config")

if __name__ == "__main__":
    main()