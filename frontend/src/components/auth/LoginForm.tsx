import { useState, type FormEvent } from 'react';
import { useAuth } from '../../hooks/useAuth';

interface LoginFormProps {
  onSwitchToRegister: () => void;
}

export default function LoginForm({ onSwitchToRegister }: LoginFormProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<Record<string, string[]>>({});
  const [isLoading, setIsLoading] = useState(false);

  const { login } = useAuth();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrors({});

    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        setErrors(data);
        return;
      }

      login(data);
    } catch (_err) {
      setErrors({
        message: ['An unexpected error occurred. Please try again.'],
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className='mx-auto w-full max-w-md'>
      <div className='my-8 neu-card'>
        <h2 className='mb-6 text-3xl font-bold'>Log In</h2>

        {errors.message && (
          <div className='mb-4 bg-destructive p-3 text-destructive-foreground'>
            {errors.message.map((error, i) => (
              <p key={i}>{error}</p>
            ))}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className='mb-4'>
            <label htmlFor='email' className='mb-2 block font-medium'>
              Email
            </label>

            <input
              id='email'
              type='email'
              className='neu-input w-full'
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
            />

            {errors.email && (
              <p className='mt-1 text-destructive'>{errors.email[0]}</p>
            )}
          </div>

          <div className='mb-6'>
            <label htmlFor='password' className='mb-2 block font-medium'>
              Password
            </label>

            <input
              id='password'
              type='password'
              className='neu-input w-full'
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
            />

            {errors.password && (
              <p className='mt-1 text-destructive'>{errors.password[0]}</p>
            )}
          </div>

          <button
            type='submit'
            className='mb-4 w-full neu-button font-bold'
            disabled={isLoading}
          >
            {isLoading ? 'Logging in...' : 'Log In'}
          </button>

          <p className='mt-4 text-center'>
            Don't have an account?{' '}
            <button
              type='button'
              className='cursor-pointer font-medium text-primary underline underline-offset-2 transition-colors duration-200 hover:text-primary/80'
              onClick={onSwitchToRegister}
            >
              Register
            </button>
          </p>
        </form>
      </div>
    </div>
  );
}
