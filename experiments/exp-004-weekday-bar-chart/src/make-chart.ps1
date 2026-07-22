# Regenerates artifacts/weekday-values-bar-chart.png
#
# Uses System.Drawing from the installed .NET runtime — no packages to install.
# Run from anywhere:
#     powershell -ExecutionPolicy Bypass -File src/make-chart.ps1

Add-Type -AssemblyName System.Drawing

$data = [ordered]@{ Mon = 12; Tue = 19; Wed = 7; Thu = 22; Fri = 15 }

$W, $H = 1200, 750
$left, $right, $top, $bottom = 120, 60, 100, 90
$plotW = $W - $left - $right
$plotH = $H - $top - $bottom
$yMax = 25          # fixed so the gridlines land on round numbers

$bmp = New-Object System.Drawing.Bitmap $W, $H
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = 'AntiAlias'
$g.TextRenderingHint = 'ClearTypeGridFit'
$g.Clear([System.Drawing.Color]::FromArgb(249, 250, 252))

$ink = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(30, 41, 59))
$muted = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(100, 116, 139))
$bar = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(37, 99, 235))
$grid = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(226, 232, 240)), 1
$axis = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(71, 85, 105)), 2

$titleFont = New-Object System.Drawing.Font 'Segoe UI', 26, ([System.Drawing.FontStyle]::Bold)
$labelFont = New-Object System.Drawing.Font 'Segoe UI', 14
$valueFont = New-Object System.Drawing.Font 'Segoe UI', 14, ([System.Drawing.FontStyle]::Bold)
$tickFont = New-Object System.Drawing.Font 'Segoe UI', 11

$centre = New-Object System.Drawing.StringFormat
$centre.Alignment = 'Center'
$rightAlign = New-Object System.Drawing.StringFormat
$rightAlign.Alignment = 'Far'

# title
$g.DrawString('Weekday Values', $titleFont, $ink,
    (New-Object System.Drawing.RectangleF 0, 25, $W, 45), $centre)

# y gridlines + ticks, every 5
for ($v = 0; $v -le $yMax; $v += 5) {
    $y = $top + $plotH - ($v / $yMax * $plotH)
    if ($v -gt 0) { $g.DrawLine($grid, $left, $y, $left + $plotW, $y) }
    $g.DrawString("$v", $tickFont, $muted,
        (New-Object System.Drawing.RectangleF ($left - 55), ($y - 10), 45, 20), $rightAlign)
}

# axes
$g.DrawLine($axis, $left, $top, $left, $top + $plotH)
$g.DrawLine($axis, $left, ($top + $plotH), ($left + $plotW), ($top + $plotH))

# y axis title, rotated
$state = $g.Save()
$g.TranslateTransform(42, ($top + $plotH / 2))
$g.RotateTransform(-90)
$g.DrawString('Value', $labelFont, $muted,
    (New-Object System.Drawing.RectangleF -60, -12, 120, 24), $centre)
$g.Restore($state)

# bars — note: $barH, not $h; PowerShell variables are case-insensitive and
# $h would silently overwrite the canvas height $H.
$slot = $plotW / $data.Count
$barW = $slot * 0.42
$i = 0
foreach ($day in $data.Keys) {
    $value = $data[$day]
    $barH = $value / $yMax * $plotH
    $x = $left + ($i * $slot) + (($slot - $barW) / 2)
    $y = $top + $plotH - $barH

    $g.FillRectangle($bar, $x, $y, $barW, $barH)
    # value label above the bar — direct labelling, so no legend is needed
    $g.DrawString("$value", $valueFont, $ink,
        (New-Object System.Drawing.RectangleF ($x - 30), ($y - 32), ($barW + 60), 26), $centre)
    # weekday label below the axis
    $g.DrawString($day, $labelFont, $muted,
        (New-Object System.Drawing.RectangleF ($x - 30), ($top + $plotH + 14), ($barW + 60), 26), $centre)
    $i++
}

$out = Join-Path $PSScriptRoot '..\artifacts\weekday-values-bar-chart.png'
$dir = Split-Path $out -Parent
if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null }
$bmp.Save((Resolve-Path -LiteralPath $dir).Path + '\weekday-values-bar-chart.png',
    [System.Drawing.Imaging.ImageFormat]::Png)

$g.Dispose(); $bmp.Dispose()
Write-Host "wrote $((Resolve-Path $out).Path)  ($W x $H)"
