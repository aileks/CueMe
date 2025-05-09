import { useState, type FormEvent } from 'react';
import { useAuth } from '../hooks/useAuth';

export default function UserProfile() {
  const { user } = useAuth();
  const [username, setUsername] = useState(user?.username || '');
  const [email, setEmail] = useState(user?.email || '');
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [errors, setErrors] = useState<Record<string, string[]>>({});
  const [isLoading, setIsLoading] = useState(false);

  const handleProfileSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrors({});
    setSuccessMessage('');

    // This would be replaced with an actual API call
    // For now, just simulate a successful update
    setTimeout(() => {
      setSuccessMessage('Profile updated successfully!');
      setIsLoading(false);
    }, 1000);
  };

  const handlePasswordSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrors({});
    setSuccessMessage('');

    if (newPassword !== confirmPassword) {
      setErrors({
        confirmPassword: ['Passwords do not match.'],
      });
      setIsLoading(false);
      return;
    }

    // This would be replaced with an actual API call
    // For now, just simulate a successful update
    setTimeout(() => {
      setSuccessMessage('Password updated successfully!');
      setNewPassword('');
      setCurrentPassword('');
      setConfirmPassword('');
      setIsLoading(false);
    }, 1000);
  };

  return (
    <div className='mx-auto max-w-3xl'>
      <h1 className='mb-6 text-3xl font-bold'>Profile Settings</h1>

      {successMessage && (
        <div className='mb-6 border-l-4 border-accent bg-accent/20 p-4 text-accent-foreground'>
          {successMessage}
        </div>
      )}

      <div className='grid gap-8 md:grid-cols-1'>
        <div className='neu-card'>
          <h2 className='mb-4 text-2xl font-semibold'>Account Information</h2>
          <form onSubmit={handleProfileSubmit}>
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

            <div className='mb-6'>
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

            <button
              type='submit'
              className='neu-button'
              disabled={isLoading}
            >
              {isLoading ? 'Updating...' : 'Update Profile'}
            </button>
          </form>
        </div>

        <div className='neu-card'>
          <h2 className='mb-4 text-2xl font-semibold'>Change Password</h2>
          <form onSubmit={handlePasswordSubmit}>
            <div className='mb-4'>
              <label
                htmlFor='currentPassword'
                className='mb-2 block font-medium'
              >
                Current Password
              </label>
              <input
                id='currentPassword'
                type='password'
                className='neu-input w-full'
                value={currentPassword}
                onChange={e => setCurrentPassword(e.target.value)}
                required
              />
              {errors.currentPassword && (
                <p className='mt-1 text-destructive'>
                  {errors.currentPassword[0]}
                </p>
              )}
            </div>

            <div className='mb-4'>
              <label
                htmlFor='newPassword'
                className='mb-2 block font-medium'
              >
                New Password
              </label>
              <input
                id='newPassword'
                type='password'
                className='neu-input w-full'
                value={newPassword}
                onChange={e => setNewPassword(e.target.value)}
                required
              />
              {errors.newPassword && (
                <p className='mt-1 text-destructive'>{errors.newPassword[0]}</p>
              )}
            </div>

            <div className='mb-6'>
              <label
                htmlFor='confirmPassword'
                className='mb-2 block font-medium'
              >
                Confirm New Password
              </label>
              <input
                id='confirmPassword'
                type='password'
                className='neu-input w-full'
                value={confirmPassword}
                onChange={e => setConfirmPassword(e.target.value)}
                required
              />
              {errors.confirmPassword && (
                <p className='mt-1 text-destructive'>
                  {errors.confirmPassword[0]}
                </p>
              )}
            </div>

            <button
              type='submit'
              className='neu-button'
              disabled={isLoading}
            >
              {isLoading ? 'Updating...' : 'Change Password'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
