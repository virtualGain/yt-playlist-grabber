param(
    [string]$directoryPath
)

function AddSongsToPlaylist($playlist, $folder) {
    $songFiles = Get-ChildItem -Path $folder.FullName -Include *.mp3, *.m4a -Recurse -File

    foreach ($songFile in $songFiles) {
        $existingTrack = $playlist.Tracks | Where-Object { $_.Location -eq $songFile.FullName }

        if ($existingTrack -eq $null) {
            $playlist.AddFile($songFile.FullName) | Out-Null
        }
    }
}

if (-not (Test-Path $directoryPath)) {
    Write-Error "The specified directory path does not exist."
    exit 1
}

$itunes = New-Object -ComObject iTunes.Application
$folders = Get-ChildItem -Path $directoryPath -Directory

foreach ($folder in $folders) {
    $playlist = $itunes.LibrarySource.Playlists | Where-Object { $_.Name -eq ("ytpg_" + $folder.Name) }

    if ($playlist -eq $null) {
        $playlist = $itunes.CreatePlaylist("ytpg_" + $folder.Name)
    }

    AddSongsToPlaylist $playlist $folder
}
