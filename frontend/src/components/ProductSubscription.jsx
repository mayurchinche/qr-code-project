import React from "react";
import { useLocation } from "react-router-dom";
import styled from "@emotion/styled";

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


const MessageContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  padding: 20px;
  margin-top: 10px;
`;

const MessageBox = styled.div`
  width: 50%;
  padding: 40px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
  border-left: 8px solid #008037;
  transition: all 0.3s ease-in-out;

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 6px 14px rgba(0, 0, 0, 0.15);
  }

  @media (max-width: 768px) {
    width: 90%;
    padding: 20px;
  }
`;

const Title = styled.h2`
  color: #008037;
  font-size: 26px;
  font-weight: bold;
  text-align: center;
  margin-bottom: 20px;

  @media (max-width: 768px) {
    font-size: 22px;
  }
`;

const Text = styled.p`
  font-size: 16px;
  color: #333;
  margin-bottom: 20px;
  line-height: 1.5;
`;

const ResourceLink = styled.a`
  display: inline-block;
  margin: 10px;
  padding: 10px 15px;
  background-color: #008037;
  color: white;
  border-radius: 6px;
  text-decoration: none;
  font-weight: bold;
  transition: background 0.3s ease-in-out;

  &:hover {
    background-color: #00682e;
  }

  @media (max-width: 600px) {
    font-size: 0.9em;
    padding: 8px 12px;
  }
`;

const Separator = styled.div`
  width: 100%;
  height: 2px;
  background-color: #4CAF50;
  margin: 10px 0;
`;

const ProductSubscription = () => {
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const modelName = queryParams.get("model") || "Sample Model";
  const serialNumber = queryParams.get("serial") || "Sample Serial";
  const mfg_year = queryParams.get("mfg_year") || "Mfg Year";
  const catalogueURL = import.meta.env.VITE_CATALOGUE_URL;
  const manualURL = import.meta.env.VITE_MANUAL_URL;

  return (
    <PageContainer>
      <Header>
        <img src="/images/losma_2_logo.png" alt="Company Logo" className="form-logo responsive-logo top-left-logo" />
        <Separator />
      </Header>
      <MessageContainer>
        <MessageBox>
          <Title>🎉 Thank You for Registering!</Title>
          <Text>
            We appreciate your trust in Our Company. <br /> <br />
            <strong>Your Purchase Details:</strong>
          </Text>
          <Text>
            <strong>Model Name:</strong> {modelName} <br />
            <strong>Serial Number:</strong> {serialNumber} <br />
            <strong>Manufacturing Year:</strong> {mfg_year}
          </Text>
          <Text>✅ Your product has been successfully registered!</Text>
          <Text>
            <strong>📂 Product Resources:</strong>
          </Text>
          <ResourceLink href={catalogueURL} target="_blank">📘 View Catalogue</ResourceLink>
          <ResourceLink href={manualURL} target="_blank">📖 Read Manual</ResourceLink>
        </MessageBox>
      </MessageContainer>
    </PageContainer>
  );
};

export default ProductSubscription;
