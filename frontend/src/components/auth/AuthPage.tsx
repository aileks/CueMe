import { useState } from 'react';
import LoginForm from './LoginForm';
import RegistrationForm from './RegistrationForm';

export default function AuthPage() {
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
            onSwitchToRegister={() => setShowLogin(false)}
          />
        : <RegistrationForm
            onSwitchToLogin={() => setShowLogin(true)}
          />
        }
      </div>
    </div>
  );
}
