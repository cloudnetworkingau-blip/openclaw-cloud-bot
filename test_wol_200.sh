#!/bin/bash
echo "Testing Wake-on-LAN for 192.168.0.200"
echo "MAC Address: e0:4f:43:e6:5b:54"
echo ""

# Check current status
echo "1. Checking if 192.168.0.200 is currently online..."
if ping -c 1 -W 2 192.168.0.200 > /dev/null 2>&1; then
    echo "   ✓ 192.168.0.200 is ONLINE (responds to ping)"
    echo ""
    echo "   Note: WoL only works when PC is asleep/hibernating."
    echo "   To test WoL:"
    echo "   - Put the PC to sleep first"
    echo "   - Then run this script again"
    echo ""
    echo "   Current WoL command (when asleep):"
    echo "   python3 ~/.openclaw/workspace/skills/wake-on-lan/scripts/wake_pc.py \\"
    echo "     --mac e0:4f:43:e6:5b:54 \\"
    echo "     --broadcast 192.168.0.255"
else
    echo "   ✗ 192.168.0.200 is OFFLINE (no ping response)"
    echo ""
    echo "   Sending Wake-on-LAN packet..."
    python3 ~/.openclaw/workspace/skills/wake-on-lan/scripts/wake_pc.py \
      --mac e0:4f:43:e6:5b:54 \
      --broadcast 192.168.0.255
    
    echo ""
    echo "   Waiting 30 seconds for PC to boot..."
    sleep 30
    
    echo "   Checking if PC woke up..."
    if ping -c 1 -W 2 192.168.0.200 > /dev/null 2>&1; then
        echo "   ✓ SUCCESS! 192.168.0.200 is now online!"
    else
        echo "   ✗ PC did not wake up. Possible issues:"
        echo "     - WoL not enabled in BIOS"
        echo "     - PC not in sleep/hibernate state"
        echo "     - Network issues"
        echo "     - Wrong MAC address"
    fi
fi

echo ""
echo "2. WoL Configuration Checklist for 192.168.0.200:"
echo "   [ ] WoL enabled in BIOS/UEFI"
echo "   [ ] Network adapter allows wake from sleep"
echo "   [ ] PC connected to power (not battery)"
echo "   [ ] Correct MAC address: e0:4f:43:e6:5b:54"
echo ""
echo "3. To enable WoL in BIOS:"
echo "   - Reboot PC → Enter BIOS (F2/Del/F10)"
echo "   - Find 'Wake on LAN', 'Resume by LAN'"
echo "   - Enable and save"
echo ""
echo "4. Windows network adapter settings:"
echo "   - Device Manager → Network adapter → Properties"
echo "   - Power Management → 'Allow this device to wake the computer'"
echo "   - Advanced → Wake on Magic Packet → Enabled"