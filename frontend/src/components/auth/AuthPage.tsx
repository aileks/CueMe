import { useState } from 'react';
import { Navigate } from 'react-router';
import LoginForm from './LoginForm';
import RegistrationForm from './RegistrationForm';
import ThemeToggle from '../ui/ThemeToggle';
import { useAuth } from '../../hooks/useAuth';

export default function AuthPage() {
  const [showLogin, setShowLogin] = useState(true);
  const { isAuthenticated } = useAuth();

  if (isAuthenticated) {
    return (
      <Navigate
        to='/'
        replace
      />
    );
  }

  return (
    <div className='container mx-auto px-4 py-8'>
      <div className='mx-auto max-w-md'>
        <div className='relative mb-8 text-center'>
          <div className='absolute top-0 right-0'>
            <ThemeToggle />
          </div>
          <h1 className='mb-2 text-4xl font-bold'>QueMe</h1>

          <p className='text-muted-foreground'>
            Create your next music fixation.
          </p>
        </div>

        {showLogin ?
          <LoginForm onSwitchToRegister={() => setShowLogin(false)} />
        : <RegistrationForm onSwitchToLogin={() => setShowLogin(true)} />}
      </div>
    </div>
  );
}
