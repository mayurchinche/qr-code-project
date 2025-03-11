import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import App from './components/App';
import LoginPage from './components/LoginPage';
import Dashboard from './components/Dashboard';
import FormPage from './components/FormPage';
import ProductSubscription from './components/ProductSubscription';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/form" element={<FormPage />} />
        <Route path="/product_subscription" element={<ProductSubscription />} />
      </Routes>
    </Router>
  </React.StrictMode>
);