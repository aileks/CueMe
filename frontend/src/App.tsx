import { useEffect } from 'react';
import { useAuth } from './hooks/useAuth';
import Router from './router';

function App() {
  const { checkAuth } = useAuth();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  return (
    <div className='min-h-screen bg-background text-foreground transition-colors duration-200'>
      <Router />
    </div>
  );
}

export default App;
