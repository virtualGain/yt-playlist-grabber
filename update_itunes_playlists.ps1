param(
    [string]$directoryPath
)

if ($directoryPath -eq $null) {
    $directoryPath = "C:\Music\ytpg"
}
$doNotTouchFolders = @()
function AddSongsToPlaylist($playlist, $folder) {
    $songFiles = Get-ChildItem -Path $folder.FullName -Include *.mp3, *.m4a -Recurse -File

    foreach ($songFile in $songFiles) {
        $existingTrack = $playlist.Tracks | Where-Object { $_.Location -eq $songFile.FullName }

        if ($existingTrack -eq $null) {
            write-host "adding song to playlist: " + $songFile.FullName
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
    #check to see if this is in the nono Folder list
    if (-not ($doNotTouchFolders | ForEach-Object { $folder.Name.Contains($_) })) {
        
        $playlist = $itunes.LibrarySource.Playlists | Where-Object { $_.Name -eq ("ytpg_" + $folder.Name) }

        if ($playlist -eq $null) {
            Write-Host "Creating playlist from folder " + $folder.Name
            $playlist = $itunes.CreatePlaylist("ytpg_" + $folder.Name)
        }
        Write-Host "Adding songs to playlist from folder " + $folder.Name
        AddSongsToPlaylist $playlist $folder
    }
}
