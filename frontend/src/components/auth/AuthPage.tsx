import { useState } from 'react';
import LoginForm from './LoginForm';
import RegistrationForm from './RegistrationForm';

type User = {
  id: string;
  email: string;
  username: string;
};

interface AuthPageProps {
  onAuthenticated: (user: User) => void;
}

export default function AuthPage({ onAuthenticated }: AuthPageProps) {
  const [showLogin, setShowLogin] = useState(true);

  return (
    <div className='container mx-auto px-4 py-8'>
      <div className='mx-auto max-w-md'>
        <div className='mb-8 text-center'>
          <h1 className='mb-2 text-4xl font-bold'>QueMe</h1>

          <p className='text-muted-foreground'>
            Create your next music fixation.
          </p>
        </div>

        {showLogin ?
          <LoginForm
            onSuccess={onAuthenticated}
            onSwitchToRegister={() => setShowLogin(false)}
          />
        : <RegistrationForm
            onSuccess={onAuthenticated}
            onSwitchToLogin={() => setShowLogin(true)}
          />
        }
      </div>
    </div>
  );
}
