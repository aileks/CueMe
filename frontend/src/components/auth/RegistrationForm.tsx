import { useState, type FormEvent } from 'react';
import { useAuth } from '../../hooks/useAuth';

interface RegistrationFormProps {
  onSwitchToLogin: () => void;
}

export default function RegistrationForm({
  onSwitchToLogin,
}: RegistrationFormProps) {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [passwordConfirmation, setPasswordConfirmation] = useState('');
  const [errors, setErrors] = useState<Record<string, string[]>>({});
  const [isLoading, setIsLoading] = useState(false);

  const { login } = useAuth();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrors({});

    if (password !== passwordConfirmation) {
      setErrors({
        passwordConfirmation: ['Passwords do not match.'],
      });
      setIsLoading(false);
      return;
    }

    try {
      const res = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ username, email, password }),
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
      <div className='neu-card my-8'>
        <h2 className='mb-6 text-3xl font-bold'>Create Account</h2>

        {errors.message && (
          <div className='mb-4 bg-destructive p-3 text-destructive-foreground'>
            {errors.message.map((error, i) => (
              <p key={i}>{error}</p>
            ))}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className='mb-4'>
            <label
              htmlFor='username'
              className='mb-2 block font-medium'
            >
              Username
            </label>

            <input
              id='username'
              type='text'
              className='neu-input w-full'
              value={username}
              onChange={e => setUsername(e.target.value)}
              required
            />
            {errors.username && (
              <p className='mt-1 text-destructive'>{errors.username[0]}</p>
            )}
          </div>

          <div className='mb-4'>
            <label
              htmlFor='email'
              className='mb-2 block font-medium'
            >
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

          <div className='mb-4'>
            <label
              htmlFor='password'
              className='mb-2 block font-medium'
            >
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

          <div className='mb-6'>
            <label
              htmlFor='passwordConfirmation'
              className='mb-2 block font-medium'
            >
              Confirm Password
            </label>

            <input
              id='passwordConfirmation'
              type='password'
              className='neu-input w-full'
              value={passwordConfirmation}
              onChange={e => setPasswordConfirmation(e.target.value)}
              required
            />
            {errors.passwordConfirmation && (
              <p className='mt-1 text-destructive'>
                {errors.passwordConfirmation[0]}
              </p>
            )}
          </div>

          <button
            type='submit'
            className='neu-button mb-4 w-full font-bold'
            disabled={isLoading}
          >
            {isLoading ? 'Creating Account...' : 'Register'}
          </button>

          <p className='mt-4 text-center'>
            Already have an account?{' '}
            <button
              type='button'
              className='font-medium text-primary underline'
              onClick={onSwitchToLogin}
            >
              Log In
            </button>
          </p>
        </form>
      </div>
    </div>
  );
}
