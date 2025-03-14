import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import App from './components/App';
import LoginPage from './components/LoginPage';
import Dashboard from './components/Dashboard';
import FormPage from './components/FormPage';
import ProductSubscription from './components/ProductSubscription';
import QRCodeForm from './components/losma_form';

import './index.css';
const API_URL = import.meta.env.VITE_API_URL;
console.log("BACKEND API:", API_URL);
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Router>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/form" element={<FormPage />} />
        <Route path="/QRCodeForm" element={<QRCodeForm />} />
        <Route path="/product_subscription" element={<ProductSubscription />} />
      </Routes>
    </Router>
  </React.StrictMode>
);