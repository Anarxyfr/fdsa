Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Speech

Start-Process "magnify.exe"
Start-Sleep -Seconds 2
[System.Windows.Forms.SendKeys]::SendWait("^{%}{i}")

Start-Job {
    $s = New-Object -ComObject SAPI.SpVoice
    $w = @("a","b","c","d","e","f")
    for ($i = 0; $i -lt 20; $i++) {
        $s.Speak(($w | Get-Random))
        Start-Sleep -Milliseconds (Get-Random -Minimum 100 -Maximum 400)
    }
}

Start-Job {
    for ($i = 0; $i -lt 50; $i++) {
        [System.Windows.Forms.MessageBox]::Show("0x" + (Get-Random -Minimum 1000 -Maximum 9999), "x", 0, 48)
        Start-Sleep -Milliseconds 250
    }
}

Start-Job {
    for ($i = 0; $i -lt 100; $i++) {
        Set-Clipboard ("X" * (Get-Random -Minimum 3 -Maximum 6))
        Start-Sleep -Milliseconds (Get-Random -Minimum 100 -Maximum 200)
    }
}

Start-Job {
    for ($i = 0; $i -lt 1000; $i++) {
        $x = Get-Random -Minimum 0 -Maximum ([System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width)
        $y = Get-Random -Minimum 0 -Maximum ([System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Height)
        [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point($x, $y)
        Start-Sleep -Milliseconds (Get-Random -Minimum 10 -Maximum 40)
    }
}

Start-Job {
    $k = @("A","B","C","D","E","F","1","2","3","4","5")
    for ($i = 0; $i -lt 1000; $i++) {
        [System.Windows.Forms.SendKeys]::SendWait(($k | Get-Random))
        Start-Sleep -Milliseconds (Get-Random -Minimum 5 -Maximum 30)
    }
}

Start-Job {
    for ($i = 0; $i -lt 30; $i++) {
        $f = New-Object Windows.Forms.Form
        $f.FormBorderStyle = 'None'
        $f.TopMost = $true
        $f.WindowState = 'Maximized'
        $f.BackColor = [System.Drawing.Color]::FromArgb((Get-Random -Minimum 0 -Maximum 255),(Get-Random -Minimum 0 -Maximum 255),(Get-Random -Minimum 0 -Maximum 255))
        $f.Show()
        Start-Sleep -Milliseconds (Get-Random -Minimum 80 -Maximum 160)
        $f.Close()
    }
}

Start-Job {
    $a = @("notepad","calc","mspaint","write","cmd")
    for ($i = 0; $i -lt 20; $i++) {
        Start-Process ($a | Get-Random)
        Start-Sleep -Milliseconds 300
    }
}

Start-Job {
    for ($i = 0; $i -lt 100; $i++) {
        [console]::beep((Get-Random -Minimum 100 -Maximum 3000), (Get-Random -Minimum 50 -Maximum 200))
    }
}

Start-Job {
    $f = New-Object Windows.Forms.Form
    $f.Text = "x"
    $f.BackColor = 'Red'
    $f.TopMost = $true
    $f.Width = 300
    $f.Height = 100
    $f.Show()
    Start-Sleep -Seconds 10
    $f.Close()
}

Start-Sleep -Seconds 20
[System.Windows.Forms.SendKeys]::SendWait("^{%}{i}")
