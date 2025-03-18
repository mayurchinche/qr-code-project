import styled from '@emotion/styled';

export const Container = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #ece9e6, #ffffff);
`;

export const Form = styled.form`
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 50px;
  background: #fff;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  width: 100%;
  max-width: 400px;
`;

export const Input = styled.input`
  margin: 10px 0;
  padding: 12px;
  width: 100%;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
`;

export const Button = styled.button`
  margin-top: 20px;
  padding: 12px;
  width: 100%;
  border: none;
  border-radius: 4px;
  background-color: #008037;
  color: white;
  font-size: 16px;
  cursor: pointer;

  &:hover {
     background-color: #054922;
  }
`;

export const Title = styled.h1`
  font-size: 24px;
  color: #333;
  margin-bottom: 20px;
`;
