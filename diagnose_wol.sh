#!/bin/bash
echo "Wake-on-LAN Diagnostic for 192.168.0.190"
echo "MAC Address: E0-4F-43-E6-50-D6"
echo "=" * 60

echo "1. Testing network connectivity..."
echo "   Our IP: $(hostname -I 2>/dev/null || echo 'Unknown')"
echo "   Gateway: $(ip route show default 2>/dev/null | awk '{print $3}' || echo 'Unknown')"
echo "   Broadcast address: 192.168.0.255"

echo ""
echo "2. Testing if 192.168.0.190 is reachable..."
if ping -c 1 -W 2 192.168.0.190 > /dev/null 2>&1; then
    echo "   ✓ PC is ONLINE (already powered on)"
    echo "   Note: WoL only works when PC is asleep/hibernating"
else
    echo "   ✗ PC is OFFLINE (good for WoL test)"
fi

echo ""
echo "3. Sending test WoL packets..."
echo "   Sending to port 9..."
python3 ~/.openclaw/workspace/skills/wake-on-lan/scripts/wake_pc.py \
  --mac E0-4F-43-E6-50-D6 \
  --broadcast 192.168.0.255 \
  --port 9

echo ""
echo "   Sending to port 7 (alternative)..."
python3 ~/.openclaw/workspace/skills/wake-on-lan/scripts/wake_pc.py \
  --mac E0-4F-43-E6-50-D6 \
  --broadcast 192.168.0.255 \
  --port 7

echo ""
echo "4. Common reasons WoL doesn't work:"
echo "   [ ] WoL not enabled in BIOS/UEFI"
echo "   [ ] PC not in sleep/hibernate state (S3/S4)"
echo "   [ ] Network adapter doesn't support WoL"
echo "   [ ] Wrong power state (must be soft-off S5, not mechanical off)"
echo "   [ ] PC not connected to power"
echo "   [ ] Network cable disconnected"
echo "   [ ] Firewall blocking UDP ports 7/9"

echo ""
echo "5. To enable WoL on 192.168.0.190:"
echo "   a. Power on the PC"
echo "   b. Enter BIOS (usually F2, Del, or F10 during boot)"
echo "   c. Look for:"
echo "      - 'Wake on LAN'"
echo "      - 'Resume by LAN'"
echo "      - 'Power on by PCI-E'"
echo "      - 'PME Event Wake Up'"
echo "   d. Enable and save"
echo ""
echo "   e. Windows settings (if applicable):"
echo "      - Device Manager → Network adapter → Properties"
echo "      - Power Management → 'Allow this device to wake the computer'"
echo "      - Advanced → 'Wake on Magic Packet' → Enabled"

echo ""
echo "6. Testing procedure:"
echo "   a. Power on 192.168.0.190"
echo "   b. Enable WoL in BIOS"
echo "   c. Put PC to sleep (Start → Sleep)"
echo "   d. Wait 1 minute"
echo "   e. Run wake command:"
echo "      python3 ~/.openclaw/workspace/skills/wake-on-lan/scripts/wake_pc.py \\"
echo "        --mac E0-4F-43-E6-50-D6 \\"
echo "        --broadcast 192.168.0.255"
echo "   f. PC should wake within 30 seconds"

echo ""
echo "7. Quick test commands:"
echo "   # Send WoL packet"
echo "   python3 ~/.openclaw/workspace/skills/wake-on-lan/scripts/wake_pc.py \\"
echo "     --mac E0-4F-43-E6-50-D6 \\"
echo "     --broadcast 192.168.0.255"
echo ""
echo "   # Check status"
echo "   ping -c 1 192.168.0.190"
echo ""
echo "   # Send multiple packets (in case of packet loss)"
echo "   for i in {1..5}; do"
echo "     python3 ~/.openclaw/workspace/skills/wake-on-lan/scripts/wake_pc.py \\"
echo "       --mac E0-4F-43-E6-50-D6 \\"
echo "       --broadcast 192.168.0.255"
echo "     sleep 2"
echo "   done"