<#
.SYNOPSIS
    Skrip Pengayaan Abstrak v2 (Batch Mode) - Jauh lebih cepat.
    Menggunakan OpenAlex batch DOI lookup (50 DOI per request).
    Fallback: Semantic Scholar dan CrossRef untuk sisa yang masih kosong.
#>

$ErrorActionPreference = 'Continue'
$ProgressPreference = 'SilentlyContinue'

$InputCsv  = Join-Path $PSScriptRoot 'csv\all_unique.csv'
$OutputCsv = Join-Path $PSScriptRoot 'csv\all_unique_enriched.csv'
$LogFile   = Join-Path $PSScriptRoot 'enrich_abstracts_log.txt'

# Reset log
if (Test-Path $LogFile) { Remove-Item $LogFile -Force }

function Write-Log {
    param([string]$Message)
    $ts = Get-Date -Format 'HH:mm:ss'
    $line = "[$ts] $Message"
    Write-Host $line
    Add-Content -Path $LogFile -Value $line -Encoding UTF8
}

function Clean-Abstract {
    param([string]$Text)
    if (-not $Text) { return '' }
    $Text = $Text -replace '</?jats:[^>]*>', ' '
    $Text = $Text -replace '<[^>]+>', ' '
    $Text = $Text -replace '\s+', ' '
    return $Text.Trim()
}

function Rebuild-InvertedIndex {
    param($inv)
    if ($null -eq $inv) { return '' }
    $wordPositions = [System.Collections.ArrayList]::new()
    foreach ($prop in $inv.PSObject.Properties) {
        foreach ($pos in $prop.Value) {
            [void]$wordPositions.Add([PSCustomObject]@{ Pos = [int]$pos; Word = $prop.Name })
        }
    }
    $sorted = $wordPositions | Sort-Object Pos
    return ($sorted | ForEach-Object { $_.Word }) -join ' '
}

# ===== MAIN =====
Write-Log '=============================================='
Write-Log 'SKRIP PENGAYAAN ABSTRAK v2 (Batch Mode)'
Write-Log '=============================================='

if (-not (Test-Path $InputCsv)) {
    Write-Log "FATAL: $InputCsv tidak ditemukan"
    exit 1
}

Write-Log 'Membaca CSV input...'
$rows = Import-Csv $InputCsv -Encoding UTF8
$totalRows = $rows.Count
Write-Log "Total baris: $totalRows"

# Build lookup: DOI -> list of row indices with empty abstract
$doiToIndices = @{}
$alreadyFilled = 0
$noDoi = 0

for ($i = 0; $i -lt $rows.Count; $i++) {
    $abs = ($rows[$i].Abstract -as [string]).Trim()
    if (-not [string]::IsNullOrWhiteSpace($abs) -and $abs.Length -ge 10) {
        $alreadyFilled++
        continue
    }
    $doi = ($rows[$i].DOI -as [string]).Trim().ToLower()
    if ($doi -and $doi.Length -gt 5 -and $doi -match '10\.\d{4,}') {
        if (-not $doiToIndices.ContainsKey($doi)) {
            $doiToIndices[$doi] = [System.Collections.ArrayList]::new()
        }
        [void]$doiToIndices[$doi].Add($i)
    } else {
        $noDoi++
    }
}

$uniqueDois = [string[]]$doiToIndices.Keys
$totalToProcess = $uniqueDois.Count
Write-Log "Abstrak sudah terisi  : $alreadyFilled"
Write-Log "DOI unik tanpa abstrak: $totalToProcess"
Write-Log "Tanpa DOI (skip)      : $noDoi"
Write-Log ''

# ===== FASE 1: OpenAlex Batch =====
Write-Log '--- FASE 1: OpenAlex Batch (50 DOI/request) ---'
$oaHit = 0
$oaProcessed = 0
$batchSize = 50

for ($b = 0; $b -lt $uniqueDois.Count; $b += $batchSize) {
    $batch = $uniqueDois[$b..([math]::Min($b + $batchSize - 1, $uniqueDois.Count - 1))]
    $oaProcessed += $batch.Count

    # Build filter: doi:10.xxx|10.yyy|...
    $doiFilter = ($batch | ForEach-Object { "https://doi.org/$_" }) -join '|'
    $filterParam = [System.Uri]::EscapeDataString("doi:$doiFilter")

    $url = "https://api.openalex.org/works?filter=$filterParam&per_page=$batchSize&select=doi,abstract_inverted_index&mailto=research@example.com"

    try {
        $resp = Invoke-RestMethod -Uri $url -Method Get -TimeoutSec 15 -UserAgent 'AcademicSLR/1.0 (mailto:research@example.com)'
        $results = $resp.results
        if ($results) {
            foreach ($work in $results) {
                $wDoi = ($work.doi -replace 'https://doi.org/', '').Trim().ToLower()
                if (-not $wDoi) { continue }
                $abstract = Clean-Abstract (Rebuild-InvertedIndex $work.abstract_inverted_index)
                if ($abstract -and $abstract.Length -ge 30 -and $doiToIndices.ContainsKey($wDoi)) {
                    foreach ($idx in $doiToIndices[$wDoi]) {
                        $rows[$idx].Abstract = $abstract
                    }
                    $oaHit++
                    $doiToIndices.Remove($wDoi)
                }
            }
        }
    }
    catch {
        Write-Log "  Batch error: $($_.Exception.Message)"
    }

    $pct = [math]::Round(($oaProcessed / $totalToProcess) * 100, 0)
    if ($oaProcessed % 200 -lt $batchSize -or $oaProcessed -ge $totalToProcess) {
        Write-Log "  OpenAlex: $oaProcessed / $totalToProcess ($pct persen) | ditemukan: $oaHit"
    }
    Start-Sleep -Milliseconds 200
}

Write-Log "OpenAlex selesai: $oaHit abstrak ditemukan"
Write-Log ''

# ===== FASE 2: Semantic Scholar (sisa yang masih kosong) =====
$remainingDois = [string[]]$doiToIndices.Keys
Write-Log "--- FASE 2: Semantic Scholar (sisa: $($remainingDois.Count) DOI) ---"
$ssHit = 0
$ssProcessed = 0

foreach ($doi in $remainingDois) {
    $ssProcessed++
    try {
        $url = "https://api.semanticscholar.org/graph/v1/paper/DOI:${doi}?fields=abstract"
        $resp = Invoke-RestMethod -Uri $url -Method Get -TimeoutSec 8 -UserAgent 'AcademicSLR/1.0'
        if ($resp.abstract) {
            $abstract = Clean-Abstract $resp.abstract
            if ($abstract.Length -ge 30) {
                foreach ($idx in $doiToIndices[$doi]) {
                    $rows[$idx].Abstract = $abstract
                }
                $ssHit++
                $doiToIndices.Remove($doi)
            }
        }
    }
    catch {
        # 404 or rate limit - skip silently
    }

    if ($ssProcessed % 100 -eq 0 -or $ssProcessed -eq $remainingDois.Count) {
        Write-Log "  SS: $ssProcessed / $($remainingDois.Count) | ditemukan: $ssHit"
    }
    Start-Sleep -Milliseconds 1100  # SS rate limit ~1 req/sec
}

Write-Log "Semantic Scholar selesai: $ssHit abstrak ditemukan"
Write-Log ''

# ===== FASE 3: CrossRef (sisa terakhir) =====
$remainingDois2 = [string[]]$doiToIndices.Keys
Write-Log "--- FASE 3: CrossRef (sisa: $($remainingDois2.Count) DOI) ---"
$crHit = 0
$crProcessed = 0

foreach ($doi in $remainingDois2) {
    $crProcessed++
    try {
        $url = "https://api.crossref.org/works/$doi"
        $resp = Invoke-RestMethod -Uri $url -Method Get -TimeoutSec 8 -UserAgent 'AcademicSLR/1.0 (mailto:research@example.com)'
        if ($resp.message.abstract) {
            $abstract = Clean-Abstract $resp.message.abstract
            if ($abstract.Length -ge 30) {
                foreach ($idx in $doiToIndices[$doi]) {
                    $rows[$idx].Abstract = $abstract
                }
                $crHit++
                $doiToIndices.Remove($doi)
            }
        }
    }
    catch {
        # skip
    }

    if ($crProcessed % 100 -eq 0 -or $crProcessed -eq $remainingDois2.Count) {
        Write-Log "  CR: $crProcessed / $($remainingDois2.Count) | ditemukan: $crHit"
    }
    Start-Sleep -Milliseconds 200
}

Write-Log "CrossRef selesai: $crHit abstrak ditemukan"
Write-Log ''

# ===== RINGKASAN =====
$totalFound = $oaHit + $ssHit + $crHit
$stillEmpty = $doiToIndices.Count + $noDoi
$newTotal = $alreadyFilled + $totalFound
$newPct = [math]::Round(($newTotal / $totalRows) * 100, 1)

Write-Log '=============================================='
Write-Log 'RINGKASAN HASIL PENGAYAAN ABSTRAK'
Write-Log '=============================================='
Write-Log "Total baris CSV              : $totalRows"
Write-Log "Abstrak sudah terisi (awal)  : $alreadyFilled"
Write-Log "DOI unik diproses            : $totalToProcess"
Write-Log '----------------------------------------------'
Write-Log "Berhasil dari OpenAlex       : $oaHit"
Write-Log "Berhasil dari Semantic Scholar: $ssHit"
Write-Log "Berhasil dari CrossRef       : $crHit"
Write-Log "TOTAL ABSTRAK BARU           : $totalFound"
Write-Log '----------------------------------------------'
Write-Log "Masih kosong                 : $($doiToIndices.Count) (ber-DOI) + $noDoi (tanpa DOI)"
$finalMsg = 'KETERISIAN AKHIR: {0} / {1} ({2} persen)' -f $newTotal, $totalRows, $newPct
Write-Log $finalMsg
Write-Log '=============================================='

# Simpan CSV
Write-Log ''
Write-Log "Menyimpan ke: $OutputCsv"
$rows | Export-Csv -Path $OutputCsv -NoTypeInformation -Encoding UTF8
Write-Log 'Selesai'
