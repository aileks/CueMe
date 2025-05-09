import { Link, useLocation } from 'react-router';

interface NavLinkProps {
  to: string;
  children: React.ReactNode;
  className?: string;
  exact?: boolean;
}

export default function NavLink({
  to,
  children,
  className = '',
  exact = false,
}: NavLinkProps) {
  const location = useLocation();
  const isActive =
    exact ? location.pathname === to : location.pathname.startsWith(to);

  return (
    <Link
      to={to}
      className={`neu-nav-link ${isActive ? 'neu-nav-link-active' : ''} ${className}`}
    >
      {children}
    </Link>
  );
}
