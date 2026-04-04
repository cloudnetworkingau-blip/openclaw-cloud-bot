# Wake-on-LAN Skill

A skill for OpenClaw that enables remote power-on of computers using Wake-on-LAN (WoL) technology.

## What This Skill Does

This skill allows you to:
- Wake up computers remotely using their MAC addresses
- Attempt to wake computers using only their IP addresses (via ARP resolution)
- Batch process multiple machines
- Troubleshoot WoL connectivity issues
- Implement security best practices for WoL deployments

## Installation

The skill has been packaged as `wake-on-lan.skill` in your workspace. To use it:

1. The skill file is at: `~/.openclaw/workspace/wake-on-lan.skill`
2. Skill source is at: `~/.openclaw/workspace/skills/wake-on-lan/`

## Quick Start for Your PC (192.168.0.200)

### Prerequisites
1. **Target PC must have WoL enabled in BIOS/UEFI**
   - Reboot PC and enter BIOS (usually F2, Del, F10)
   - Look for "Wake on LAN", "Resume by LAN", "Power on by PCI-E"
   - Enable and save settings

2. **Get your PC's MAC address** (one of these methods):
   - When PC is on: Open Command Prompt and type `ipconfig /all`
   - Look for "Physical Address" under your network adapter
   - Check router's DHCP client list
   - Look for sticker on PC or motherboard

### Method 1: Using MAC Address (Recommended)

If you know your PC's MAC address (e.g., `AA:BB:CC:DD:EE:FF`):

```bash
# Using the Python script
python3 ~/.openclaw/workspace/skills/wake-on-lan/scripts/wake_pc.py \
  --mac AA:BB:CC:DD:EE:FF \
  --broadcast 192.168.0.255 \
  --port 9

# Or install wakeonlan package
sudo apt-get install wakeonlan
wakeonlan AA:BB:CC:DD:EE:FF
```

### Method 2: Using IP Address Only

If you only have the IP address (192.168.0.200):

```bash
python3 ~/.openclaw/workspace/skills/wake-on-lan/scripts/wake_pc.py \
  --ip 192.168.0.200 \
  --broadcast 192.168.0.255
```

**Note:** This method requires the PC to have been online recently so its MAC is in the ARP cache.

## How to Use with OpenClaw

Once the skill is loaded, OpenClaw will automatically use it when you ask about:
- Waking up computers
- Remote power management
- Wake-on-LAN functionality
- Network boot operations

### Example Conversations

**You:** "Wake up my PC at 192.168.0.200"
**OpenClaw:** (Uses the skill to send WoL packet)

**You:** "How do I enable Wake-on-LAN?"
**OpenClaw:** (Provides guidance from the skill's troubleshooting guide)

**You:** "Wake all the office computers"
**OpenClaw:** (Uses batch processing if you have a machine list)

## Skill Contents

### Scripts
- `wake_pc.py` - Main WoL script with IP/MAC support
- `batch_wake.py` - Advanced batch processing with JSON/YAML/CSV

### Reference Documentation
- `api_reference.md` - Detailed WoL protocol specification
- `troubleshooting.md` - Comprehensive troubleshooting guide  
- `security.md` - Security best practices and deployment guidelines

## Testing the Skill

Run the test to verify functionality:
```bash
cd ~/.openclaw/workspace/skills/wake-on-lan
python3 scripts/wake_pc.py --test
```

## Common Issues & Solutions

### PC Doesn't Wake Up
1. **Check BIOS:** WoL must be enabled in BIOS/UEFI
2. **Power state:** PC must be in sleep/hibernate/soft-off (not fully unplugged)
3. **Network:** Both devices must be on same subnet (192.168.0.x)
4. **Adapter settings:** Some network adapters need specific power settings

### Can't Find MAC Address
1. **When PC is on:** Use `ipconfig /all` (Windows) or `ip link show` (Linux)
2. **Check router:** Login to router admin and check DHCP client list
3. **Physical check:** Look for sticker on PC/motherboard/network card

### Cross-Subnet Issues
WoL typically doesn't cross routers. Solutions:
- Use subnet-directed broadcast (192.168.0.255)
- Configure router to forward directed broadcasts
- Use a WoL relay on the target subnet

## Security Considerations

⚠️ **Important:** WoL packets are unauthenticated!
- Anyone on your network can send them
- Consider disabling on public networks
- Use VLAN segmentation for sensitive environments
- Log WoL attempts for audit purposes

## Next Steps

1. **Test with your actual MAC address** (replace AA:BB:CC:DD:EE:FF)
2. **Verify BIOS settings** on target PC
3. **Test from another machine** on your network
4. **Create machine list** for batch operations if needed

## Support

If you encounter issues:
1. Check the troubleshooting guide in the skill
2. Verify network connectivity between devices
3. Ensure WoL is properly configured in BIOS
4. Test with different WoL tools to isolate the issue

The skill includes comprehensive documentation covering protocol details, platform-specific instructions, and security guidelines.