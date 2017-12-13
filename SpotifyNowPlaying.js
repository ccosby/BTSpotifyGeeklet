#!/usr/bin/env osascript -l JavaScript

function run(argv) {
    var Spotify = Application("Spotify");

    var data = { running: false };

    if (!Spotify.running()) {
        return JSON.stringify(data);
    }

    data.spotify_version = Spotify.version();

    if (Spotify.playerState() in {"playing": 1, "paused": 1}) {
        var track = Spotify.currentTrack();
        data.running = true;
        data.name = track.name();
        data.artist = track.artist();
        data.album = track.album();
        data.artwork_url = track.artworkUrl();
        data.player_position = Spotify.playerPosition();
        data.duration = track.duration();
    }

    return JSON.stringify(data);
}