import React from 'react';
import { useLocation } from 'react-router-dom';
import styled from '@emotion/styled';

const BackgroundWrapper = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #74ebd5 0%, #ACB6E5 100%);
`;

const MessageBox = styled.div`
  padding: 40px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
  max-width: 600px;
  width: 100%;

  @media (max-width: 600px) {
    padding: 20px;
  }
`;

const Title = styled.h1`
  color: #333;
  margin-bottom: 20px;
  font-size: 2em;

  @media (max-width: 600px) {
    font-size: 1.5em;
  }
`;

const Text = styled.p`
  color: #555;
  margin-bottom: 20px;
  font-size: 1.1em;

  @media (max-width: 600px) {
    font-size: 1em;
  }
`;

const ResourceLink = styled.a`
  display: block;
  margin: 10px 0;
  color: #007bff;
  text-decoration: none;
  font-size: 1.1em;

  &:hover {
    text-decoration: underline;
    color: #0056b3;
  }

  @media (max-width: 600px) {
    font-size: 1em;
  }
`;

const ProductSubscription = () => {
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const modelName = queryParams.get('model') || 'Sample Model';
  const serialNumber = queryParams.get('serial') || 'Sample Serial';
  const catalogueURL = "https://losma.com/product/galileo-plus";
  const manualURL = "https://losma.com/product/galileo-plus";
  return (
    <BackgroundWrapper>
      <MessageBox>
        <Title>Thank You for Registering!</Title>
        <Text>
          We appreciate your trust in Our Company. Your purchase of
          <strong> {modelName} </strong>
          with Serial Number          <strong> {serialNumber}</strong>
          has been successfully registered.
        </Text>
        <Text>
        <strong>Product Resources:</strong>
        </Text>
        <ResourceLink href="https://losma.com/product/galileo-plus" target="_blank">Product Catalogue: View Catalogue</ResourceLink>
        <ResourceLink href="https://losma.com/product/galileo-plus" target="_blank">User Manual: Read Manual</ResourceLink>
      </MessageBox>
    </BackgroundWrapper>
  );
};

export default ProductSubscription;