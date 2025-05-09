import { Link } from 'react-router';
import { PlusCircle, Music2, Sparkles, Clock } from 'lucide-react';

export default function Dashboard() {
  return (
    <div>
      <div className='mb-8 neu-card'>
        <h2 className='mb-4 flex items-center gap-2 text-2xl font-bold'>
          <Sparkles className='h-6 w-6 text-accent' />
          Home
        </h2>

        <p className='mb-4'>
          Welcome to QueMe, your personal music playlist generator. Start
          creating playlists based on your preferences!
        </p>

        <Link
          to='/create'
          className='inline-flex neu-button items-center gap-2 focus:outline-0'
        >
          <PlusCircle className='h-5 w-5' />
          Create New Playlist
        </Link>
      </div>

      <div className='grid grid-cols-1 gap-6 md:grid-cols-2'>
        <div className='neu-card'>
          <h3 className='mb-3 flex items-center gap-2 text-xl font-bold'>
            <Clock className='h-5 w-5 text-accent' />
            Recent Playlists
          </h3>

          <p className='text-muted-foreground'>
            You haven't created any playlists yet. Get started by clicking the
            button above!
          </p>
        </div>

        <div className='neu-card'>
          <h3 className='mb-3 flex items-center gap-2 text-xl font-bold'>
            <Music2 className='h-5 w-5 text-accent' />
            Surprise Me
          </h3>

          <div className='py-2 text-center text-lg font-medium text-amber-600'>
            Coming Soon!
          </div>
        </div>
      </div>
    </div>
  );
}
