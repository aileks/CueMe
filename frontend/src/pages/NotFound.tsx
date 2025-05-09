import { Link } from 'react-router';
import { Home } from 'lucide-react';

export default function NotFound() {
  return (
    <div className='flex h-screen items-center justify-center'>
      <div className='mx-auto max-w-md neu-card text-center'>
        <h1 className='mb-4 text-6xl font-bold'>404</h1>
        <h2 className='mb-4 text-2xl font-semibold'>Page Not Found</h2>
        <p className='mb-6'>
          The page you're looking for doesn't exist or has been moved.
        </p>
        <Link to='/' className='inline-flex neu-button items-center gap-2'>
          <Home size={18} />
          Return Home
        </Link>
      </div>
    </div>
  );
}
