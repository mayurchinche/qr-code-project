import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import styled from "@emotion/styled";
import { FaExclamationTriangle } from "react-icons/fa";

const AlertBox = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background-color: rgba(255, 0, 0, 0.1);
  border-left: 5px solid red;
  color: red;
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 10px;
  border-radius: 5px;
  animation: fadeIn 0.5s ease-in-out;

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
  }
`;

const CloseButton = styled.button`
  background: transparent;
  border: none;
  font-size: 16px;
  color: red;
  cursor: pointer;
  margin-left: auto;
`;

const PageContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  padding: 20px;
`;

const Header = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
`;

const FormContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: flex-start;
  width: 100%;
  padding: 20px;
  margin-top: 10px;
`;

const FormBox = styled.div`
  width: 60%;
  padding: 40px;
  border: none;
  box-shadow: none;

  @media (max-width: 768px) {
    width: 100%;
    padding: 15px;
  }
`;

const FormTitle = styled.h2`
  color: #008037;
  font-size: 24px;
  font-weight: bold;
  text-align: left;
  margin-bottom: 20px;

  @  @media (max-width: 768px) {
    font-size: 20px;
    text-align: left;
    margin-left: 5px;
  }
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  margin-bottom: 15px;
`;

const InfoText = styled.p`
  font-size: 12px;
  color: #008037;
  margin-bottom: 10px;
`;

const Label = styled.label`
  font-weight: normal;
  color: #008037;
  font-size: 14px;
`;

const Input = styled.input`
  border: none;
  border-bottom: 2px solid #008037;
  padding: 8px;
  font-size: 16px;
  outline: none;
  background: transparent;
  width: 100%;
  color: #008037;
`;

const CheckboxGroup = styled.div`
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
`;

const SubmitButton = styled.button`
  width: 100%;
  background-color: #008037;
  color: white;
  font-size: 18px;
  font-weight: bold;
  padding: 12px;
  border: none;
  cursor: pointer;
  text-transform: uppercase;

  &:hover {
    background-color: #00682e;
  }

  @media (max-width: 768px) {
    font-size: 16px;
    padding: 10px;
  }
`;

const Separator = styled.div`
  width: 100%;
  height: 2px;
  background-color: #4CAF50;
  margin: 5px 0;
`;

const ErrorMessage = styled.div`
  color: red;
  margin-top: 10px;
`;

const SuccessMessage = styled.div`
  color: green;
  margin-top: 10px;
`;

const QRCodeForm = () => {
  const navigate = useNavigate();
  const urlParams = new URLSearchParams(window.location.search);
  const [model, setModel] = useState(urlParams.get("model") || "");
  const [serial, setSerial] = useState(urlParams.get("serial") || "");
  const [mfgYear, setMfgYear] = useState(urlParams.get("mfg_year") || "");
  const [company, setCompany] = useState("");
  const [city, setCity] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [success, setSuccess] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const API_URL = import.meta.env.VITE_API_URL;

const ErrorMessage = ({ message, onClose }) => {
  if (!message) return null;
  return (
    <AlertBox>
      <FaExclamationTriangle />
      {message}
      <CloseButton onClick={onClose}>×</CloseButton>
    </AlertBox>
  );
};
  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");
    setSuccess(null);
    setIsProcessing(true); // Set processing state to true

    try {
      // Check if the customer is already registered
      const checkResponse = await axios.post(`${API_URL}/check_registration`, {
        email: String(email),
        model_name: String(model),
        serial_number: String(serial),
        mfg_year: String(mfgYear)
      }, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });

      if (checkResponse.data.exists) {
        setMessage("You have already registered for this product.");
        setIsProcessing(false); // Set processing state to false
        return;
      }
      // Proceed with form submission if not registered
      const response = await axios.post(`${API_URL}/submit_form`, {
        email: String(email),
        company_name: String(company),
        customer_city: String(city),
        model_name: String(model),
        serial_number: String(serial),
        mfg_year: String(mfgYear)
      }, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });

      if (response.data.message === "Email Sent") {
        setSuccess(true);
        setMessage("");
        navigate(`/product_subscription?model=${model}&serial=${serial}&mfg_year=${mfgYear}`);
      } else {
        setSuccess(false);
        setMessage("Submission failed.");
      }
    } catch (error) {
      setSuccess(false);
      setMessage("An error occurred while submitting the form.");
      console.error("Submit form error:", error);
    } finally {
      setIsProcessing(false); // Ensure processing state is reset
    }
  };

  return (
    <PageContainer>
      <Header>
        <img src="/images/losma_2_logo.png" alt="Company Logo" className="form-logo responsive-logo top-left-logo" />
               <Separator />
      </Header>
      <FormContainer>
        <FormBox>
          <FormTitle>Fill out the form to receive your product manual</FormTitle>
          {message && <ErrorMessage>{message}</ErrorMessage>}
          {success && <SuccessMessage>Form submitted successfully!</SuccessMessage>}
          <form onSubmit={handleSubmit}>
            <FormGroup>
              <Label>Series and Model *</Label>
              <Input type="text" value={model} disabled />
            </FormGroup>

            <FormGroup>
              <Label>Serial Number *</Label>
              <Input type="text" value={serial} disabled />
            </FormGroup>

            <FormGroup>
              <Label>Manufacturing Year *</Label>
              <Input type="text" value={mfgYear} disabled />
            </FormGroup>

            <FormGroup>
              <Label>Company *</Label>
              <Input
                type="text"
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                required
              />
            </FormGroup>

            <FormGroup>
              <Label>Email *</Label>
              <Input
                type="email"
                value={email}
               onChange={(e) => {
      setEmail(e.target.value);
      setMessage(""); // Clear error message when email changes
    }}
                required
              />
            </FormGroup>

            <FormGroup>
              <Label>City *</Label>
              <Input
                type="text"
                value={city}
                onChange={(e) => setCity(e.target.value)}
                required
              />
            </FormGroup>

            <CheckboxGroup>
              <InfoText>We will be storing your data for future use.</InfoText>
              <div style={{ marginTop: '5px' }}>
                <input type="checkbox" required />
                <Label>I agree to the Privacy Policy *</Label>
              </div>
            </CheckboxGroup>

            <div style={{ marginTop: '20px' }}></div>
            <SubmitButton type="submit" disabled={isProcessing}>
              {isProcessing ? "Processing..." : "SEND"}
            </SubmitButton>
            {message && <ErrorMessage message={message} onClose={() => setMessage("")} />}
          </form>
        </FormBox>
      </FormContainer>
    </PageContainer>
  );
};

export default QRCodeForm;