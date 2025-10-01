# clean.ps1
# Script PowerShell per la pulizia dei file del progetto (sostituisce clean.sh).

# --- VARIABILI BASATE SU clean.sh ---
$BASE_PATH = ".\HAIIAssessment\mysite"
$FOLDER_PATH1 = Join-Path $BASE_PATH "static\output1"
$FOLDER_PATH2 = Join-Path $BASE_PATH "static\output2"
$FOLDER_PATH3 = Join-Path $BASE_PATH "static\output3"
$FOLDER_PATH4 = Join-Path $BASE_PATH "templates\user-generated"
$FOLDER_PATH5 = Join-Path $BASE_PATH "uploads"
$FOLDER_PATH6 = Join-Path $BASE_PATH "static\output4"

$MAX_SIZE_BYTES = 16500000 # 16.5 MB in bytes
$MAX_AGE_MINUTES_LONG = 119
$MAX_AGE_MINUTES_SHORT = 5
$GITKEEP = ".gitkeep"

# Funzione per calcolare la dimensione totale delle cartelle (in Bytes)
function Get-FolderSizeInBytes {
    param([string[]]$Paths)
    $totalSize = 0
    foreach ($Path in $Paths) {
        if (Test-Path $Path) {
            # Calcola la dimensione totale (ricorsiva) in bytes
            $totalSize += Get-ChildItem -Path $Path -Recurse -File | Measure-Object -Property Length -Sum | Select-Object -ExpandProperty Sum
        }
    }
    return $totalSize
}

# Funzione per cancellare i file più vecchi di un certo numero di minuti (escludendo .gitkeep)
function Cleanup-OldFiles {
    param(
        [string]$Path,
        [int]$Minutes
    )
    if (Test-Path $Path) {
        Write-Host "Cleaning $Path (older than $Minutes minutes)..."
        $CutoffDate = (Get-Date).AddMinutes(-$Minutes)
        
        Get-ChildItem -Path $Path -File -Recurse | Where-Object { 
            ($_.LastWriteTime -lt $CutoffDate) -and ($_.Name -ne $GITKEEP) 
        } | Remove-Item -Force
    }
}

# -------------------------------------------------------------
# 1. ESECUZIONE PULIZIA TEMPORALE (mmin +119 e +5)
# -------------------------------------------------------------

# Pulizia lunga (119 minuti)
$LongCleanupPaths = @($FOLDER_PATH1, $FOLDER_PATH2, $FOLDER_PATH3, $FOLDER_PATH4, $FOLDER_PATH6)
foreach ($Path in $LongCleanupPaths) {
    Cleanup-OldFiles -Path $Path -Minutes $MAX_AGE_MINUTES_LONG
}

# Pulizia breve (5 minuti per uploads)
Cleanup-OldFiles -Path $FOLDER_PATH5 -Minutes $MAX_AGE_MINUTES_SHORT

# -------------------------------------------------------------
# 2. CONTROLLO DIMENSIONE E PULIZIA FORZATA
# -------------------------------------------------------------

$ALL_PATHS = @($FOLDER_PATH1, $FOLDER_PATH2, $FOLDER_PATH3, $FOLDER_PATH4, $FOLDER_PATH5, $FOLDER_PATH6)
$currentTotalSize = Get-FolderSizeInBytes -Paths $ALL_PATHS

Write-Host "Current total size: $($currentTotalSize / 1MB) MB. Max size: $($MAX_SIZE_BYTES / 1MB) MB."

if ($currentTotalSize -gt $MAX_SIZE_BYTES) {
    Write-Warning "Total folder size exceeds $MAX_SIZE_BYTES bytes. Performing forced cleanup!"
    
    foreach ($Path in $ALL_PATHS) {
        if (Test-Path $Path) {
            Write-Host "Forcing delete in $Path..."
            # Elimina TUTTI i file nella cartella (escludendo .gitkeep)
            Get-ChildItem -Path $Path -File -Recurse | Where-Object { $_.Name -ne $GITKEEP } | Remove-Item -Force
        }
    }
}