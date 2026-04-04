# Wake-on-LAN Security Guide

## Security Risks Overview

Wake-on-LAN presents several security considerations that must be addressed in any deployment:

### Primary Risks
1. **Unauthorized Access**: Anyone on the network can wake machines
2. **Denial of Service**: Excessive waking can disrupt operations
3. **Power Consumption**: Unauthorized waking increases energy costs
4. **Information Disclosure**: MAC addresses exposed in packets
5. **Network Reconnaissance**: WoL traffic can map network topology

## Threat Model

### Attack Vectors
| Vector | Risk Level | Impact |
|--------|------------|---------|
| Internal network | High | Full network access |
| Wireless network | Medium | Limited to wireless range |
| Internet-facing | Critical | Global accessibility |
| Physical access | Critical | Direct network connection |

### Potential Attackers
1. **Internal users** (disgruntled employees, contractors)
2. **Network intruders** (compromised devices)
3. **External attackers** (if WoL exposed to internet)
4. **Accidental triggers** (misconfigured automation)

## Security Best Practices

### 1. Network Segmentation

**Isolate WoL traffic to specific VLANs:**
```bash
# Example VLAN configuration
vlan 100
 name wol-isolated
!
interface GigabitEthernet0/1
 switchport mode access
 switchport access vlan 100
```

**Benefits:**
- Limits WoL to authorized segments
- Prevents broadcast storms
- Simplifies monitoring

### 2. Access Control

**Implement MAC address filtering:**
```python
# Example: Whitelist approved MAC addresses
ALLOWED_MACS = {
    'AA:BB:CC:DD:EE:FF': 'office-pc',
    '11:22:33:44:55:66': 'nas-server'
}

def is_allowed(mac):
    return mac in ALLOWED_MACS
```

**Network-level controls:**
- Router ACLs to restrict WoL sources
- Firewall rules limiting UDP 7/9
- 802.1X authentication for network access

### 3. Authentication

**Use SecureON when available:**
- 4-byte or 6-byte password in magic packet
- Must match BIOS configuration
- Not all hardware supports this

**Alternative authentication:**
```python
# Custom authentication wrapper
def send_authenticated_wol(mac, password):
    # Hash password with MAC as salt
    auth_token = hash_password(password, mac)
    magic_packet = create_magic_packet(mac) + auth_token
    send_packet(magic_packet)
```

### 4. Logging and Monitoring

**Comprehensive logging:**
```python
import logging
from datetime import datetime

def log_wol_attempt(source_ip, target_mac, success):
    logger.info(f"{datetime.now()} - WoL from {source_ip} to {target_mac} - {'SUCCESS' if success else 'FAILED'}")
```

**Monitor for anomalies:**
- Unusual WoL patterns (off-hours, frequent attempts)
- Unknown source IP addresses
- Failed authentication attempts
- Multiple rapid wake attempts

### 5. Time Restrictions

**Implement time-based controls:**
```python
from datetime import datetime, time

BUSINESS_HOURS = (time(8, 0), time(18, 0))
WEEKDAYS = range(0, 5)  # Monday-Friday

def is_business_hours():
    now = datetime.now()
    return (now.weekday() in WEEKDAYS and 
            BUSINESS_HOURS[0] <= now.time() <= BUSINESS_HOURS[1])
```

## Deployment Scenarios

### Home Network (Low Security)

**Recommended configuration:**
- Use subnet-directed broadcasts (192.168.1.255)
- Enable on trusted devices only
- Consider disabling when not needed
- Basic logging enabled

**Risks:**
- Guests on WiFi can wake devices
- IoT devices could be compromised
- Limited monitoring capabilities

### Small Business (Medium Security)

**Recommended configuration:**
- Separate VLAN for WoL-enabled devices
- MAC address whitelisting
- Time-based restrictions
- Centralized logging

**Additional measures:**
- Regular security audits
- Employee training on WoL risks
- Incident response plan

### Enterprise (High Security)

**Recommended configuration:**
- Dedicated management network
- Two-factor authentication for WoL requests
- SIEM integration for monitoring
- Regular penetration testing

**Advanced controls:**
- Network access control (NAC)
- Behavioral analytics
- Automated response to threats
- Compliance reporting

## Technical Implementation

### Secure WoL Gateway

**Architecture:**
```
[WoL Client] → [Auth Gateway] → [Target Network]
      ↓              ↓               ↓
   Request    Validate & Log    Forward if OK
```

**Example gateway implementation:**
```python
class WolGateway:
    def __init__(self):
        self.allowed_clients = load_whitelist()
        self.rate_limiter = RateLimiter()
        
    def handle_request(self, client_ip, target_mac):
        # Check authorization
        if not self.is_authorized(client_ip):
            log_unauthorized(client_ip)
            return False
            
        # Check rate limits
        if self.rate_limiter.is_limited(client_ip):
            log_rate_limit(client_ip)
            return False
            
        # Forward WoL packet
        return self.forward_wol(target_mac)
```

### Encryption Options

**While WoL itself doesn't support encryption, you can:**

1. **VPN tunnel:** Send WoL through encrypted VPN
2. **SSH tunnel:** Port forward through SSH
3. **TLS wrapper:** Custom implementation
4. **IPsec:** Network-level encryption

**Example SSH tunnel:**
```bash
# Tunnel WoL through SSH
ssh -L 9000:target_subnet:9 user@gateway
wakeonlan -p 9000 AA:BB:CC:DD:EE:FF
```

## Compliance Considerations

### Regulatory Requirements

| Regulation | WoL Considerations |
|------------|-------------------|
| **GDPR** | Logging of access attempts, data protection |
| **HIPAA** | Access controls for medical devices |
| **PCI DSS** | Network segmentation, access logging |
| **SOX** | Change management, access reviews |

### Audit Requirements

**Documentation needed:**
1. WoL policy and procedures
2. Authorized devices and users
3. Network architecture diagrams
4. Log retention policy
5. Incident response procedures

**Regular audits should verify:**
- WoL is only enabled where needed
- Access controls are effective
- Logs are complete and secure
- Policies are being followed

## Incident Response

### Detection
- Monitor for unusual WoL patterns
- Alert on failed authentication
- Track wake frequency per device
- Correlate with other security events

### Response Procedures

**Suspected unauthorized WoL:**
1. **Contain:** Block source IP, disable WoL on target
2. **Investigate:** Review logs, interview users
3. **Eradicate:** Remove unauthorized access
4. **Recover:** Restore normal operations
5. **Learn:** Update policies and controls

### Forensics

**Evidence to collect:**
- WoL packet captures
- Network device logs
- Authentication logs
- System logs from target
- User account activity

## Hardening Checklist

### Network Level
- [ ] Use separate VLAN for WoL traffic
- [ ] Implement router ACLs
- [ ] Disable WoL on internet-facing interfaces
- [ ] Enable logging on network devices
- [ ] Regular review of firewall rules

### System Level
- [ ] Enable SecureON with strong passwords
- [ ] Disable WoL on unnecessary devices
- [ ] Regular BIOS/UEFI updates
- [ ] Monitor power state changes
- [ ] Implement host-based firewalls

### Operational Level
- [ ] Maintain inventory of WoL-enabled devices
- [ ] Regular access reviews
- [ ] Employee security training
- [ ] Incident response testing
- [ ] Regular security assessments

## Alternative Secure Solutions

### When WoL is Too Risky

1. **Smart PDUs:** Network-controlled power strips
2. **IP KVM:** Keyboard/video/mouse over IP
3. **Out-of-band management:** iDRAC, iLO, IPMI
4. **Physical controls:** Scheduled power timers
5. **Zero-touch provisioning:** Automated boot sequences

### Risk Assessment Template

**For each WoL deployment, assess:**
- Sensitivity of target systems
- Network exposure level
- Authentication strength
- Monitoring capabilities
- Business impact of compromise

**Scoring:**
- Low risk: Proceed with basic controls
- Medium risk: Implement enhanced controls
- High risk: Consider alternatives to WoL

## Conclusion

Wake-on-LAN is a powerful convenience feature that introduces security risks. By implementing appropriate controls based on your risk assessment, you can enjoy the benefits of remote waking while maintaining security posture.

**Key principles:**
1. **Least privilege:** Only enable WoL where needed
2. **Defense in depth:** Multiple layers of security
3. **Monitoring:** Comprehensive logging and alerting
4. **Regular review:** Continuous improvement of controls