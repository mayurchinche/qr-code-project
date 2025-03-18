import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import styled from "@emotion/styled";

const PageContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  padding: 20px;
  background: #f4f4f4;
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

const QRCodeImage = styled.img`
  width: 200px;
  height: 200px;
  margin-top: 20px;
  border: 2px solid #008037;
  border-radius: 8px;
  display: block;
  object-fit: contain;

  @media (max-width: 768px) {
    width: 150px;
    height: 150px;
  }
`;

const DownloadButton = styled.button`
  margin-top: 10px;
  padding: 10px 20px;
  font-size: 1rem;
  cursor: pointer;
  background-color: #008037;
  color: white;
  border: none;
  border-radius: 5px;

  &:hover {
    background-color: #00682e;
  }
`;

const QRCodeForm = () => {
  const navigate = useNavigate();
  const urlParams = new URLSearchParams(window.location.search);
  const [model, setModel] = useState(urlParams.get("model") || "");
  const [serial, setSerial] = useState(urlParams.get("serial") || "");
  const [mfgYear, setMfgYear] = useState(urlParams.get("mfg_year") || "");
  const [qrCode, setQrCode] = useState("");
  const [generatedURL, setGeneratedURL] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const API_URL = import.meta.env.VITE_API_URL;

  const handleGenerateURL = async () => {
    setIsGenerating(true);
    try {
      const response = await axios.get(
        `${API_URL}/generate_qr_url?model_name=${model}&serial_number=${serial}&mfg_year=${mfgYear}`
      );
      const data = response.data;
      if (data.qr_code && data.url) {
        setQrCode(data.qr_code);
        setGeneratedURL(data.url);
      }
    } catch (error) {
      console.error("Error generating QR code:", error);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownloadQR = () => {
    const link = document.createElement("a");
    link.href = qrCode;
    link.download = "QR_Code.png";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <PageContainer>
      <Header>
        <img src="/images/losma_2_logo.png" alt="Company Logo" className="form-logo responsive-logo top-left-logo" />
      </Header>
      <FormContainer>
        <FormBox>
          <h2>Generate QR Code</h2>
          <button onClick={handleGenerateURL} disabled={isGenerating}>
            {isGenerating ? "Generating..." : "Generate QR Code"}
          </button>
          {qrCode && (
            <>
              <QRCodeImage src={qrCode} alt="Generated QR Code" />
              <DownloadButton onClick={handleDownloadQR}>Download QR Code</DownloadButton>
            </>
          )}
        </FormBox>
      </FormContainer>
    </PageContainer>
  );
};

export default QRCodeForm;
