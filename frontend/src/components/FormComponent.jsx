import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import styled from '@emotion/styled';

const BackgroundWrapper = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #74ebd5 0%, #ACB6E5 100%);
`;

const FormWrapper = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 20px;
  width: 100%;
  max-width: 600px;
  margin: auto;
  background: white;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border-radius: 8px;

  @media (max-width: 600px) {
    padding: 20px 10px;
    box-shadow: none;
  }
`;

const FormTitle = styled.h1`
  font-size: 2em;
  margin-bottom: 20px;
  color: #333;

  @media (max-width: 600px) {
    font-size: 1.5em;
  }
`;

const StyledInput = styled.input`
  padding: 15px;
  width: 100%;
  margin: 10px 0;
  box-sizing: border-box;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1em;

  &:focus {
    border-color: #007bff;
    outline: none;
    box-shadow: 0 0 5px rgba(0, 123, 255, 0.25);
  }

  @media (max-width: 600px) {
    padding: 10px;
  }
`;

const SubmitButton = styled.button`
  padding: 15px 20px;
  margin: 20px 0;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1em;
  cursor: pointer;
  transition: background-color 0.3s;

  &:hover {
    background-color: #0056b3;
  }

  @media (max-width: 600px) {
    padding: 10px 16px;
    font-size: 0.9em;
  }
`;

const Message = styled.div`
  margin-top: 20px;
  padding: 15px;
  color: ${(props) => (props.success ? '#155724' : '#721c24')};
  background-color: ${(props) => (props.success ? '#d4edda' : '#f8d7da')};
  border: 1px solid ${(props) => (props.success ? '#c3e6cb' : '#f5c6cb')};
  border-radius: 4px;

  @media (max-width: 600px) {
    padding: 10px;
  }
`;

const FormComponent = () => {
  const navigate = useNavigate();
  const urlParams = new URLSearchParams(window.location.search);
  const [modelName, setModelName] = useState(urlParams.get('model') || '');
  const [serialNumber, setSerialNumber] = useState(urlParams.get('serial') || '');
  const [companyName, setCompanyName] = useState('');
  const [city, setCity] = useState('');
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [success, setSuccess] = useState(null);
  const API_URL = import.meta.env.VITE_API_URL;
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API_URL}/submit_form`, {
        email,
        company_name: companyName,
        customer_city: city,
        model_name: modelName,
        serial_number: serialNumber,
      }, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
               },
      });

      if (response.data.message === 'Email Sent') {
        setSuccess(true);
        navigate(`/product_subscription?model=${modelName}&serial=${serialNumber}`);
      } else {
        setSuccess(false);
        setMessage('Submission failed.');
      }
    } catch (error) {
      setSuccess(false);
      setMessage('An error occurred while submitting the form.');
      console.error('Submit form error:', error);
    }
  };

  return (
    <BackgroundWrapper>
      <FormWrapper>
        <FormTitle>Product Registration</FormTitle>
        <form onSubmit={handleSubmit}>
          <StyledInput
            type="text"
            value={modelName}
            placeholder="Model Name"
            disabled
          />
          <StyledInput
            type="text"
            value={serialNumber}
            placeholder="Serial Number"
            disabled
          />
          <StyledInput
            type="text"
            value={companyName}
            placeholder="Company Name"
            onChange={(e) => setCompanyName(e.target.value)}
            required
          />
          <StyledInput
            type="text"
            value={city}
            placeholder="City"
            onChange={(e) => setCity(e.target.value)}
            required
          />
          <StyledInput
            type="email"
            value={email}
            placeholder="Gmail Address"
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <SubmitButton type="submit">Submit</SubmitButton>
        </form>
        {message && (
          <Message success={success}>
            {message}
          </Message>
        )}
      </FormWrapper>
    </BackgroundWrapper>
  );
};

export default FormComponent;