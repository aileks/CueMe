import { useParams, Link } from 'react-router';
import { ArrowLeft, Edit, Share2, RotateCw } from 'lucide-react';

export default function PlaylistDetail() {
  const { id } = useParams();

  return (
    <div className='mx-auto max-w-4xl'>
      <div className='mb-6'>
        <Link
          to='/playlists'
          className='inline-flex neu-button items-center gap-2'
        >
          <ArrowLeft size={16} />
          Back to Playlists
        </Link>
      </div>

      <div className='mb-6 neu-card'>
        <div className='flex items-start justify-between'>
          <div>
            <h1 className='mb-2 text-3xl font-bold'>Playlist #{id}</h1>
            <p className='text-muted-foreground'>Created on May 5, 2025</p>
          </div>
          <div className='flex gap-2'>
            <button className='flex neu-button items-center gap-1'>
              <Edit size={16} />
              Edit
            </button>
            <button className='flex neu-button items-center gap-1'>
              <Share2 size={16} />
              Export
            </button>
            <button className='flex neu-button items-center gap-1'>
              <RotateCw size={16} />
              Regenerate
            </button>
          </div>
        </div>
      </div>

      <div className='mb-6 neu-card'>
        <h2 className='mb-4 text-2xl font-semibold'>Playlist Details</h2>
        <p className='py-8 text-center text-muted-foreground'>
          This playlist is coming soon!
        </p>
        <p className='text-center text-primary'>Feature under development</p>
      </div>

      <div className='neu-card'>
        <h2 className='mb-4 text-2xl font-semibold'>Tracks</h2>
        <div className='py-8 text-center text-muted-foreground'>
          <p className='mb-2'>Tracks will appear here once implemented</p>
          <p>Coming Soon!</p>
        </div>
      </div>
    </div>
  );
}
