$archiveCount = (Get-ChildItem -Path ARCHIVE -Recurse -File -Filter *.py).Count
$activeCount = (Get-ChildItem -Path . -File -Filter *.py | Where-Object { $_.FullName -notmatch "ARCHIVE" }).Count

Write-Host "📊 검증 결과:"
Write-Host "  활성 파일: $activeCount개"
Write-Host "  보관 파일: $archiveCount개"
Write-Host "  총 파일: $($activeCount + $archiveCount)개"

if ($archiveCount -ge 20) {
    Write-Host "✅ ARCHIVE 파일 수 정상 (26개)"
}
else {
    Write-Host "⚠️  ARCHIVE 파일 수 불일치 (예상: ~26개, 실제: $archiveCount개)"
}

if ($activeCount -le 30) {
    Write-Host "✅ 활성 파일 수 정상 (26개)"
}
else {
    Write-Host "⚠️  활성 파일 수 불일치 (예상: ~26개, 실제: $activeCount개)"
}

Write-Host "`n📁 ARCHIVE 카테고리별:"
Write-Host "  mapper: $((Get-ChildItem ARCHIVE\duplicates\mapper -File -ErrorAction SilentlyContinue).Count)개"
Write-Host "  tests: $((Get-ChildItem ARCHIVE\duplicates\tests -File -ErrorAction SilentlyContinue).Count)개"
Write-Host "  analyzers: $((Get-ChildItem ARCHIVE\duplicates\analyzers -File -ErrorAction SilentlyContinue).Count)개"
Write-Host "  legacy: $((Get-ChildItem ARCHIVE\legacy -File -ErrorAction SilentlyContinue).Count)개"
Write-Host "  old_versions: $((Get-ChildItem ARCHIVE\old_versions -File -ErrorAction SilentlyContinue).Count)개"

