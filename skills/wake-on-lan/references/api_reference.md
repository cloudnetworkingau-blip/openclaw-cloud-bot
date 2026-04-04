# Wake-on-LAN Protocol Reference

## Protocol Overview

Wake-on-LAN (WoL) is an Ethernet computer networking standard that allows a computer to be turned on or awakened by a network message.

### Magic Packet Format

The magic packet is a broadcast frame containing anywhere within its payload 6 bytes of all 255 (FF FF FF FF FF FF in hexadecimal), followed by sixteen repetitions of the target computer's 48-bit MAC address, for a total of 102 bytes.

**Packet Structure:**
```
[6 bytes of 0xFF] + [16 repetitions of MAC address] = 102 bytes total
```

**Example for MAC AA:BB:CC:DD:EE:FF:**
```
FFFFFFFFFFFF AABBCCDDEEFF AABBCCDDEEFF AABBCCDDEEFF AABBCCDDEEFF
AABBCCDDEEFF AABBCCDDEEFF AABBCCDDEEFF AABBCCDDEEFF AABBCCDDEEFF
AABBCCDDEEFF AABBCCDDEEFF AABBCCDDEEFF AABBCCDDEEFF AABBCCDDEEFF
AABBCCDDEEFF
```

### Network Transport

- **Protocol:** UDP (User Datagram Protocol)
- **Ports:** Typically 7 (echo) or 9 (discard), but any port can be used
- **Destination:** Broadcast address (255.255.255.255) or subnet-directed broadcast
- **TTL:** Usually 1 (stays within local network) but can be increased for routed WoL

## MAC Address Formats

Wake-on-LAN accepts MAC addresses in several formats:

| Format | Example | Notes |
|--------|---------|-------|
| Colon-separated | `AA:BB:CC:DD:EE:FF` | Most common |
| Hyphen-separated | `AA-BB-CC-DD-EE-FF` | Common on Windows |
| Period-separated | `AABB.CCDD.EEFF` | Cisco format |
| No separators | `AABBCCDDEEFF` | Raw hexadecimal |

## Broadcast Addresses

### Common Broadcast Addresses

| Network | Broadcast Address | Notes |
|---------|------------------|-------|
| Default | `255.255.255.255` | Limited broadcast (stays within subnet) |
| Class A | `x.255.255.255` | For 10.0.0.0/8 networks |
| Class B | `x.x.255.255` | For 172.16.0.0/12 networks |
| Class C | `x.x.x.255` | For 192.168.0.0/16 networks |

### Subnet Calculation

For IP address `192.168.0.200` with netmask `255.255.255.0`:
- Network: `192.168.0.0`
- Broadcast: `192.168.0.255`

## Port Configuration

### Standard Ports

| Port | Service | Notes |
|------|---------|-------|
| 7 | Echo | Original WoL port, may be filtered |
| 9 | Discard | Most common, often unfiltered |
| 0 | Reserved | Sometimes used |
| Any | Custom | Can be configured in BIOS |

### Firewall Considerations

- WoL packets are typically allowed through firewalls
- Some routers may filter broadcast traffic
- Enterprise networks often restrict WoL for security

## Platform-Specific Implementation

### Linux
```bash
# Using wakeonlan package
sudo apt-get install wakeonlan
wakeonlan AA:BB:CC:DD:EE:FF

# Using etherwake
sudo apt-get install etherwake
sudo etherwake AA:BB:CC:DD:EE:FF

# Raw socket implementation
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
```

### Windows
```powershell
# PowerShell implementation
$mac = "AA-BB-CC-DD-EE-FF"
$macByteArray = $mac.Split("-") | ForEach-Object { [Byte] "0x$_" }
$packet = [Byte[]] (,0xFF * 6) + ($macByteArray * 16)
$udpClient = New-Object System.Net.Sockets.UdpClient
$udpClient.Connect([System.Net.IPAddress]::Broadcast, 9)
$udpClient.Send($packet, $packet.Length)
$udpClient.Close()
```

### macOS
```bash
# Using wakeonlan (brew install wakeonlan)
brew install wakeonlan
wakeonlan AA:BB:CC:DD:EE:FF

# Using Python
python3 -c "import socket; s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1); s.sendto(b'\\xff'*6 + bytes.fromhex('AABBCCDDEEFF')*16, ('255.255.255.255', 9))"
```

## Advanced Features

### SecureON (WoL with password)
Some implementations support password-protected WoL:
- 4-byte or 6-byte password appended to magic packet
- Must match password configured in BIOS
- Not widely supported

### Wake on Wireless LAN (WoWLAN)
- Extension for wireless networks
- Requires compatible hardware and drivers
- Different packet format (uses specific management frames)

### BIOS/UEFI Settings

Common BIOS settings that affect WoL:
- **Wake on LAN**: Enable/Disable
- **Wake on PCI/PCIe**: Enable for network cards
- **Deep Sleep**: May disable WoL
- **ERP Ready**: May affect power states
- **Boot from Network**: Related but separate feature

## Troubleshooting Reference

### Common Error Codes

| Error | Cause | Solution |
|-------|-------|----------|
| No response | Target offline | Check power connection |
| Packet sent, no wake | WoL disabled in BIOS | Enable in BIOS settings |
| Can't resolve MAC | Machine never on network | Check ARP cache when online |
| Permission denied | Raw socket requires root | Use sudo or appropriate permissions |
| Network unreachable | Wrong broadcast address | Verify subnet mask |

### Diagnostic Commands

```bash
# Check network interface
ip link show
ifconfig

# Check ARP cache
arp -a
ip neigh show

# Test network connectivity
ping -c 1 192.168.0.255
ping -b -c 1 192.168.0.255

# Check firewall rules
sudo iptables -L
sudo ufw status

# Monitor network traffic
sudo tcpdump -i eth0 port 7 or port 9
```

## Security Considerations

### Risks
1. **Unauthorized access**: Anyone on network can send WoL packets
2. **Denial of Service**: Can be used to wake machines excessively
3. **Power consumption**: Waking machines increases energy usage
4. **Information disclosure**: MAC addresses exposed in packets

### Mitigations
1. **Network segmentation**: Isolate WoL to specific VLANs
2. **Authentication**: Use SecureON if supported
3. **Logging**: Monitor WoL attempts
4. **Time restrictions**: Only allow WoL during business hours
5. **IP filtering**: Restrict which hosts can send WoL packets

## RFC References

- **RFC 826**: Address Resolution Protocol (ARP)
- **RFC 1122**: Requirements for Internet Hosts
- **RFC 1812**: Requirements for IP Version 4 Routers
- **AMD Magic Packet Specification**: Original WoL specification

## Related Technologies

- **Intel AMT**: Active Management Technology
- **IPMI**: Intelligent Platform Management Interface
- **ACPI**: Advanced Configuration and Power Interface
- **PXE**: Preboot Execution Environment
