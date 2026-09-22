<#
.SYNOPSIS
    Sinkronisasi Abstrak Hasil Pengayaan ke Seluruh File CSV.
    - Backup all_unique.csv -> all_unique_original_backup.csv
    - Ganti all_unique.csv dengan all_unique_enriched.csv
    - Sinkronkan abstrak ke all_combined.csv dan seluruh file raw database
#>

$ErrorActionPreference = 'Stop'
$csvDir = Join-Path $PSScriptRoot 'csv'
$enrichedFile = Join-Path $csvDir 'all_unique_enriched.csv'

if (-not (Test-Path $enrichedFile)) {
    Write-Error "File $enrichedFile tidak ditemukan!"
}

Write-Host "=== MEMULAI SINKRONISASI ABSTRAK ==="
Write-Host "Membaca data pengayaan dari all_unique_enriched.csv..."
$enriched = Import-Csv $enrichedFile -Encoding UTF8

$doiMap = @{}
$titleMap = @{}

foreach ($row in $enriched) {
    $abs = ($row.Abstract -as [string]).Trim()
    if ($abs.Length -ge 20) {
        $doi = ($row.DOI -as [string]).Trim().ToLower()
        if ($doi -and $doi.Length -gt 5) {
            $doiMap[$doi] = $abs
        }
        $title = ($row.Title -as [string]).Trim().ToLower() -replace '[^a-z0-9]', ''
        if ($title.Length -ge 10) {
            $titleMap[$title] = $abs
        }
    }
}

Write-Host "Total abstrak valid dalam kamus pengayaan: $($doiMap.Count) DOI, $($titleMap.Count) Judul"
Write-Host ""

# 1. Backup dan update all_unique.csv
$uniqueFile = Join-Path $csvDir 'all_unique.csv'
$uniqueBackup = Join-Path $csvDir 'all_unique_original_backup.csv'
if (-not (Test-Path $uniqueBackup)) {
    Copy-Item $uniqueFile $uniqueBackup -Force
    Write-Host "[OK] Backup dibuat: all_unique_original_backup.csv"
}
Copy-Item $enrichedFile $uniqueFile -Force
Write-Host "[OK] all_unique.csv telah diperbarui dengan data enriched."
Write-Host ""

# 2. Sinkronkan ke seluruh file CSV lainnya
$targetFiles = @(
    'sciencedirect.csv',
    'scopus.csv',
    'crossref.csv',
    'openalex.csv',
    'semantic_scholar.csv',
    'springer.csv',
    'pubmed.csv',
    'all_combined.csv'
)

Write-Host "=== SINKRONISASI KE FILE RAW & COMBINED ==="
foreach ($fileName in $targetFiles) {
    $filePath = Join-Path $csvDir $fileName
    if (-not (Test-Path $filePath)) {
        Write-Host "[-] Lewati $fileName (file tidak ada)"
        continue
    }

    # Buat backup jika belum ada
    $backupPath = Join-Path $csvDir "$fileName.bak"
    if (-not (Test-Path $backupPath)) {
        Copy-Item $filePath $backupPath -Force
    }

    $rows = Import-Csv $filePath -Encoding UTF8
    $totalRows = $rows.Count
    $updatedCount = 0
    $alreadyFilled = 0

    for ($i = 0; $i -lt $rows.Count; $i++) {
        $currentAbs = ($rows[$i].Abstract -as [string]).Trim()
        if ($currentAbs.Length -ge 20) {
            $alreadyFilled++
            continue
        }

        $doi = ($rows[$i].DOI -as [string]).Trim().ToLower()
        $matchedAbs = $null

        if ($doi -and $doiMap.ContainsKey($doi)) {
            $matchedAbs = $doiMap[$doi]
        } else {
            $cleanTitle = ($rows[$i].Title -as [string]).Trim().ToLower() -replace '[^a-z0-9]', ''
            if ($cleanTitle -and $titleMap.ContainsKey($cleanTitle)) {
                $matchedAbs = $titleMap[$cleanTitle]
            }
        }

        if ($matchedAbs) {
            $rows[$i].Abstract = $matchedAbs
            $updatedCount++
        }
    }

    $rows | Export-Csv -Path $filePath -NoTypeInformation -Encoding UTF8
    $finalFilled = $alreadyFilled + $updatedCount
    $pct = [math]::Round(($finalFilled / $totalRows) * 100, 1)

    Write-Host ("{0,-22}: +{1,4} abstrak baru | Total terisi: {2,4}/{3,4} ({4,5}%)" -f $fileName, $updatedCount, $finalFilled, $totalRows, $pct)
}

Write-Host ""
Write-Host "=== SINKRONISASI SELESAI DENGAN SUKSES ==="
