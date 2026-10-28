$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$diagramRoot = Split-Path -Parent $PSScriptRoot
$diagramOutput = Join-Path $diagramRoot 'docs/state_diagram.png'
$bitmap = New-Object System.Drawing.Bitmap 1600,1080
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
$graphics.Clear([System.Drawing.Color]::White)
$fontTitle = New-Object System.Drawing.Font 'Segoe UI',30,([System.Drawing.FontStyle]::Bold)
$fontNode = New-Object System.Drawing.Font 'Segoe UI',25,([System.Drawing.FontStyle]::Bold)
$fontBody = New-Object System.Drawing.Font 'Segoe UI',18
$fontLabel = New-Object System.Drawing.Font 'Segoe UI',18
$textBrush = New-Object System.Drawing.SolidBrush ([System.Drawing.ColorTranslator]::FromHtml('#17243A'))
$arrowPen = New-Object System.Drawing.Pen ([System.Drawing.ColorTranslator]::FromHtml('#51647A')),3
$arrowPen.CustomEndCap = New-Object System.Drawing.Drawing2D.AdjustableArrowCap 6,7
$format = New-Object System.Drawing.StringFormat
$format.Alignment = [System.Drawing.StringAlignment]::Center
$format.LineAlignment = [System.Drawing.StringAlignment]::Center

function Label([string]$Text, [single]$X, [single]$Y, $Font = $fontLabel) {
    $size = $graphics.MeasureString($Text, $Font)
    $labelRect = New-Object System.Drawing.RectangleF ($X - $size.Width / 2 - 8),($Y - $size.Height / 2 - 3),($size.Width + 16),($size.Height + 6)
    $graphics.FillRectangle([System.Drawing.Brushes]::White, $labelRect)
    $graphics.DrawString($Text, $Font, $textBrush, (New-Object System.Drawing.PointF $X,$Y), $format)
}

function Arrow([single]$X1, [single]$Y1, [single]$X2, [single]$Y2) {
    $graphics.DrawLine($arrowPen, $X1, $Y1, $X2, $Y2)
}

function State([single]$X, [single]$Y, [single]$W, [single]$H, [string]$Title, [string[]]$Lines, [string]$Color) {
    $fill = New-Object System.Drawing.SolidBrush ([System.Drawing.ColorTranslator]::FromHtml($Color))
    $border = New-Object System.Drawing.Pen ([System.Drawing.ColorTranslator]::FromHtml('#8191A5')),2
    $rect = New-Object System.Drawing.RectangleF $X,$Y,$W,$H
    $graphics.FillRectangle($fill, $rect)
    $graphics.DrawRectangle($border, $X, $Y, $W, $H)
    $graphics.DrawString($Title, $fontNode, $textBrush, (New-Object System.Drawing.PointF ($X + $W / 2),($Y + 34)), $format)
    $lineY = $Y + 78
    foreach ($line in $Lines) {
        $graphics.DrawString($line, $fontBody, $textBrush, (New-Object System.Drawing.PointF ($X + $W / 2),$lineY), $format)
        $lineY += 33
    }
    $fill.Dispose()
    $border.Dispose()
}

try {
    Label 'Drill #11 - AutoRun State Diagram' 800 44 $fontTitle
    Label 'A dedicated AutoRun class; one RUN state for left and right' 800 96 $fontBody
    Arrow 75 520 120 520
    $graphics.FillEllipse($textBrush, 43, 508, 24, 24)
    Arrow 420 485 1180 485
    Arrow 1180 555 420 555
    Arrow 385 450 685 330
    Arrow 610 235 220 450
    Arrow 990 255 1320 450
    Arrow 235 590 650 875
    Arrow 735 800 405 590
    Arrow 950 875 1330 590

    Label 'Left / Right key down' 800 457
    Label 'All direction keys released' 800 589
    Label 'A key down' 535 371
    Label '5 seconds / restore size' 350 286
    Label 'Arrow key / normal Run' 1275 331
    Label 'Idle for 5 seconds' 325 755
    Label 'Space key down' 650 663
    Label 'Left / Right key down' 1280 755

    State 120 450 300 140 'IDLE' @('Idle animation', 'Normal size') '#EAF2FF'
    State 1180 450 300 140 'RUN' @('200 px/s | 100 x 100', 'Move while key held') '#EAF7ED'
    State 610 150 380 180 'AUTO_RUN' @('AutoRun class', '400 px/s | 150 x 150', 'Bounce at edges | 5 s') '#F1ECFF'
    State 650 800 300 140 'SLEEP' @('Lie down', 'Space / arrow to wake') '#F0F2F5'
    Label 'Screen: 800 x 600 | Character stays inside the screen in both Run modes' 800 1000 $fontBody
    $bitmap.Save($diagramOutput, [System.Drawing.Imaging.ImageFormat]::Png)
    Write-Output $diagramOutput
} finally {
    $graphics.Dispose()
    $bitmap.Dispose()
    $fontTitle.Dispose()
    $fontNode.Dispose()
    $fontBody.Dispose()
    $fontLabel.Dispose()
    $textBrush.Dispose()
    $arrowPen.Dispose()
    $format.Dispose()
}
