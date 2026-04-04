#!/usr/bin/env python3
import subprocess
import sys

def put_windows_to_sleep():
    """
    Connect to Windows via WinRM and put it to sleep
    """
    # First, let's try using winexe if available
    try:
        # Check if winexe is installed
        result = subprocess.run(['which', 'winexe'], capture_output=True, text=True)
        if result.returncode == 0:
            print("winexe found, attempting to put Windows to sleep...")
            # Using winexe to run sleep command
            cmd = f'winexe -U geez%yslgwayhzaq1@WSW //192.168.0.190 "rundll32.exe powrprof.dll,SetSuspendState 0,1,0"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print("Success! Windows should be going to sleep now.")
                return True
            else:
                print(f"winexe failed: {result.stderr}")
                return False
        else:
            print("winexe not found")
    except Exception as e:
        print(f"Error with winexe: {e}")
    
    # Try using impacket's wmiexec.py if available
    try:
        # Check for impacket
        import importlib
        spec = importlib.util.find_spec("impacket")
        if spec is not None:
            print("impacket found, trying wmiexec...")
            # Create a simple command file
            with open('/tmp/sleep_cmd.txt', 'w') as f:
                f.write('rundll32.exe powrprof.dll,SetSuspendState 0,1,0\n')
            
            cmd = f'python3 -c "from impacket.examples import wmiexec; wmiexec.wmiexec(\'geez:yslgwayhzaq1@WSW@192.168.0.190\', \'cmd.exe\')" < /tmp/sleep_cmd.txt'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print("Success via wmiexec!")
                return True
            else:
                print(f"wmiexec failed: {result.stderr}")
                return False
        else:
            print("impacket not found")
    except Exception as e:
        print(f"Error with impacket: {e}")
    
    # Try using evil-winrm if available
    try:
        result = subprocess.run(['which', 'evil-winrm'], capture_output=True, text=True)
        if result.returncode == 0:
            print("evil-winrm found, attempting connection...")
            # Create a PowerShell script to sleep
            ps_script = '''$ErrorActionPreference = "Stop"
try {
    Add-Type -AssemblyName System.Windows.Forms
    [System.Windows.Forms.Application]::SetSuspendState([System.Windows.Forms.PowerState]::Suspend, $false, $false)
    Write-Output "Sleep command executed successfully"
} catch {
    Write-Output "Error: $_"
    exit 1
}'''
            
            with open('/tmp/sleep.ps1', 'w') as f:
                f.write(ps_script)
            
            cmd = f'evil-winrm -i 192.168.0.190 -u geez -p \'yslgwayhzaq1@WSW\' -s /tmp -c "powershell -ExecutionPolicy Bypass -File sleep.ps1"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print("Success via evil-winrm!")
                return True
            else:
                print(f"evil-winrm failed: {result.stderr}")
                return False
        else:
            print("evil-winrm not found")
    except Exception as e:
        print(f"Error with evil-winrm: {e}")
    
    print("All methods failed. Please install one of: winexe, impacket, or evil-winrm")
    return False

if __name__ == "__main__":
    success = put_windows_to_sleep()
    sys.exit(0 if success else 1)