#!/usr/bin/env python3
"""
Get MAC addresses for IP addresses using various methods
"""

import subprocess
import re
import sys

def get_mac_from_ip(ip_address):
    """Try multiple methods to get MAC address for an IP"""
    methods = []
    
    # Method 1: Read /proc/net/arp (Linux)
    try:
        with open('/proc/net/arp', 'r') as f:
            for line in f.readlines()[1:]:  # Skip header
                parts = line.split()
                if len(parts) >= 4 and parts[0] == ip_address:
                    mac = parts[3]
                    if mac != '00:00:00:00:00:00':
                        methods.append(("ARP table (/proc/net/arp)", mac))
                        break
    except Exception as e:
        pass
    
    # Method 2: Use ip neigh command
    try:
        result = subprocess.run(
            ['ip', 'neigh', 'show', ip_address],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout:
            # Parse output: "192.168.0.200 dev ens33 lladdr aa:bb:cc:dd:ee:ff REACHABLE"
            match = re.search(r'lladdr\s+([0-9a-fA-F:]+)', result.stdout)
            if match:
                methods.append(("ip neigh command", match.group(1)))
    except Exception as e:
        pass
    
    # Method 3: Use arp command if available
    try:
        result = subprocess.run(
            ['arp', '-a', ip_address],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout:
            # Look for MAC address pattern
            mac_pattern = r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})'
            match = re.search(mac_pattern, result.stdout)
            if match:
                methods.append(("arp command", match.group(0)))
    except Exception as e:
        pass
    
    # Method 4: Ping first, then check
    try:
        # Ping to ensure entry in ARP table
        subprocess.run(
            ['ping', '-c', '1', '-W', '1', ip_address],
            capture_output=True,
            timeout=5
        )
        
        # Now try ip neigh again
        result = subprocess.run(
            ['ip', 'neigh', 'show', ip_address],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout:
            match = re.search(r'lladdr\s+([0-9a-fA-F:]+)', result.stdout)
            if match:
                methods.append(("ping + ip neigh", match.group(1)))
    except Exception as e:
        pass
    
    return methods

def get_local_network_info():
    """Get information about local network"""
    info = []
    
    try:
        # Get default gateway
        result = subprocess.run(
            ['ip', 'route', 'show', 'default'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            info.append(("Default route", result.stdout.strip()))
        
        # Get network interfaces
        result = subprocess.run(
            ['ip', 'addr', 'show'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            # Extract IP addresses
            ip_matches = re.findall(r'inet (\d+\.\d+\.\d+\.\d+/\d+)', result.stdout)
            for ip in ip_matches:
                info.append(("Local IP", ip))
    
    except Exception as e:
        info.append(("Error", str(e)))
    
    return info

def main():
    ips = ["192.168.0.200", "192.168.0.190"]
    
    print("Getting MAC addresses for IP addresses")
    print("=" * 60)
    
    # Show local network info
    print("\nLocal Network Information:")
    print("-" * 40)
    network_info = get_local_network_info()
    for method, value in network_info:
        print(f"{method}: {value}")
    
    # Try to get MAC for each IP
    for ip in ips:
        print(f"\n\nTrying to get MAC for {ip}:")
        print("-" * 40)
        
        # First, check if host is reachable
        try:
            ping_result = subprocess.run(
                ['ping', '-c', '1', '-W', '2', ip],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if ping_result.returncode == 0:
                print(f"✓ {ip} is reachable (responded to ping)")
            else:
                print(f"✗ {ip} is not reachable (no ping response)")
                print("  Note: Host must be powered on and connected to network")
                continue
        except Exception as e:
            print(f"✗ Ping failed: {e}")
            continue
        
        # Try to get MAC
        methods = get_mac_from_ip(ip)
        
        if methods:
            print(f"Found MAC address(es) for {ip}:")
            for method, mac in methods:
                print(f"  {method}: {mac}")
            
            # Use the first valid MAC
            first_mac = methods[0][1]
            print(f"\nRecommended MAC to use: {first_mac}")
            
            # Show WoL command
            print(f"\nWake-on-LAN command:")
            print(f"  python3 ~/.openclaw/workspace/skills/wake-on-lan/scripts/wake_pc.py \\")
            print(f"    --mac {first_mac} \\")
            print(f"    --broadcast 192.168.0.255")
        else:
            print(f"Could not determine MAC address for {ip}")
            print("\nAlternative methods to get MAC:")
            print("  1. On the PC itself:")
            print("     Windows: ipconfig /all")
            print("     Linux: ip link show")
            print("  2. Check router admin page → DHCP client list")
            print("  3. Look for sticker on PC/motherboard")
            print("  4. Use nmap: sudo nmap -sn 192.168.0.0/24")

if __name__ == "__main__":
    main()