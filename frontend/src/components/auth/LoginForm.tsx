import { useState, FormEvent } from 'react';

interface LoginFormProps {
  onSuccess: (user: any) => void;
  onSwitchToRegister: () => void;
}

export default function LoginForm({
  onSuccess,
  onSwitchToRegister,
}: LoginFormProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<Record<string, string[]>>({});
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrors({});

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        setErrors(data);
        return;
      }

      // Success - call the success handler with user data
      onSuccess(data);
    } catch (error) {
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
        <h2 className='text-3xl font-bold mb-6'>Log In</h2>

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
            {isLoading ? 'Logging in...' : 'Log In'}
          </button>

          <p className='text-center mt-4'>
            Don't have an account?
            <button
              type='button'
              className='text-primary font-medium underline'
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
