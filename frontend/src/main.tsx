import React from 'react';
import ReactDOM from 'react-dom/client';
import { DesignSystemShowcase } from './components/ui/Showcase';
import './index.css';

const rootEl = document.getElementById('root');
if (rootEl) {
  ReactDOM.createRoot(rootEl).render(
    <React.StrictMode>
      <DesignSystemShowcase />
    </React.StrictMode>
  );
}
