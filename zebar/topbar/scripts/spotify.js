// `running()` is checked first because any other call launches Spotify.
function run(argv) {
  const spotify = Application('Spotify');
  if (!spotify.running()) return JSON.stringify({ running: false });

  switch (argv[0]) {
    case 'playpause':
      spotify.playpause();
      break;
    case 'next':
      spotify.nextTrack();
      break;
    case 'previous':
      spotify.previousTrack();
      break;
    case 'shuffle':
      spotify.shuffling = !spotify.shuffling();
      break;
    case 'repeat':
      spotify.repeating = !spotify.repeating();
      break;
    case 'seek':
      spotify.playerPosition = Number(argv[1]);
      break;
  }

  const state = {
    running: true,
    state: spotify.playerState(),
    shuffling: spotify.shuffling(),
    repeating: spotify.repeating(),
    position: spotify.playerPosition(),
  };
  try {
    const track = spotify.currentTrack;
    Object.assign(state, {
      name: track.name(),
      artist: track.artist(),
      album: track.album(),
      artwork: track.artworkUrl(),
      duration: track.duration() / 1000,
    });
  } catch {
    // Spotify has no current track until something is played.
  }
  return JSON.stringify(state);
}
