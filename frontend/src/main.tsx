import './index.css';

import { initializeTheme } from './store/theme';
try {
  initializeTheme();
} catch (e) {
  console.error('Failed to initialize theme:', e);
}

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { Provider } from 'jotai';
import App from './App.tsx';

const rootElement = document.getElementById('root');
if (rootElement) {
  createRoot(rootElement).render(
    <StrictMode>
      <Provider>
        <App />
      </Provider>
    </StrictMode>
  );
}
