# Wake-on-LAN Troubleshooting Guide

## Quick Diagnostic Checklist

### Before Starting
- [ ] Target machine is connected to power (not on battery)
- [ ] Target is in sleep/hibernate/soft-off state (not fully powered down)
- [ ] WoL is enabled in BIOS/UEFI settings
- [ ] Network cable is connected (for wired WoL)
- [ ] You have the correct MAC address

### Network Checks
- [ ] Sender and target are on same subnet
- [ ] No firewall blocking UDP ports 7/9
- [ ] Router supports broadcast forwarding
- [ ] Network switch isn't filtering broadcasts

## Common Problems and Solutions

### Problem: Packet sent but machine doesn't wake

**Possible causes:**
1. WoL not enabled in BIOS
2. Wrong power state
3. Network adapter settings
4. Operating system power management

**Solutions:**

1. **Check BIOS/UEFI settings:**
   - Reboot target and enter BIOS (usually F2, Del, F10)
   - Look for "Wake on LAN", "Power on by PCI-E", "Resume by LAN"
   - Enable all relevant WoL options
   - Save and exit

2. **Verify power state:**
   - WoL works from S3 (sleep), S4 (hibernate), S5 (soft-off)
   - Does NOT work from G3 (mechanical off)
   - Test by putting to sleep: `systemctl suspend` (Linux) or Start > Sleep (Windows)

3. **Check network adapter settings:**
   ```bash
   # Linux: check wake-on-lan setting
   sudo ethtool eth0 | grep Wake-on
   
   # Enable if disabled
   sudo ethtool -s eth0 wol g
   ```

4. **OS power management:**
   - Windows: Device Manager > Network adapter > Properties > Power Management > "Allow this device to wake the computer"
   - Linux: May need to disable power saving: `sudo iwconfig wlan0 power off`

### Problem: Can't determine MAC address

**Solutions:**

1. **Check when machine is online:**
   ```bash
   # On target machine
   ip link show
   ifconfig
   ipconfig /all  # Windows
   
   # On another machine on same network
   arp -a
   ```

2. **Check router/DHCP server:**
   - Login to router admin interface
   - Look for DHCP client list or connected devices
   - Find device by IP or hostname

3. **Physical inspection:**
   - Check sticker on computer or network card
   - May be on motherboard near Ethernet port

4. **Use last known IP:**
   ```bash
   # Try to ping first to populate ARP cache
   ping -c 1 192.168.0.200
   
   # Then check ARP
   arp -a 192.168.0.200
   ```

### Problem: Cross-subnet WoL not working

**Issue:** WoL packets don't cross router boundaries by default.

**Solutions:**

1. **Enable directed broadcasts on router:**
   ```bash
   # Cisco example
   interface GigabitEthernet0/0
   ip directed-broadcast
   ```

2. **Use subnet-directed broadcast:**
   - Instead of 255.255.255.255, use subnet broadcast (192.168.0.255)
   - May require router configuration

3. **Port forwarding (not recommended):**
   - Forward UDP port 7/9 from router to target IP
   - Security risk - exposes WoL to internet

4. **Use a WoL relay:**
   - Install software on a machine in target subnet
   - Forward WoL packets from external network

### Problem: Wireless WoL (WoWLAN) not working

**Additional requirements:**
- Compatible wireless adapter and drivers
- May need specific configuration
- Often less reliable than wired

**Solutions:**

1. **Check adapter support:**
   ```bash
   # Linux
   iw list | grep -A5 "Wake On"
   
   # Enable if supported
   sudo iwconfig wlan0 wol g
   ```

2. **Windows wireless adapter:**
   - Device Manager > Wireless adapter > Properties
   - Advanced tab: Look for "Wake on Magic Packet"
   - Power Management: "Allow this device to wake the computer"

### Problem: Intermittent success

**Possible causes:**
1. Network congestion
2. Switch filtering
3. Power management interference
4. Packet loss

**Solutions:**

1. **Send multiple packets:**
   ```bash
   # Send 3 packets with 1-second delay
   for i in {1..3}; do wakeonlan AA:BB:CC:DD:EE:FF; sleep 1; done
   ```

2. **Try different ports:**
   - Port 7 (echo) vs port 9 (discard)
   - Some networks filter one but not the other

3. **Increase TTL:**
   ```python
   # Python example
   sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, 2)
   ```

## Platform-Specific Issues

### Linux

**Network manager interference:**
```bash
# Disable network manager power saving
sudo nmcli radio wifi off
sudo iwconfig wlan0 power off

# Check and set WoL
sudo ethtool eth0 | grep Wake-on
sudo ethtool -s eth0 wol g
```

**Persistent WoL settings:**
Create `/etc/network/interfaces.d/wol`:
```
auto eth0
iface eth0 inet dhcp
    pre-up /usr/sbin/ethtool -s eth0 wol g
```

Or use systemd:
```bash
sudo systemctl enable wol.service
```

### Windows

**Common issues:**
1. Fast Startup interferes with WoL
2. Network adapter power saving
3. Driver issues

**Solutions:**
1. **Disable Fast Startup:**
   - Control Panel > Power Options > Choose what power buttons do
   - Uncheck "Turn on fast startup"

2. **Update network drivers:**
   - Download latest from manufacturer website
   - Older drivers may have better WoL support

3. **Power settings:**
   - Control Panel > Power Options > Change plan settings > Change advanced power settings
   - PCI Express > Link State Power Management > Off

### macOS

**Limited WoL support:**
- Primarily for Wake on Wireless LAN
- Ethernet WoL may require third-party tools

**Enable:**
```bash
# Enable for specific interface
sudo pmset -a womp 1

# Check status
pmset -g | grep womp
```

## Advanced Diagnostics

### Packet Capture
```bash
# On sender (check packet is sent)
sudo tcpdump -i eth0 -n "udp port 7 or udp port 9"

# On target if possible (check packet arrives)
sudo tcpdump -i eth0 -n "udp port 7 or udp port 9"
```

### Network Testing
```bash
# Test broadcast connectivity
ping -b -c 1 192.168.0.255

# Test specific port
nc -z -u 192.168.0.255 9

# Trace route to broadcast
traceroute 192.168.0.255
```

### Hardware Diagnostics
1. **Test with different network cable**
2. **Try different switch port**
3. **Test with different computer as sender**
4. **Check for LED activity on network port when off**

## When All Else Fails

### Alternative Approaches
1. **Smart power strip:** Remote-controlled outlet
2. **IP-enabled PDU:** Data center power distribution
3. **Intel AMT:** Out-of-band management
4. **Raspberry Pi relay:** Physical power button control

### Last Resort Checklist
- [ ] Test with another WoL tool (different implementation)
- [ ] Try from different machine on network
- [ ] Test with machine in different room/switch
- [ ] Consult motherboard/network card documentation
- [ ] Check for BIOS updates that improve WoL support

## Getting Help

### Information to Collect
1. **Sender details:**
   - OS and version
   - WoL tool/command used
   - Network configuration

2. **Target details:**
   - Make/model of computer
   - Motherboard/network card
   - BIOS version
   - OS and version

3. **Network details:**
   - Router make/model
   - Switch configuration
   - Network topology diagram

### Where to Ask
- Manufacturer support forums
- /r/techsupport on Reddit
- Server Fault or Super User
- OpenClaw community Discord