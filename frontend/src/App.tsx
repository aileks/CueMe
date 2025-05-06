import AuthPage from './components/auth/AuthPage';
import { AuthProvider, useAuth } from './context/AuthContext';

const Dashboard = () => {
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
  };

  return (
    <div className='container mx-auto p-6'>
      <header className='flex justify-between items-center mb-8'>
        <h1 className='text-4xl font-bold'>CueMe</h1>

        <div className='flex items-center gap-4'>
          <span>Welcome, {user?.username}!</span>

          <button
            onClick={handleLogout}
            className='neu-button'
          >
            Log Out
          </button>
        </div>
      </header>

      <div className='neu-card mb-8'>
        <h2 className='text-2xl font-bold mb-4'>Your Dashboard</h2>

        <p className='mb-4'>
          Welcome to CueMe, your personal music playlist generator. Start
          creating playlists based on your preferences!
        </p>

        <button className='neu-button'>Create New Playlist</button>
      </div>

      <div className='grid grid-cols-1 md:grid-cols-2 gap-6'>
        <div className='neu-card'>
          <h3 className='text-xl font-bold mb-3'>Recent Playlists</h3>

          <p className='text-muted-foreground'>
            You haven't created any playlists yet. Get started by clicking the
            button above!
          </p>
        </div>

        <div className='neu-card'>
          <h3 className='text-xl font-bold mb-3'>Surprise Me</h3>

          <p className='text-muted-foreground'>
            Create your first playlist to get personalized randomizations.
          </p>
        </div>
      </div>
    </div>
  );
};

const AppContent = () => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className='h-screen flex items-center justify-center'>
        <div className='neu-box p-6'>
          <p className='text-xl'>Loading...</p>
        </div>
      </div>
    );
  }

  return user ?
      <Dashboard />
    : <AuthPage
        onAuthenticated={userData => console.log('Authenticated:', userData)}
      />;
};

function App() {
  return (
    <AuthProvider>
      <div className='min-h-screen bg-background text-foreground'>
        <AppContent />
      </div>
    </AuthProvider>
  );
}

export default App;
