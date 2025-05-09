import { Link } from 'react-router';

export default function Dashboard() {
  return (
    <div>
      <div className='mb-8 neu-card'>
        <h2 className='mb-4 text-2xl font-bold'>Your Dashboard</h2>

        <p className='mb-4'>
          Welcome to QueMe, your personal music playlist generator. Start
          creating playlists based on your preferences!
        </p>

        <Link
          to='/create'
          className='inline-block neu-button focus:outline-0'
        >
          Create New Playlist
        </Link>
      </div>

      <div className='grid grid-cols-1 gap-6 md:grid-cols-2'>
        <div className='neu-card'>
          <h3 className='mb-3 text-xl font-bold'>Recent Playlists</h3>

          <p className='text-muted-foreground'>
            You haven't created any playlists yet. Get started by clicking the
            button above!
          </p>
        </div>

        <div className='neu-card'>
          <h3 className='mb-3 text-xl font-bold'>Surprise Me</h3>

          <div className='py-2 text-center text-lg text-primary'>
            Coming Soon!
          </div>
        </div>
      </div>
    </div>
  );
}
