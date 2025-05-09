import {
  createBrowserRouter,
  Outlet,
  RouterProvider,
  Navigate,
} from 'react-router';
import { useAuth } from './hooks/useAuth';
import AuthPage from './components/auth/AuthPage';
import Dashboard from './pages/Dashboard';
import UserProfile from './pages/UserProfile';
import CreatePlaylist from './pages/CreatePlaylist';
import ManagePlaylists from './pages/ManagePlaylists';
import PlaylistDetail from './pages/PlaylistDetail';
import NotFound from './pages/NotFound';
import NavLink from './components/ui/NavLink';
import ThemeToggle from './components/ui/ThemeToggle';
import { Suspense } from 'react';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className='flex h-screen items-center justify-center'>
        <div className='neu-box p-6'>
          <p className='text-xl'>Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <Navigate
        to='/auth'
        replace
      />
    );
  }

  return <>{children}</>;
};

const AppLayout = () => {
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
  };

  return (
    <div className='container mx-auto p-6'>
      <header className='mb-8 flex items-center justify-between'>
        <h1 className='text-4xl font-bold'>QueMe</h1>

        <nav className='hidden items-center gap-6 md:flex'>
          <NavLink
            to='/'
            exact
          >
            Dashboard
          </NavLink>
          <NavLink to='/playlists'>My Playlists</NavLink>
          <NavLink to='/create'>Create Playlist</NavLink>
          <NavLink to='/profile'>Profile</NavLink>
        </nav>

        <div className='flex items-center gap-4'>
          <h4 className='text-xl'>Welcome, {user?.username}!</h4>
          <ThemeToggle className='mr-2' />
          <button
            onClick={handleLogout}
            className='neu-button'
          >
            Log Out
          </button>
        </div>
      </header>

      <main>
        <Suspense
          fallback={
            <div className='flex h-64 items-center justify-center'>
              <div className='neu-box p-6'>
                <p className='text-xl'>Loading...</p>
              </div>
            </div>
          }
        >
          <Outlet />
        </Suspense>
      </main>
    </div>
  );
};

// Router configuration
const router = createBrowserRouter([
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <AppLayout />
      </ProtectedRoute>
    ),
    children: [
      {
        index: true,
        element: <Dashboard />,
      },
      {
        path: 'profile',
        element: <UserProfile />,
      },
      {
        path: 'create',
        element: <CreatePlaylist />,
      },
      {
        path: 'playlists',
        element: <ManagePlaylists />,
      },
      {
        path: 'playlists/:id',
        element: <PlaylistDetail />,
      },
    ],
  },
  {
    path: '/auth',
    element: <AuthPage />,
  },
  {
    path: '*',
    element: <NotFound />,
  },
]);

export default function Router() {
  return <RouterProvider router={router} />;
}
