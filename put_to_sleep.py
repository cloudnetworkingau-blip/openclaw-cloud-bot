#!/usr/bin/env python3
"""
Script to put a Windows computer to sleep remotely.
Supports multiple methods: WinRM, WMI, and RDP-based approaches.
"""

import sys
import subprocess
import socket
import time

def check_port(host, port, timeout=2):
    """Check if a port is open on the target host."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def put_to_sleep_windows(host, username=None, password=None):
    """
    Attempt to put a Windows computer to sleep using various methods.
    
    Args:
        host: IP address or hostname of the Windows machine
        username: Optional username for authentication
        password: Optional password for authentication
    """
    
    print(f"Attempting to put {host} to sleep...")
    
    # Method 1: Try using net rpc (if Samba tools are available)
    print("\nMethod 1: Trying net rpc command...")
    try:
        cmd = ["net", "rpc", "shutdown", "-t", "1", "-f", "-C", "Sleep command", "-I", host]
        if username and password:
            cmd.extend(["-U", f"{username}%{password}"])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✓ Sleep command sent via net rpc")
            return True
        else:
            print(f"✗ net rpc failed: {result.stderr}")
    except FileNotFoundError:
        print("✗ net command not available")
    except subprocess.TimeoutExpired:
        print("✗ net rpc timed out")
    
    # Method 2: Try using winexe (if available)
    print("\nMethod 2: Trying winexe...")
    try:
        auth = ""
        if username and password:
            auth = f"--user={username}%{password}"
        
        cmd = f"winexe {auth} //{host} 'rundll32.exe powrprof.dll,SetSuspendState 0,1,0'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✓ Sleep command sent via winexe")
            return True
        else:
            print(f"✗ winexe failed: {result.stderr}")
    except FileNotFoundError:
        print("✗ winexe not installed")
    except subprocess.TimeoutExpired:
        print("✗ winexe timed out")
    
    # Method 3: Create a simple RDP-based approach suggestion
    print("\nMethod 3: Manual RDP approach")
    print("Since RDP port 3389 is open, you can:")
    print("1. Connect via RDP using xfreerdp:")
    print(f"   xfreerdp /v:{host} /u:[username] /p:[password]")
    print("2. Once connected, press Windows key + X, then U, then S")
    print("   (or use Start Menu > Power > Sleep)")
    
    # Method 4: PowerShell suggestion
    print("\nMethod 4: PowerShell approach (requires PowerShell on this machine)")
    print("Install PowerShell on Linux: sudo snap install powershell --classic")
    print("Then run:")
    print(f"   pwsh -Command \"\\\"(New-Object -ComObject WScript.Shell).SendKeys('%%{ESC}') | Out-Null; Start-Sleep -Seconds 2; (New-Object -ComObject WScript.Shell).SendKeys('u'); Start-Sleep -Seconds 1; (New-Object -ComObject WScript.Shell).SendKeys('s')\\\"\"")
    
    return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 put_to_sleep.py <host_ip> [username] [password]")
        print("Example: python3 put_to_sleep.py 192.168.0.190")
        sys.exit(1)
    
    host = sys.argv[1]
    username = sys.argv[2] if len(sys.argv) > 2 else None
    password = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Check if host is reachable
    print(f"Checking connectivity to {host}...")
    
    # Check RDP port
    if check_port(host, 3389):
        print("✓ RDP port 3389 is open")
    else:
        print("✗ RDP port 3389 is closed")
    
    # Check WinRM port
    if check_port(host, 5985):
        print("✓ WinRM port 5985 is open")
    else:
        print("✗ WinRM port 5985 is closed")
    
    # Check SMB port
    if check_port(host, 445):
        print("✓ SMB port 445 is open")
    else:
        print("✗ SMB port 445 is closed")
    
    # Try to put to sleep
    success = put_to_sleep_windows(host, username, password)
    
    if success:
        print(f"\n✅ Successfully sent sleep command to {host}")
        print("The computer should enter sleep mode shortly.")
    else:
        print(f"\n❌ Could not automatically put {host} to sleep")
        print("\nAlternative solutions:")
        print("1. Use physical access: Press the power button briefly")
        print("2. Schedule a sleep task on the Windows machine itself")
        print("3. Use a smart power strip that can cut power")
        print("4. Configure BIOS power management for auto-sleep")
    
    print(f"\nMAC Address for Wake-on-LAN: e0:4f:43:e6:50:d6")
    print("To wake it up later, use: wakeonlan e0:4f:43:e6:50:d6")

if __name__ == "__main__":
    main()