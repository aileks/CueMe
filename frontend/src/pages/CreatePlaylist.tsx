import { useState, type FormEvent } from 'react';
import { PlusCircle, X } from 'lucide-react';

export default function CreatePlaylist() {
  const [playlistName, setPlaylistName] = useState('');
  const [selectedGenres, setSelectedGenres] = useState<string[]>([]);
  const [artistInput, setArtistInput] = useState('');
  const [artists, setArtists] = useState<string[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [playlistGenerated, setPlaylistGenerated] = useState(false);

  // Placeholder genre list - would come from an API in a real app
  const availableGenres = [
    'Rock',
    'Pop',
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

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsGenerating(true);

    // Simulate API call
    setTimeout(() => {
      setIsGenerating(false);
      setPlaylistGenerated(true);
    }, 2000);
  };

  return (
    <div className='mx-auto max-w-3xl'>
      <h1 className='mb-6 text-3xl font-bold'>Create New Playlist</h1>

      {playlistGenerated ?
        <div className='neu-card'>
          <h2 className='mb-4 text-2xl font-semibold'>Playlist Generated!</h2>
          <p className='mb-6'>Your playlist has been created successfully.</p>

          <div className='mb-6 rounded-md bg-secondary/20 px-4 py-4'>
            <p className='mb-4 text-lg font-medium'>
              This feature is coming soon!
            </p>
            <p>
              In the future, you'll see your generated playlist here with
              options to edit, save, or export it.
            </p>
          </div>

          <div className='flex gap-4'>
            <button
              className='neu-button'
              onClick={() => {
                setPlaylistGenerated(false);
                setSelectedGenres([]);
                setArtists([]);
                setPlaylistName('');
              }}
            >
              Create Another
            </button>
            <button className='neu-button'>Save Playlist</button>
          </div>
        </div>
      : <form onSubmit={handleSubmit}>
          <div className='mb-6 neu-card'>
            <h2 className='mb-4 text-2xl font-semibold'>Playlist Details</h2>

            <div className='mb-4'>
              <label
                htmlFor='playlistName'
                className='mb-2 block font-medium'
              >
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
            <div className='flex flex-wrap gap-3'>
              {availableGenres.map(genre => (
                <button
                  key={genre}
                  type='button'
                  className={`neu-tag ${
                    selectedGenres.includes(genre) ?
                      'bg-primary text-primary-foreground'
                    : ''
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
                placeholder='Artist name'
              />
              <button
                type='button'
                className='ml-2 neu-button'
                onClick={addArtist}
              >
                <PlusCircle size={20} />
              </button>
            </div>

            {artists.length > 0 && (
              <div className='mb-4 flex flex-wrap gap-2'>
                {artists.map(artist => (
                  <div
                    key={artist}
                    className='neu-tag flex items-center gap-2'
                  >
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

          <button
            type='submit'
            className='neu-button'
            disabled={
              isGenerating ||
              (!selectedGenres.length && !artists.length) ||
              !playlistName
            }
          >
            {isGenerating ? 'Generating...' : 'Generate Playlist'}
          </button>
        </form>
      }
    </div>
  );
}
