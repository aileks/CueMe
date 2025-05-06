import { useState, type FormEvent } from 'react';

type User = {
  id: string;
  email: string;
  username: string;
};

interface RegistrationFormProps {
  onSuccess: (user: User) => void;
  onSwitchToLogin: () => void;
}

export default function RegistrationForm({
  onSuccess,
  onSwitchToLogin,
}: RegistrationFormProps) {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<Record<string, string[]>>({});
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrors({});

    try {
      const res = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        setErrors(data);
        return;
      }

      onSuccess(data);
    } catch (_err) {
      setErrors({
        message: ['An unexpected error occurred. Please try again.'],
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className='w-full max-w-md mx-auto'>
      <div className='neu-card my-8'>
        <h2 className='text-3xl font-bold mb-6'>Create Account</h2>

        {errors.message && (
          <div className='mb-4 p-3 bg-destructive text-destructive-foreground'>
            {errors.message.map((error, i) => (
              <p key={i}>{error}</p>
            ))}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className='mb-4'>
            <label
              htmlFor='username'
              className='block mb-2 font-medium'
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
              className='block mb-2 font-medium'
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

          <div className='mb-6'>
            <label
              htmlFor='password'
              className='block mb-2 font-medium'
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

          <button
            type='submit'
            className='neu-button w-full mb-4 font-bold'
            disabled={isLoading}
          >
            {isLoading ? 'Creating Account...' : 'Register'}
          </button>

          <p className='text-center mt-4'>
            Already have an account?{' '}
            <button
              type='button'
              className='text-primary font-medium underline'
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
