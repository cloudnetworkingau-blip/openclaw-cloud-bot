#!/usr/bin/env python3
import base64
import http.client
import ssl
import xml.etree.ElementTree as ET

def create_winrm_sleep_request():
    """Create a WinRM SOAP request to execute sleep command"""
    # SOAP envelope for WinRM
    envelope = '''<?xml version="1.0" encoding="UTF-8"?>
<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" 
            xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/08/addressing" 
            xmlns:wsman="http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd">
  <s:Header>
    <wsa:To>http://192.168.0.190:5985/wsman</wsa:To>
    <wsman:ResourceURI>http://schemas.microsoft.com/wbem/wsman/1/windows/shell/cmd</wsman:ResourceURI>
    <wsa:ReplyTo>
      <wsa:Address>http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous</wsa:Address>
    </wsa:ReplyTo>
    <wsa:Action>http://schemas.xmlsoap.org/ws/2004/09/transfer/Create</wsa:Action>
    <wsman:MaxEnvelopeSize s:mustUnderstand="true">153600</wsman:MaxEnvelopeSize>
    <wsa:MessageID>uuid:12345678-1234-1234-1234-123456789012</wsa:MessageID>
    <wsman:Locale xml:lang="en-US" s:mustUnderstand="false"/>
    <wsman:SelectorSet>
      <wsman:Selector Name="ShellId">%s</wsman:Selector>
    </wsman:SelectorSet>
  </s:Header>
  <s:Body>
    <rsp:CommandLine xmlns:rsp="http://schemas.microsoft.com/wbem/wsman/1/windows/shell">
      <rsp:Command>rundll32.exe</rsp:Command>
      <rsp:Arguments>powrprof.dll,SetSuspendState 0,1,0</rsp:Arguments>
    </rsp:CommandLine>
  </s:Body>
</s:Envelope>'''
    return envelope

def main():
    host = "192.168.0.190"
    port = 5985
    username = "geez"
    password = "yslgwayhzaq1@WSW"
    
    # Create basic auth header
    auth = base64.b64encode(f"{username}:{password}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/soap+xml;charset=UTF-8",
        "User-Agent": "Python WinRM Client"
    }
    
    try:
        # Create connection (WinRM uses HTTP, not HTTPS by default)
        conn = http.client.HTTPConnection(host, port, timeout=10)
        
        # First, create a shell
        print("Creating WinRM shell...")
        create_shell_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" 
            xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/08/addressing" 
            xmlns:wsman="http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd">
  <s:Header>
    <wsa:To>http://192.168.0.190:5985/wsman</wsa:To>
    <wsman:ResourceURI>http://schemas.microsoft.com/wbem/wsman/1/windows/shell/cmd</wsman:ResourceURI>
    <wsa:ReplyTo>
      <wsa:Address>http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous</wsa:Address>
    </wsa:ReplyTo>
    <wsa:Action>http://schemas.xmlsoap.org/ws/2004/09/transfer/Create</wsa:Action>
    <wsman:MaxEnvelopeSize s:mustUnderstand="true">153600</wsman:MaxEnvelopeSize>
    <wsa:MessageID>uuid:12345678-1234-1234-1234-123456789012</wsa:MessageID>
    <wsman:Locale xml:lang="en-US" s:mustUnderstand="false"/>
  </s:Header>
  <s:Body>
    <rsp:Shell xmlns:rsp="http://schemas.microsoft.com/wbem/wsman/1/windows/shell">
      <rsp:InputStreams>stdin</rsp:InputStreams>
      <rsp:OutputStreams>stdout stderr</rsp:OutputStreams>
    </rsp:Shell>
  </s:Body>
</s:Envelope>'''
        
        conn.request("POST", "/wsman", create_shell_xml, headers)
        response = conn.getresponse()
        
        if response.status != 200:
            print(f"Failed to create shell: {response.status} {response.reason}")
            return False
            
        # Parse response to get ShellId
        response_data = response.read().decode()
        root = ET.fromstring(response_data)
        ns = {'w': 'http://schemas.xmlsoap.org/ws/2004/08/addressing',
              'p': 'http://schemas.microsoft.com/wbem/wsman/1/windows/shell'}
        
        shell_id_elem = root.find('.//{http://schemas.microsoft.com/wbem/wsman/1/windows/shell}ShellId')
        if shell_id_elem is None:
            print("Could not find ShellId in response")
            return False
            
        shell_id = shell_id_elem.text
        print(f"Got ShellId: {shell_id}")
        
        # Now execute sleep command
        print("Executing sleep command...")
        sleep_request = create_winrm_sleep_request().replace("%s", shell_id)
        conn.request("POST", "/wsman", sleep_request, headers)
        response = conn.getresponse()
        
        if response.status == 200:
            print("Sleep command sent successfully!")
            print("Your Windows machine should be going to sleep now.")
            return True
        else:
            print(f"Failed to execute command: {response.status} {response.reason}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)