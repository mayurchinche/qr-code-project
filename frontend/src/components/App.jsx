import React from 'react';
import { useNavigate } from 'react-router-dom';
const API_URL = import.meta.env.VITE_API_URL;
console.log("Backend API:", API_URL);

const App = () => {
  const navigate = useNavigate();

  return (
    <div>
      <h1>Dashboard</h1>
      <button onClick={() => navigate('/')}>Logout</button>
    </div>
  );
};

export default App;