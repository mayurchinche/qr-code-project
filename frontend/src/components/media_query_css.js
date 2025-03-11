import styled from '@emotion/styled';

export const DashboardContainer = styled.div`
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 20px;
    width: 100%;
`;

export const DashboardButton = styled.button`
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 10px 20px;
    margin: 5px;
    font-size: 1em;

    &:hover {
        background-color: #0056b3;
    }

    @media (max-width: 600px) {
        padding: 8px 16px;
        font-size: 0.9em;
    }
`;

export const TableWrapper = styled.div`
    width: 100%;
    overflow-x: auto;
`;

export const StyledTable = styled.table`
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;

    @media (max-width: 600px) {
        font-size: 0.9em;
    }
`;

export const StyledTableHeader = styled.th`
    background-color: #007bff;
    color: white;
    padding: 10px;
    text-align: left;

    @media (max-width: 600px) {
        padding: 8px;
    }
`;

export const StyledTableRow = styled.tr`
    &:nth-of-type(even) {
        background-color: #f2f2f2;
    }
`;

export const StyledTableCell = styled.td`
    padding: 10px;
    border: 1px solid #ddd;

    @media (max-width: 600px) {
        padding: 8px;
    }
`;

export const SearchInput = styled.input`
    padding: 10px;
    margin: 10px 0;
    width: 100%;
    box-sizing: border-box;

    @media (max-width: 600px) {
        padding: 8px;
    }
`;

export const RefreshButton = styled(DashboardButton)`
    background-color: #28a745;

    &:hover {
        background-color: #218838;
    }
`;

export const FormContainer = styled.div`
    width: 100%;
    max-width: 600px;
    margin: 20px 0;

    @media (max-width: 600px) {
        padding: 10px;
        margin: 15px 0;
    }
`;

export const StyledLabel = styled.label`
    display: block;
    margin: 10px 0 5px 0;
    font-size: 1em;

    @media (max-width: 600px) {
        font-size: 0.9em;
    }
`;

export const StyledInput = styled.input`
    padding: 10px;
    margin: 5px 0;
    width: 100%;
    box-sizing: border-box;

    @media (max-width: 600px) {
        padding: 8px;
    }
`;

export const GenerateButton = styled(DashboardButton)`
    background-color: #ffc107;

    &:hover {
        background-color: #e0a800;
    }
`;

export const SuccessMessage = styled.div`
    margin-top: 20px;
    padding: 10px;
    color: #155724;
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    border-radius: 4px;

    @media (max-width: 600px) {
        padding: 8px;
    }

    a {
        color: #155724;
        text-decoration: underline;

        &:hover {
            color: #0b2e13;
        }
    }
`;