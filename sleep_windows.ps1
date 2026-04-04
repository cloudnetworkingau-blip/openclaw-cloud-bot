# PowerShell script to put Windows computer to sleep
# Usage: powershell -ExecutionPolicy Bypass -File sleep_windows.ps1 -ComputerName 192.168.0.190

param(
    [string]$ComputerName = "localhost",
    [PSCredential]$Credential
)

# Function to put computer to sleep
function Invoke-Sleep {
    param(
        [string]$TargetComputer
    )
    
    try {
        # Create a CIM session
        $SessionParams = @{
            ComputerName = $TargetComputer
            ErrorAction = 'Stop'
        }
        
        if ($Credential) {
            $SessionParams.Credential = $Credential
        }
        
        $CimSession = New-CimSession @SessionParams
        
        # Put computer to sleep
        Invoke-CimMethod -CimSession $CimSession -ClassName Win32_OperatingSystem -MethodName Win32Shutdown -Arguments @{Flags = 4}
        
        Write-Host "Sleep command sent successfully to $TargetComputer" -ForegroundColor Green
        
        # Clean up
        Remove-CimSession -CimSession $CimSession
    }
    catch {
        Write-Host "Error: $_" -ForegroundColor Red
        return $false
    }
    
    return $true
}

# Alternative method using WMI
function Invoke-SleepWMI {
    param(
        [string]$TargetComputer
    )
    
    try {
        $WmiParams = @{
            Class = 'Win32_OperatingSystem'
            Name = 'Win32Shutdown'
            ArgumentList = 4  # 4 = Sleep
            ComputerName = $TargetComputer
            ErrorAction = 'Stop'
        }
        
        if ($Credential) {
            $WmiParams.Credential = $Credential
        }
        
        Invoke-WmiMethod @WmiParams
        
        Write-Host "Sleep command sent successfully to $TargetComputer via WMI" -ForegroundColor Green
    }
    catch {
        Write-Host "Error: $_" -ForegroundColor Red
        return $false
    }
    
    return $true
}

# Try CIM first, fall back to WMI
$Result = Invoke-Sleep -TargetComputer $ComputerName
if (-not $Result) {
    Write-Host "Trying WMI method..." -ForegroundColor Yellow
    $Result = Invoke-SleepWMI -TargetComputer $ComputerName
}

if ($Result) {
    exit 0
} else {
    exit 1
}