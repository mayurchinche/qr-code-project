import styled from '@emotion/styled';

export const DashboardContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  width: 100%;
  min-height: 100vh;
  background: linear-gradient(135deg, #ece9e6, #ffffff);

  select {
    margin-bottom: 20px;
    padding: 12px;
    width: 100%;
    max-width: 800px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 16px;

    @media (max-width: 768px) {
      padding: 10px;
      width: 100%;
    }
  }
`;

export const DashboardButton = styled.button`
  padding: 12px 20px;
  margin: 10px;
  border: none;
  border-radius: 4px;
  background-color: #007bff;
  color: white;
  font-size: 16px;
  cursor: pointer;

  &:hover {
    background-color: #0056b3;
  }
  &:disabled {
        background-color: #d3d3d3; /* Light Grey */
        color: #a1a1a1; /* Dimmed text */
        cursor: not-allowed;
    }
  @media (max-width: 768px) {
    width: 100%;
    margin: 8px 0;
  }


`;

export const TableWrapper = styled.div`
  margin-top: 20px;
  width: 100%;
  max-width: 100%;
  overflow-x: auto;
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);

  @media (max-width: 768px) {
    width: 100%;
  }
`;

export const StyledTable = styled.table`
  width: 100%;
  border-collapse: collapse;
`;

export const StyledTableHeader = styled.th`
  padding: 12px;
  background-color: #007bff;
  color: white;
  text-align: left;
  border-bottom: 1px solid #ddd;

  @media (max-width: 768px) {
    padding: 8px;
  }
`;

export const StyledTableRow = styled.tr`
  &:nth-of-type(even) {
    background-color: #f2f2f2;
  }
`;

export const StyledTableCell = styled.td`
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;

  @media (max-width: 768px) {
    padding: 8px;
  }
`;

export const SearchInput = styled.input`
  margin-bottom: 20px;
  padding: 12px;
  width: 100%;
  max-width: 800px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;

  @media (max-width: 768px) {
    padding: 10px;
    width: 100%;
  }
`;
export const RefreshButton = styled.button`
    margin: 10px;
    padding: 10px 20px;
    font-size: 1rem;
    cursor: pointer;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 5px;
`;
export const FormContainer = styled.div`
    margin-top: 20px;
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 8px;
    background-color: #f9f9f9;
    width: 100%;
    max-width: 500px;
`;

export const StyledLabel = styled.label`
    display: block;
    margin: 10px 0 5px;
    font-weight: bold;
`;

export const StyledInput = styled.input`
    width: 100%;
    padding: 8px;
    margin-bottom: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
`;

export const GenerateButton = styled.button`
    margin-top: 10px;
    padding: 10px 20px;
    font-size: 1rem;
    cursor: pointer;
    background-color: #28a745;
    color: white;
    border: none;
    border-radius: 5px;
`;

export const SuccessMessage = styled.p`
    margin-top: 10px;
    color: green;
    font-weight: bold;
    a {
        color: #007bff;
        text-decoration: none;
    }
`;