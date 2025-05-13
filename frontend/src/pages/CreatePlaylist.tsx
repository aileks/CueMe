import { useState, useEffect, type FormEvent } from 'react';
import { PlusCircle, X, Music2, Loader2, Sliders } from 'lucide-react';

export default function CreatePlaylist() {
  const [playlistName, setPlaylistName] = useState('');
  const availableGenres = [
    'Rock',
    'Pop',
    'Punk',
    'Hip-Hop',
    'R&B',
    'Jazz',
    'Electronic',
    'Classical',
    'Country',
    'Folk',
    'Metal',
    'Indie',
  ];

  const [selectedGenres, setSelectedGenres] = useState<string[]>([]);
  const [artistInput, setArtistInput] = useState('');
  const [artists, setArtists] = useState<string[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [playlistGenerated, setPlaylistGenerated] = useState(false);
  const [generatedPlaylist, setGeneratedPlaylist] = useState<any>(null);
  const [error, setError] = useState('');

  // Audio features state
  const [availableFeatures, setAvailableFeatures] = useState<any>({});
  const [showFeatures, setShowFeatures] = useState(false);
  const [featurePreferences, setFeaturePreferences] = useState<Record<string, number>>({});

  // Only fetch audio features on component mount
  useEffect(() => {
    fetchAudioFeatures();
  }, []);

  const fetchAudioFeatures = async () => {
    try {
      const res = await fetch('/api/playlists/features');

      if (!res.ok) {
        throw new Error(`Features fetch failed: ${res.statusText}`);
      }

      const data = await res.json();
      setAvailableFeatures(data.features || {});
    } catch (err) {
      console.error('Error fetching audio features:', err);
    }
  };

  const handleGenreToggle = (genre: string) => {
    if (selectedGenres.includes(genre)) {
      setSelectedGenres(selectedGenres.filter(g => g !== genre));
    } else {
      setSelectedGenres([...selectedGenres, genre]);
    }
  };

  const addArtist = () => {
    if (artistInput.trim() && !artists.includes(artistInput)) {
      setArtists([...artists, artistInput.trim()]);
      setArtistInput('');
    }
  };

  const removeArtist = (artist: string) => {
    setArtists(artists.filter(a => a !== artist));
  };

  const handleFeatureChange = (feature: string, value: number) => {
    setFeaturePreferences({
      ...featurePreferences,
      [feature]: value,
    });
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addArtist();
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    if (!playlistName) {
      setError('Please enter a playlist name');
      return;
    }

    if (
      selectedGenres.length === 0 &&
      artists.length === 0 &&
      Object.keys(featurePreferences).length === 0
    ) {
      setError('Please select at least one genre, artist, or audio feature');
      return;
    }

    try {
      setIsGenerating(true);
      setError('');

      const res = await fetch('/api/playlists/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: playlistName,
          genres: selectedGenres.map(g => g.toLowerCase()), // Convert genres to lowercase for the API
          artists: artists,
          features: featurePreferences,
          trackCount: 50,
        }),
      });

      if (!res.ok) {
        throw new Error(`Failed to generate playlist: ${res.statusText}`);
      }

      const playlist = await res.json();
      setGeneratedPlaylist(playlist);
      setPlaylistGenerated(true);
    } catch (err) {
      console.error('Error generating playlist:', err);
      setError('Failed to generate playlist. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const savePlaylist = async () => {
    if (!generatedPlaylist) return;

    try {
      const res = await fetch('/api/playlists/playlist/save', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(generatedPlaylist),
      });

      if (!res.ok) {
        throw new Error('Failed to save playlist');
      }

      const data = await res.json();
      alert('Playlist saved successfully!');
      console.log('Saved playlist:', data);
    } catch (err) {
      console.error('Error saving playlist:', err);
      alert('Failed to save playlist. Please try again.');
    }
  };

  const resetForm = () => {
    setPlaylistGenerated(false);
    setSelectedGenres([]);
    setArtists([]);
    setPlaylistName('My New Playlist');
    setGeneratedPlaylist(null);
    setFeaturePreferences({});
  };

  // Render audio feature controls
  const renderFeatureControls = () => {
    return (
      <div className='mb-6 neu-card'>
        <div className='mb-4 flex items-center justify-between'>
          <h2 className='text-2xl font-semibold'>Audio Features</h2>
          <button
            type='button'
            className='flex neu-button items-center gap-2'
            onClick={() => setShowFeatures(!showFeatures)}
          >
            <Sliders className='h-5 w-5' />
            {showFeatures ? 'Hide Features' : 'Show Features'}
          </button>
        </div>

        {showFeatures && (
          <div className='grid gap-4 md:grid-cols-2'>
            {Object.entries(availableFeatures).map(([feature, info]: [string, any]) => (
              <div key={feature} className='mb-2'>
                <label className='mb-1 block font-medium'>
                  {feature.charAt(0).toUpperCase() + feature.slice(1)}
                  {featurePreferences[feature] !== undefined &&
                    `: ${featurePreferences[feature].toFixed(2)}`}
                </label>
                <input
                  type='range'
                  min={info.min}
                  max={info.max}
                  step={(info.max - info.min) / 100}
                  value={featurePreferences[feature] || info.mean}
                  onChange={e => handleFeatureChange(feature, parseFloat(e.target.value))}
                  className='h-2 w-full cursor-pointer appearance-none rounded-lg bg-muted'
                />
                <div className='mt-1 flex justify-between text-xs text-muted-foreground'>
                  <span>Low</span>
                  <span>High</span>
                </div>
                {info.description && (
                  <p className='mt-1 text-xs text-muted-foreground'>{info.description}</p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className='mx-auto max-w-3xl'>
      <h1 className='mb-6 text-3xl font-bold'>Create New Playlist</h1>

      {error && <div className='mb-4 bg-destructive p-3 text-destructive-foreground'>{error}</div>}

      {playlistGenerated ?
        <div className='neu-card'>
          <h2 className='mb-4 text-2xl font-semibold'>Playlist Generated!</h2>

          <div className='mb-4'>
            <h3 className='mb-2 text-xl font-medium'>{generatedPlaylist.playlist_name}</h3>

            {generatedPlaylist.genres.length > 0 && (
              <div className='mb-2'>
                <h4 className='mb-1 text-sm font-medium text-muted-foreground'>Genres:</h4>
                <div className='flex flex-wrap gap-2'>
                  {generatedPlaylist.genres.map((genre: string) => (
                    <span key={genre} className='neu-tag'>
                      {genre}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {generatedPlaylist.artists.length > 0 && (
              <div>
                <h4 className='mb-1 text-sm font-medium text-muted-foreground'>Artists:</h4>
                <div className='flex flex-wrap gap-2'>
                  {generatedPlaylist.artists.map((artist: string) => (
                    <span key={artist} className='neu-tag flex items-center gap-1'>
                      <Music2 size={14} />
                      {artist}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {generatedPlaylist.tracks.length > 0 ?
            <div className='mb-6 max-h-96 overflow-auto'>
              <h3 className='mb-2 text-lg font-medium'>Tracks</h3>
              <div className='border-border-color border-t'>
                {generatedPlaylist.tracks.map((track: any, index: number) => (
                  <div
                    key={track.id || index}
                    className='border-border-color flex justify-between border-b px-2 py-3'
                  >
                    <div>
                      <p className='font-medium'>{track.title}</p>
                      <p className='text-sm text-muted-foreground'>{track.artist}</p>
                    </div>
                    <div className='text-right text-sm text-muted-foreground'>{track.album}</div>
                  </div>
                ))}
              </div>
            </div>
          : <div className='mb-6 bg-muted p-4 text-center'>
              <p>No tracks found matching your criteria. Try different genres or artists.</p>
            </div>
          }

          <div className='flex gap-4'>
            <button className='neu-button' onClick={resetForm}>
              Create Another
            </button>

            <button className='neu-button' onClick={savePlaylist}>
              Save Playlist
            </button>
          </div>
        </div>
      : <form onSubmit={handleSubmit}>
          <div className='mb-6 neu-card'>
            <h2 className='mb-4 text-2xl font-semibold'>Playlist Details</h2>

            <div className='mb-4'>
              <label htmlFor='playlistName' className='mb-2 block font-medium'>
                Playlist Name
              </label>

              <input
                id='playlistName'
                type='text'
                className='neu-input w-full'
                value={playlistName}
                onChange={e => setPlaylistName(e.target.value)}
                placeholder='My Awesome Playlist'
                required
              />
            </div>
          </div>

          <div className='mb-6 neu-card'>
            <h2 className='mb-4 text-2xl font-semibold'>Select Genres</h2>

            {/* Using hardcoded genres directly */}
            <div className='flex flex-wrap gap-3'>
              {availableGenres.map(genre => (
                <button
                  key={genre}
                  type='button'
                  className={`neu-tag cursor-pointer transition-colors duration-200 ${
                    selectedGenres.includes(genre) ? 'bg-primary text-primary-foreground' : ''
                  }`}
                  onClick={() => handleGenreToggle(genre)}
                >
                  {genre}
                </button>
              ))}
            </div>
          </div>

          <div className='mb-6 neu-card'>
            <h2 className='mb-4 text-2xl font-semibold'>Add Artists</h2>

            <div className='mb-4 flex'>
              <input
                type='text'
                className='neu-input flex-grow'
                value={artistInput}
                onChange={e => setArtistInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder='Artist name'
              />

              <button type='button' className='ml-2 neu-button' onClick={addArtist}>
                <PlusCircle size={20} />
              </button>
            </div>

            {artists.length > 0 && (
              <div className='mb-4 flex flex-wrap gap-2'>
                {artists.map(artist => (
                  <div key={artist} className='neu-tag flex items-center gap-2'>
                    {artist}
                    <button
                      type='button'
                      className='text-muted-foreground hover:text-destructive'
                      onClick={() => removeArtist(artist)}
                    >
                      <X size={16} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Audio Features Section */}
          {Object.keys(availableFeatures).length > 0 && renderFeatureControls()}

          <button
            type='submit'
            className='neu-button'
            disabled={
              isGenerating ||
              (!selectedGenres.length &&
                !artists.length &&
                Object.keys(featurePreferences).length === 0) ||
              !playlistName
            }
          >
            {isGenerating ?
              <>
                <Loader2 className='mr-2 h-4 w-4 animate-spin' />
                Generating...
              </>
            : 'Generate Playlist'}
          </button>
        </form>
      }
    </div>
  );
}
