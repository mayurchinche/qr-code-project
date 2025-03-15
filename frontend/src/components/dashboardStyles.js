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
  background-color: #008037;
  color: white;
  font-size: 16px;
  cursor: pointer;

  &:hover {
    background-color: #054922;
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
  background-color: #008037;
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
    background-color: #008037;
    color: white;
    border: none;
    border-radius: 5px;
      &:hover {
    background-color: #054922;
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



export const FormContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  margin-top: 30px;
  @media (max-width: 768px) {
    padding: 15px;
  }
`;
export const FormRow = styled.div`
  display: flex;
  align-items: center;
  flex-wrap: nowrap;
  justify-content: space-between;
  width: 100%;

  @media (max-width: 768px) {
    flex-direction: column;
    align-items: flex-start;
  }
`;

export const Title = styled.h3`
  padding: 12px;
  background-color: #008037;
  color: white;
  text-align: center;
  margin-bottom: 20px;
  border-bottom: 1px solid #ddd;
  width: 100%;
  @media (max-width: 768px) {
  width: 100%;
    padding: 8px;
  }
`;



export const StyledLabel = styled.label`
  margin-bottom: 5px;
  font-weight: bold;

  @media (max-width: 768px) {
    display: block;
  }
`;

export const StyledInput = styled.input`
  padding: 8px;
  font-size: 14px;
  border: 1px solid #ccc;
  border-radius: 4px;
  width: 200px;

  @media (max-width: 768px) {
    width: 100%;
  }
`;

export const GenerateButton = styled.button`
  padding: 10px 15px;
  font-size: 16px;
  border: none;
  border-radius: 4px;
  background-color: #008037;
  color: white;
  cursor: pointer;
  margin-left: 10px;

  &:disabled {
    background-color: #6c757d;
    cursor: not-allowed;
  }

  @media (max-width: 768px) {
    width: 100%;
    margin-left: 0;
    margin-top: 10px;
  }
    &:hover {
    background-color: #054922;
  }
  @media (max-width: 768px) {
    width: 100%;
    margin: 8px 0;
  }
`;

export const SuccessMessage = styled.div`
  margin-top: 20px;
  padding: 10px;
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
  border-radius: 4px;
  width: 100%;
  text-align: center;
  position: relative;
  @media (max-width: 768px) {
    width: 100%;
    margin-right: 0;
    margin-bottom: 15px;
  }
`;

export const CopyButton = styled.button`
  margin-left: 10px;
  padding: 5px 10px;
  font-size: 12px;
  border: none;
  border-radius: 4px;
  background-color: #008037;
  color: white;
  cursor: pointer;
  background-color: ${(props) => (props.copied ? '#6c757d' : '#28a745')};

`;


export const InnerContainer = styled.div`
  max-width: 900px;
  width: 100%;
`;

export const FieldContainer = styled.div`
  display: flex;
  flex-direction: column;
  margin-right: 10px;
  margin-bottom: 10px;

  @media (max-width: 768px) {
    width: 100%;
    margin-right: 0;
    margin-bottom: 15px;
  }
`;


export const ErrorMessage = styled.div`
  color: red;
  margin-top: 10px;
`;