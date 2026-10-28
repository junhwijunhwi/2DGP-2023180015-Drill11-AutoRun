$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$diagramRoot = Split-Path -Parent $PSScriptRoot
$diagramOutput = Join-Path $diagramRoot 'docs/state_diagram.png'
$bitmap = New-Object System.Drawing.Bitmap 1600,1080
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
$graphics.Clear([System.Drawing.Color]::White)
$fontTitle = New-Object System.Drawing.Font 'Malgun Gothic',30,([System.Drawing.FontStyle]::Bold)
$fontNode = New-Object System.Drawing.Font 'Malgun Gothic',25,([System.Drawing.FontStyle]::Bold)
$fontBody = New-Object System.Drawing.Font 'Malgun Gothic',18
$fontLabel = New-Object System.Drawing.Font 'Malgun Gothic',18
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
    Label '실습 #11 - 소년 자동 무적 런 상태 다이어그램' 800 44 $fontTitle
    Label 'AutoRun 상태 클래스 추가 / 좌우 이동은 하나의 RUN 상태로 처리' 800 96 $fontBody
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

    Label '왼쪽 / 오른쪽 방향키 누름' 800 457
    Label '방향키를 모두 뗌' 800 589
    Label 'A 키 누름' 535 371
    Label '5초 경과 / 원래 크기로 복귀' 350 286
    Label '방향키 누름 / 일반 달리기로 전환' 1275 331
    Label '대기 상태에서 5초 경과' 325 755
    Label '스페이스 키 누름' 650 663
    Label '왼쪽 / 오른쪽 방향키 누름' 1280 755

    State 120 450 300 140 '대기 (IDLE)' @('대기 애니메이션', '기본 크기') '#EAF2FF'
    State 1180 450 300 140 '달리기 (RUN)' @('초당 200픽셀 | 100 x 100', '방향키를 누를 때 이동') '#EAF7ED'
    State 610 150 380 180 '자동 무적 런' @('AutoRun 상태 클래스', '초당 400픽셀 | 150 x 150', '양 끝에서 자동 반사 | 5초') '#F1ECFF'
    State 650 800 300 140 '수면 (SLEEP)' @('누운 자세로 정지', '스페이스 / 방향키로 기상') '#F0F2F5'
    Label '화면: 800 x 600 | 일반 달리기와 자동 무적 런 모두 캐릭터 전체가 화면 안에 머무름' 800 1000 $fontBody
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
