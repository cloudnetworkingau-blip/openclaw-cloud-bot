#!/usr/bin/env python3
"""
Example script showing how to wake up a PC with IP address 192.168.0.200
using the wake-on-lan skill.

This demonstrates the two main approaches:
1. Direct MAC address (if known)
2. IP address resolution via ARP cache
"""

import subprocess
import sys
from pathlib import Path

# Add the skill scripts to path
skill_dir = Path(__file__).parent / "skills" / "wake-on-lan" / "scripts"
sys.path.insert(0, str(skill_dir))

try:
    from wake_pc import wake_by_ip, send_wol_packet
except ImportError:
    print("Error: Could not import wake_pc module")
    print("Make sure the wake-on-lan skill is installed")
    sys.exit(1)


def example_1_direct_mac():
    """Example 1: Wake using known MAC address"""
    print("Example 1: Waking with known MAC address")
    print("-" * 40)
    
    # Replace with actual MAC address of your PC
    mac_address = "AA:BB:CC:DD:EE:FF"  # Example MAC
    
    print(f"MAC Address: {mac_address}")
    print(f"Broadcast: 192.168.0.255")
    print(f"Port: 9")
    
    success = send_wol_packet(
        mac_address=mac_address,
        broadcast_ip="192.168.0.255",
        port=9
    )
    
    if success:
        print("✓ WoL packet sent successfully")
    else:
        print("✗ Failed to send WoL packet")
    
    return success


def example_2_ip_resolution():
    """Example 2: Wake using IP address (resolves MAC via ARP)"""
    print("\nExample 2: Waking with IP address 192.168.0.200")
    print("-" * 40)
    
    target_ip = "192.168.0.200"
    
    print(f"Target IP: {target_ip}")
    print("Attempting to resolve MAC address from ARP cache...")
    
    # First, let's check if the IP is in ARP cache
    try:
        result = subprocess.run(
            ['arp', '-a', target_ip],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and target_ip in result.stdout:
            print("✓ IP found in ARP cache")
            # Extract MAC from output
            import re
            mac_pattern = r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})'
            match = re.search(mac_pattern, result.stdout)
            if match:
                print(f"MAC Address: {match.group(0)}")
        else:
            print("Note: IP not in ARP cache")
            print("The machine needs to have been online recently")
            print("for ARP resolution to work.")
    
    except Exception as e:
        print(f"ARP check error: {e}")
    
    # Now try to wake using IP
    print("\nSending WoL packet...")
    success = wake_by_ip(
        ip_address=target_ip,
        broadcast_ip="192.168.0.255",
        port=9
    )
    
    return success


def example_3_command_line():
    """Example 3: Using command-line interface"""
    print("\nExample 3: Command-line usage")
    print("-" * 40)
    
    commands = [
        "# Install wakeonlan if needed",
        "sudo apt-get install wakeonlan",
        "",
        "# Method A: Using wakeonlan command with MAC",
        "wakeonlan AA:BB:CC:DD:EE:FF",
        "",
        "# Method B: Using Python script with IP",
        f"python3 {skill_dir}/wake_pc.py --ip 192.168.0.200",
        "",
        "# Method C: Using Python script with MAC",
        f"python3 {skill_dir}/wake_pc.py --mac AA:BB:CC:DD:EE:FF --broadcast 192.168.0.255",
        "",
        "# Method D: Batch processing with CSV",
        f"python3 {skill_dir}/wake_pc.py --batch machines.csv",
    ]
    
    for cmd in commands:
        print(cmd)


def example_4_troubleshooting():
    """Example 4: Troubleshooting steps"""
    print("\nExample 4: Troubleshooting checklist")
    print("-" * 40)
    
    checklist = [
        "1. Verify PC is connected to power (not on battery)",
        "2. Check WoL is enabled in BIOS/UEFI settings:",
        "   - Reboot PC and enter BIOS (usually F2, Del, F10)",
        "   - Look for 'Wake on LAN', 'Resume by LAN'",
        "   - Enable and save settings",
        "3. Check network adapter settings:",
        "   - Windows: Device Manager > Network adapter > Properties",
        "     > Power Management > 'Allow this device to wake the computer'",
        "   - Linux: Run 'sudo ethtool eth0 | grep Wake-on'",
        "4. Verify network connectivity:",
        "   - Ping the broadcast address: ping -c 1 192.168.0.255",
        "   - Check ARP cache: arp -a",
        "5. Test from different machine on same network",
        "6. Try different WoL port (7 instead of 9 or vice versa)",
    ]
    
    for item in checklist:
        print(item)


def main():
    """Main function to demonstrate all examples"""
    print("Wake-on-LAN Skill Demonstration")
    print("=" * 60)
    print("This shows how to wake up a PC at 192.168.0.200")
    print()
    
    # Example 1: Direct MAC
    example_1_direct_mac()
    
    # Example 2: IP resolution
    example_2_ip_resolution()
    
    # Example 3: Command line
    example_3_command_line()
    
    # Example 4: Troubleshooting
    example_4_troubleshooting()
    
    print("\n" + "=" * 60)
    print("Important Notes:")
    print("1. Replace AA:BB:CC:DD:EE:FF with your PC's actual MAC address")
    print("2. The PC must have WoL enabled in BIOS")
    print("3. Both devices must be on same network (192.168.0.x)")
    print("4. For IP method to work, PC must have been online recently")
    print("=" * 60)


if __name__ == "__main__":
    main()