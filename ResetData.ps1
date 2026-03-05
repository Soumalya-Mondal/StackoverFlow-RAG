# define parent folder path
$parentFolderPath = (Resolve-Path ".").Path

# define folder paths to reset
$kbdbFolderPath = Join-Path -Path $parentFolderPath -ChildPath "kbdb"
$outputFolderPath = Join-Path -Path $parentFolderPath -ChildPath "output"

# delete all contents from "kbdb" folder
if (Test-Path -Path $kbdbFolderPath) {
    try {
        Get-ChildItem -Path $kbdbFolderPath -Recurse | Remove-Item -Recurse -Force
    }
    catch {
        Write-Output "ERROR - $($_)"
    }
}

# delete all contents from "output" folder
if (Test-Path -Path $outputFolderPath) {
    try {
        Get-ChildItem -Path $outputFolderPath -Recurse | Remove-Item -Recurse -Force
    }
    catch {
        Write-Output "ERROR - $($_)"
    }
}