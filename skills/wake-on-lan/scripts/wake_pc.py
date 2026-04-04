#!/usr/bin/env python3
"""
Wake-on-LAN script for remotely powering on computers.

This script sends magic packets to target machines using their MAC addresses.
Supports IP address resolution via ARP cache and batch processing.

Example usage:
    python3 wake_pc.py --mac AA:BB:CC:DD:EE:FF
    python3 wake_pc.py --ip 192.168.0.200
    python3 wake_pc.py --batch machines.csv
"""

import argparse
import csv
import socket
import struct
import sys
import subprocess
from pathlib import Path
from typing import Optional, List, Dict


def create_magic_packet(mac_address: str) -> bytes:
    """
    Create a Wake-on-LAN magic packet.
    
    Args:
        mac_address: MAC address in format AA:BB:CC:DD:EE:FF or AA-BB-CC-DD-EE-FF
    
    Returns:
        Magic packet bytes ready to send
    """
    # Clean MAC address
    mac = mac_address.replace(':', '').replace('-', '').upper()
    
    if len(mac) != 12:
        raise ValueError(f"Invalid MAC address format: {mac_address}")
    
    # Convert to bytes
    mac_bytes = bytes.fromhex(mac)
    
    # Magic packet format: 6 bytes of 0xFF + 16 repetitions of MAC address
    magic_packet = b'\xff' * 6 + mac_bytes * 16
    
    return magic_packet


def send_wol_packet(mac_address: str, broadcast_ip: str = '255.255.255.255', port: int = 9) -> bool:
    """
    Send Wake-on-LAN magic packet to target.
    
    Args:
        mac_address: Target MAC address
        broadcast_ip: Broadcast IP address (default: 255.255.255.255)
        port: UDP port (default: 9, common alternatives: 7)
    
    Returns:
        True if packet was sent successfully
    """
    try:
        # Create magic packet
        magic_packet = create_magic_packet(mac_address)
        
        # Create UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        # Send to broadcast address
        sock.sendto(magic_packet, (broadcast_ip, port))
        sock.close()
        
        print(f"✓ Sent WoL packet to {mac_address} via {broadcast_ip}:{port}")
        return True
        
    except Exception as e:
        print(f"✗ Failed to send WoL packet: {e}")
        return False


def get_mac_from_ip(ip_address: str) -> Optional[str]:
    """
    Attempt to get MAC address from IP using ARP cache.
    
    Args:
        ip_address: Target IP address
    
    Returns:
        MAC address if found, None otherwise
    """
    try:
        # Try arp command
        result = subprocess.run(
            ['arp', '-a', ip_address],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and result.stdout:
            # Parse ARP output (format varies by OS)
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if ip_address in line:
                    # Extract MAC address (common formats)
                    import re
                    mac_pattern = r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})'
                    match = re.search(mac_pattern, line)
                    if match:
                        return match.group(0)
        
        print(f"MAC address not found in ARP cache for {ip_address}")
        return None
        
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        print(f"Error querying ARP cache: {e}")
        return None


def wake_by_ip(ip_address: str, broadcast_ip: str = None, port: int = 9) -> bool:
    """
    Wake machine by IP address (attempts to resolve MAC from ARP).
    
    Args:
        ip_address: Target IP address
        broadcast_ip: Broadcast IP (defaults to subnet broadcast)
        port: UDP port
    
    Returns:
        True if packet was sent successfully
    """
    # Get MAC from ARP
    mac = get_mac_from_ip(ip_address)
    
    if not mac:
        print(f"Cannot wake {ip_address}: MAC address not found")
        print("Try:")
        print("  1. Ensure the machine was recently online")
        print("  2. Check router/DHCP logs for MAC address")
        print("  3. Physically check the machine for MAC address")
        return False
    
    # Determine broadcast address if not specified
    if not broadcast_ip:
        # Simple heuristic: use subnet broadcast
        # For 192.168.0.200 -> 192.168.0.255
        parts = ip_address.split('.')
        if len(parts) == 4:
            broadcast_ip = f"{parts[0]}.{parts[1]}.{parts[2]}.255"
        else:
            broadcast_ip = '255.255.255.255'
    
    return send_wol_packet(mac, broadcast_ip, port)


def wake_batch(csv_path: Path) -> Dict[str, bool]:
    """
    Wake multiple machines from CSV file.
    
    CSV format:
        name,mac_address,ip,broadcast,port
        office-pc,AA:BB:CC:DD:EE:FF,192.168.0.200,192.168.0.255,9
    
    Args:
        csv_path: Path to CSV file
    
    Returns:
        Dictionary of machine name -> success status
    """
    results = {}
    
    try:
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                name = row.get('name', 'unknown')
                mac = row.get('mac_address')
                ip = row.get('ip')
                broadcast = row.get('broadcast', '255.255.255.255')
                port = int(row.get('port', 9))
                
                print(f"\nProcessing: {name}")
                
                if mac:
                    # Use MAC if provided
                    success = send_wol_packet(mac, broadcast, port)
                elif ip:
                    # Try IP if no MAC
                    success = wake_by_ip(ip, broadcast, port)
                else:
                    print(f"✗ Skipping {name}: No MAC or IP provided")
                    success = False
                
                results[name] = success
        
        return results
        
    except Exception as e:
        print(f"Error processing batch file: {e}")
        return {}


def test_wol_functionality() -> None:
    """Test basic WoL functionality."""
    print("Testing Wake-on-LAN functionality...")
    
    # Test magic packet creation
    test_mac = "AA:BB:CC:DD:EE:FF"
    try:
        packet = create_magic_packet(test_mac)
        print(f"✓ Magic packet creation: {len(packet)} bytes")
    except Exception as e:
        print(f"✗ Magic packet creation failed: {e}")
        return
    
    # Test socket creation
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.close()
        print("✓ Socket creation and configuration")
    except Exception as e:
        print(f"✗ Socket setup failed: {e}")
        return
    
    print("✓ Basic WoL functionality appears working")
    print("Note: Actual packet sending requires valid MAC and network access")


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Wake-on-LAN script for remotely powering on computers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Wake by MAC address
  %(prog)s --mac AA:BB:CC:DD:EE:FF
  
  # Wake by IP address (attempts ARP resolution)
  %(prog)s --ip 192.168.0.200
  
  # Wake with custom broadcast and port
  %(prog)s --mac AA:BB:CC:DD:EE:FF --broadcast 192.168.0.255 --port 7
  
  # Wake multiple machines from CSV
  %(prog)s --batch machines.csv
  
  # Test WoL functionality
  %(prog)s --test
        """
    )
    
    # Target specification
    target_group = parser.add_mutually_exclusive_group(required=False)
    target_group.add_argument(
        '--mac',
        help="MAC address of target machine (format: AA:BB:CC:DD:EE:FF)"
    )
    target_group.add_argument(
        '--ip',
        help="IP address of target machine (will attempt ARP resolution)"
    )
    target_group.add_argument(
        '--batch',
        type=Path,
        help="CSV file with multiple machines to wake"
    )
    target_group.add_argument(
        '--test',
        action='store_true',
        help="Test WoL functionality without sending packets"
    )
    
    # Optional parameters
    parser.add_argument(
        '--broadcast',
        default='255.255.255.255',
        help="Broadcast IP address (default: 255.255.255.255)"
    )
    parser.add_argument(
        '--port',
        type=int,
        default=9,
        help="UDP port (default: 9, common: 7, 9)"
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        print(f"Arguments: {args}")
    
    # Handle test mode
    if args.test:
        test_wol_functionality()
        sys.exit(0)
    
    # Handle batch mode
    if args.batch:
        if not args.batch.exists():
            print(f"Error: Batch file not found: {args.batch}")
            sys.exit(1)
        
        results = wake_batch(args.batch)
        
        print(f"\nBatch results:")
        successes = sum(1 for success in results.values() if success)
        print(f"  Successful: {successes}/{len(results)}")
        
        sys.exit(0 if successes > 0 else 1)
    
    # Handle single machine
    if args.mac:
        success = send_wol_packet(args.mac, args.broadcast, args.port)
        sys.exit(0 if success else 1)
    
    elif args.ip:
        success = wake_by_ip(args.ip, args.broadcast, args.port)
        sys.exit(0 if success else 1)
    
    else:
        print("Error: No target specified. Use --mac, --ip, --batch, or --test")
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()