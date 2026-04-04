#!/usr/bin/env python3
"""
Test script to attempt waking 192.168.0.190
"""

import socket
import sys
from pathlib import Path

# Add skill scripts to path
skill_dir = Path(__file__).parent / "skills" / "wake-on-lan" / "scripts"
sys.path.insert(0, str(skill_dir))

try:
    from wake_pc import create_magic_packet, send_wol_packet
except ImportError:
    print("Error: Could not import wake_pc module")
    sys.exit(1)

def test_network():
    """Test basic network connectivity"""
    print("Testing network connectivity to 192.168.0.255...")
    try:
        # Try to create a socket to test network
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(2)
        
        # Test binding (won't actually send without MAC)
        sock.bind(('', 0))
        print("✓ Network socket creation successful")
        sock.close()
        return True
    except Exception as e:
        print(f"✗ Network error: {e}")
        return False

def send_test_packets():
    """Send WoL packets with common broadcast addresses"""
    print("\nAttempting to send WoL packets...")
    
    # Common MAC address patterns to try (replace with actual if known)
    # These are just examples - you need the REAL MAC address
    test_macs = [
        # Add your actual MAC addresses here when you know them
        # "AA:BB:CC:DD:EE:FF",  # Example - replace with real MAC
        # "00:11:22:33:44:55",  # Example - replace with real MAC
    ]
    
    broadcast_addresses = [
        "192.168.0.255",    # Subnet-directed broadcast
        "255.255.255.255",  # Limited broadcast
    ]
    
    ports = [7, 9]  # Common WoL ports
    
    if not test_macs:
        print("No MAC addresses to test.")
        print("\nYou need to add the actual MAC address to this script.")
        print("Get the MAC address by:")
        print("  1. Powering on the PC and running 'ipconfig /all' (Windows)")
        print("  2. Checking router DHCP client list")
        print("  3. Looking for sticker on PC/motherboard")
        return False
    
    for mac in test_macs:
        print(f"\nTesting MAC: {mac}")
        for broadcast in broadcast_addresses:
            for port in ports:
                print(f"  Trying {broadcast}:{port}...")
                success = send_wol_packet(mac, broadcast, port)
                if success:
                    print(f"  ✓ Packet sent successfully!")
    
    return True

def main():
    print("Wake-on-LAN Test for 192.168.0.190")
    print("=" * 50)
    
    # Test network
    if not test_network():
        print("\nNetwork test failed. Check:")
        print("  1. Are you on the same network as 192.168.0.190?")
        print("  2. Is the network interface up?")
        print("  3. Any firewall blocking UDP broadcasts?")
        return
    
    # Try to send packets
    send_test_packets()
    
    print("\n" + "=" * 50)
    print("Next Steps:")
    print("1. Get the MAC address of 192.168.0.190")
    print("2. Enable WoL in BIOS/UEFI on that PC")
    print("3. Add the MAC to the test_macs list in this script")
    print("4. Run this script again")
    print("\nQuick MAC finding commands:")
    print("  Windows (on the PC): ipconfig /all")
    print("  Linux (on the PC): ip link show")
    print("  Router: Check DHCP client list")
    print("=" * 50)

if __name__ == "__main__":
    main()