<#
.SYNOPSIS
   This script creates a backup of new or changed files from a source folder to a destination folder in OneDrive.

.PARAMETER SourceFolderPath
   The full path of the source folder to be backed up.

.PARAMETER DestinationFolderName
   The name of the destination folder in the OneDrive root directory where the backup will be stored.
#>
param (
    [Parameter(Mandatory=$true)]
    [string]$SourceFolderPath,
    
    [Parameter(Mandatory=$true)]
    [string]$DestinationFolderName
)

#$ErrorActionPreference = "Stop"

function Copy-NewOrChangedFiles {
    param (
        [string]$Source,
        [string]$Destination
    )

    $filesCopied = $false

    Get-ChildItem -Path $Source -Recurse | ForEach-Object {
        $sourceFile = $_
        $destinationFile = $sourceFile.FullName.Replace($Source, $Destination)

        if (-not (Test-Path -Path $destinationFile)) {
            $destinationDirectory = Split-Path -Path $destinationFile -Parent
            if (-not (Test-Path -Path $destinationDirectory)) {
                New-Item -ItemType Directory -Path $destinationDirectory -Force | Out-Null
            }
            Copy-Item -Path $sourceFile.FullName -Destination $destinationFile -Force
            $filesCopied = $true
        } elseif ($sourceFile.LastWriteTime -gt (Get-Item -Path $destinationFile).LastWriteTime) {
            Copy-Item -Path $sourceFile.FullName -Destination $destinationFile -Force
            $filesCopied = $true
        }
    }

    return $filesCopied
}


# Check if the source folder exists
if (-not (Test-Path -Path $SourceFolderPath -PathType Container)) {
    throw "The source folder path is not valid or does not exist."
}

# Get the OneDrive root folder path
$OneDriveFolderPath = $env:OneDrive
$DestinationFolderPath = Join-Path -Path $OneDriveFolderPath -ChildPath $DestinationFolderName

# Check if the destination folder exists in OneDrive root directory, if not, create it
if (-not (Test-Path -Path $DestinationFolderPath -PathType Container)) {
    New-Item -ItemType Directory -Path $DestinationFolderPath -Force | Out-Null
}

# Copy changed or new files to the destination folder
$filesCopied = Copy-NewOrChangedFiles -Source $SourceFolderPath -Destination $DestinationFolderPath

if ($filesCopied) {
    Write-Host "Backup completed successfully. The backup is located at: $DestinationFolderPath"
} else {
    Write-Host "No new or changed files found. No backup created."
}
