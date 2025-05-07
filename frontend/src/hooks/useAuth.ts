import { useAtomValue, useSetAtom } from 'jotai';
import {
  userAtom,
  isLoadingAtom,
  loginAction,
  logoutAction,
  isAuthenticatedAtom,
  checkAuthAction,
} from '../store/auth';

/**
 * Custom hook that provides authentication-related state and functions
 */
export function useAuth() {
  const user = useAtomValue(userAtom);
  const isLoading = useAtomValue(isLoadingAtom);
  const isAuthenticated = useAtomValue(isAuthenticatedAtom);
  const login = useSetAtom(loginAction);
  const logout = useSetAtom(logoutAction);
  const checkAuth = useSetAtom(checkAuthAction);

  return {
    user,
    isLoading,
    isAuthenticated,
    login,
    logout,
    checkAuth,
  };
}
