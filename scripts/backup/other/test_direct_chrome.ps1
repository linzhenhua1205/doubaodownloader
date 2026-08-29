# 直接测试Chrome是否能运行
Write-Host "="*60
Write-Host "直接测试Chrome运行"
Write-Host "="*60

$chromePath = "h:\github\md\chrome-win64\chrome-win64\chrome.exe"

Write-Host "检查Chrome文件..."
if (Test-Path $chromePath) {
    Write-Host "[OK] Chrome文件存在"
    
    Write-Host "`n尝试启动Chrome（将在5秒后自动关闭）..."
    $process = Start-Process -FilePath $chromePath -PassThru -ArgumentList "--version"
    Start-Sleep -Seconds 3
    if ($process -and !$process.HasExited) {
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
    }
    Write-Host "[OK] Chrome测试完毕"
} else {
    Write-Host "[ERROR] Chrome文件不存在: $chromePath"
}

Write-Host "`n" + "="*60
Write-Host "测试完成"
Write-Host "="*60
