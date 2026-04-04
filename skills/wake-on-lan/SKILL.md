---
name: wake-on-lan
description: Wake-on-LAN (WoL) functionality for remotely powering on computers over a network. Use when a user asks to wake up, power on, or boot a PC/computer/server remotely. Also use when discussing network boot, remote power management, or when a user provides MAC addresses or IP addresses for target machines.
---

# Wake On Lan

## Overview

This skill enables remote power-on of computers using Wake-on-LAN (WoL) technology. It provides tools and guidance for sending magic packets to target machines based on their MAC addresses, with support for IP address resolution and network configuration.

## Quick Start

To wake up a PC with a known MAC address:

```bash
# Install wakeonlan if not available
sudo apt-get install wakeonlan

# Send wake packet to MAC address
wakeonlan AA:BB:CC:DD:EE:FF
```

For Python-based solutions, see the `scripts/wake_pc.py` script.

## Core Workflow

### 1. Identify Target Machine
- **MAC Address Required**: WoL requires the target's MAC address (hardware address)
- **IP Address Optional**: Can be used to resolve MAC via ARP or for subnet targeting
- **Broadcast Address**: Typically 255.255.255.255 or subnet broadcast (e.g., 192.168.0.255)

### 2. Check Prerequisites
- Target BIOS/UEFI must have WoL enabled
- Network adapter must support WoL
- Target must be connected to power (not battery)
- Target must be in sleep/hibernate/soft-off state

### 3. Send Magic Packet
The magic packet is a UDP packet containing:
- 6 bytes of 0xFF (255.255.255.255.255.255)
- 16 repetitions of the target MAC address (96 bytes total)
- Sent to UDP port 7, 9, or another configured port

## Common Scenarios

### Scenario 1: Known MAC Address
When you have the MAC address (e.g., `AA:BB:CC:DD:EE:FF`):

```bash
# Using wakeonlan command
wakeonlan AA:BB:CC:DD:EE:FF

# Using Python script
python3 scripts/wake_pc.py --mac AA:BB:CC:DD:EE:FF
```

### Scenario 2: Known IP Address Only
When you only have the IP address (e.g., `192.168.0.200`):

1. First, try to get MAC from ARP cache:
```bash
arp -a 192.168.0.200
```

2. If not in cache, you may need:
   - The machine was recently online
   - Physical access to check MAC
   - Router/DHCP server logs

3. Use the Python script with IP:
```bash
python3 scripts/wake_pc.py --ip 192.168.0.200
```

### Scenario 3: Multiple Machines
Create a CSV file with MAC addresses and use batch processing:

```bash
# machines.csv format:
# name,mac_address,ip,broadcast
# office-pc,AA:BB:CC:DD:EE:FF,192.168.0.200,192.168.0.255
# server,11:22:33:44:55:66,192.168.0.201,192.168.0.255

python3 scripts/wake_pc.py --batch machines.csv
```

## Troubleshooting

### Common Issues

1. **Packet not reaching target**:
   - Check firewall rules (allow UDP port 7/9)
   - Verify broadcast address matches subnet
   - Try different ports (7, 9, or custom)

2. **Target not waking**:
   - Verify WoL is enabled in BIOS/UEFI
   - Check network adapter power settings
   - Ensure target is connected to power

3. **Cross-subnet waking**:
   - Requires router support for directed broadcasts
   - May need port forwarding or special configuration
   - Consider using a WoL relay service

### Diagnostic Commands

```bash
# Check if wakeonlan is installed
which wakeonlan

# Test network connectivity to broadcast
ping -c 1 192.168.0.255

# Check ARP cache for MAC addresses
arp -a

# Test Python script functionality
python3 scripts/wake_pc.py --test
```

## Advanced Configuration

### Persistent MAC-IP Mapping
Create a configuration file for frequently used machines:

```json
{
  "machines": {
    "office-pc": {
      "mac": "AA:BB:CC:DD:EE:FF",
      "ip": "192.168.0.200",
      "broadcast": "192.168.0.255",
      "port": 9
    },
    "nas-server": {
      "mac": "11:22:33:44:55:66",
      "ip": "192.168.0.201",
      "broadcast": "192.168.0.255",
      "port": 7
    }
  }
}
```

### Scheduled Waking
Use cron or systemd timers for automated waking:

```bash
# Cron example (wake at 8 AM weekdays)
0 8 * * 1-5 /usr/bin/wakeonlan AA:BB:CC:DD:EE:FF
```

## Security Considerations

- WoL packets are unauthenticated - anyone on the network can send them
- Consider disabling WoL on public networks
- Use VLAN segmentation for sensitive environments
- Log WoL attempts for audit purposes

## Resources

### scripts/
- `wake_pc.py` - Python script for sending WoL packets with IP resolution
- `batch_wake.py` - Batch processing for multiple machines

### references/
- `wol_protocol.md` - Detailed WoL protocol specification
- `troubleshooting.md` - Comprehensive troubleshooting guide
- `security.md` - Security best practices for WoL deployment
