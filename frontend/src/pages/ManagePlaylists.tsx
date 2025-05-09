import { Link } from 'react-router';
import { Edit, Trash2, ExternalLink } from 'lucide-react';

type Playlist = {
  id: string;
  name: string;
  trackCount: number;
  createdAt: string;
};

export default function ManagePlaylists() {
  const playlists: Playlist[] = [
    // Placeholder
  ];

  return (
    <div className='mx-auto max-w-4xl'>
      <div className='mb-6 flex items-center justify-between'>
        <h1 className='text-3xl font-bold'>My Playlists</h1>
        <Link
          to='/create'
          className='neu-button'
        >
          Create New Playlist
        </Link>
      </div>

      {playlists.length === 0 ?
        <div className='neu-card py-10 text-center'>
          <h3 className='text-2xl font-semibold'>Coming Soon!</h3>
        </div>
      : <div className='grid gap-4'>
          {playlists.map(playlist => (
            <div
              key={playlist.id}
              className='neu-card'
            >
              <div className='flex items-start justify-between'>
                <div>
                  <h2 className='text-xl font-semibold'>{playlist.name}</h2>
                  <p className='text-muted-foreground'>
                    {playlist.trackCount} tracks · Created on{' '}
                    {playlist.createdAt}
                  </p>
                </div>
                <div className='flex gap-2'>
                  <Link
                    to={`/playlists/${playlist.id}`}
                    className='neu-button'
                    aria-label='View playlist'
                  >
                    <ExternalLink size={18} />
                  </Link>
                  <button
                    className='neu-button'
                    aria-label='Edit playlist'
                  >
                    <Edit size={18} />
                  </button>
                  <button
                    className='neu-button'
                    aria-label='Delete playlist'
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      }
    </div>
  );
}
