/** @jsxImportSource @emotion/react */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import useFetchCustomers from '../hooks/useFetchCustomers';
import useFetchProducts from '../hooks/useFetchProducts';
import Loader from './Loader';
import {
    DashboardContainer,
    DashboardButton,
    TableWrapper,
    StyledTable,
    StyledTableHeader,
    StyledTableRow,
    StyledTableCell,
    SearchInput,
    RefreshButton,
    FormContainer,
    StyledLabel,
    StyledInput,
    GenerateButton,
    SuccessMessage
} from './dashboardStyles';

const Dashboard = () => {
    const navigate = useNavigate();
    const [loadCustomers, setLoadCustomers] = useState(true);
    const [loadProducts, setLoadProducts] = useState(false);
    const [customerFilterText, setCustomerFilterText] = useState('');
    const [cityFilter, setCityFilter] = useState('');
    const [productModelFilter, setProductModelFilter] = useState('');
    const [productSerialFilter, setProductSerialFilter] = useState('');
    const [currentPage, setCurrentPage] = useState(1);
    const rowsPerPage = 5;
    const [modelName, setModelName] = useState('');
    const [serialNumber, setSerialNumber] = useState('');
    const [mfg_year, setMfgYear] = useState('');
    const [generatedURL, setGeneratedURL] = useState('');
    const [isSuccess, setIsSuccess] = useState(false);
    const [isGenerating, setIsGenerating] = useState(false); // Loader state for the generate URL process
    const API_URL = import.meta.env.VITE_API_URL;
    const customerRowsPerPage = 10;

    const { data: customers, loading: customersLoading, error: customersError, refetch: refetchCustomers } = useFetchCustomers(
        loadCustomers ? `${API_URL}/get_customer_queries` : null
    );

    const { data: products, loading: productsLoading, error: productsError, refetch: refetchProducts } = useFetchProducts(
        loadProducts ? `${API_URL}/get_products` : null
    );

    useEffect(() => {
        if (loadProducts) setCurrentPage(1);
        if (loadCustomers) setCurrentPage(1);
    }, [loadProducts, loadCustomers]);

    const cityOptions = [...new Set(customers.map((customer) => customer.customer_city))];

    const filteredCustomers = customers.filter(
        (customer) =>
            (customer.customer_gmail.includes(customerFilterText) ||
                customer.company_name.includes(customerFilterText)) &&
            (cityFilter === '' || customer.customer_city === cityFilter)
    );

    const filteredProducts = products
        .filter((product) =>
            product.model_name.includes(productModelFilter) &&
            product.serial_number.includes(productSerialFilter)
        )
        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at)); // Sort by latest first

const handleGenerateURL = async () => {
    setIsGenerating(true);
    try {
        const response = await axios.get(`${API_URL}/generate_qr_url?model_name=${modelName}&serial_number=${serialNumber}&mfg_year=${mfg_year}`);
        const data = response.data;
        console.log("data", data);
        if (data.message !== 'Already exists' && data.url) {
            setGeneratedURL(data.url);
            setIsSuccess(true);
            await refetchProducts(); // Refresh the table with the latest data
        } else if (data.message && data.message === 'Already exists') {
            setGeneratedURL('');
            alert('URL already exists');
            setIsSuccess(false);
        }
    } catch (error) {
        console.error('Error generating URL:', error);
        setIsSuccess(false);
    } finally {
        setIsGenerating(false);
    }
};

    const refreshCurrentView = () => {
        if (loadCustomers) {
            refetchCustomers();
        } else if (loadProducts) {
            refetchProducts();
        }
    };

   const handleNextPage = () => {
        if (currentPage * rowsPerPage < filteredProducts.length) {
            setCurrentPage(currentPage + 1);
        }
    if (currentPage * customerRowsPerPage < filteredCustomers.length) {
            setCurrentPage(currentPage + 1);
        }
    };

    const handlePrevPage = () => {
        if (currentPage > 1) {
            setCurrentPage(currentPage - 1);
        }
    };

    return (
        <DashboardContainer>
            <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', flexWrap: 'wrap' }}>
                <DashboardButton onClick={() => {
                    setLoadProducts(false);
                    setLoadCustomers(true);
                }}>
                    View Customer Details
                </DashboardButton>
                <DashboardButton onClick={() => {
                    setLoadCustomers(false);
                    setLoadProducts(true);
                }}>
                    View Product Details
                </DashboardButton>
                <RefreshButton onClick={refreshCurrentView}>Refresh</RefreshButton>
            </div>
            {loadCustomers && (
                <div style={{ width: '100%' }}>
                    <SearchInput
                        type="text"
                        placeholder="Search by email or company..."
                        value={customerFilterText}
                        onChange={(e) => setCustomerFilterText(e.target.value)}
                    />
                    <select value={cityFilter} onChange={(e) => setCityFilter(e.target.value)}>
                        <option value="">All cities</option>
                        {cityOptions.map((city, index) => (
                            <option key={index} value={city}>{city}</option>
                        ))}
                    </select>
                    <TableWrapper>
                        {customersLoading && <Loader />}
                        {customersError && <p>Error fetching data: {customersError.message}</p>}
                        {!customersLoading && !customersError && (
                            <div>
                                <StyledTable>

                                    <thead>
                                        <StyledTableRow>
                                            <StyledTableHeader>Model Name</StyledTableHeader>
                                            <StyledTableHeader>Serial Number</StyledTableHeader>
                                            <StyledTableHeader>Mfg_Year</StyledTableHeader>
                                            <StyledTableHeader>Email</StyledTableHeader>
                                            <StyledTableHeader>City</StyledTableHeader>
                                            <StyledTableHeader>Company Name</StyledTableHeader>
                                            <StyledTableHeader>Date</StyledTableHeader>
                                        </StyledTableRow>
                                    </thead>
                                    <tbody>
                                        {filteredCustomers.slice((currentPage - 1) * customerRowsPerPage, currentPage * customerRowsPerPage).map((customer, index) => (
                                            <StyledTableRow key={index}>
                                                <StyledTableCell>{customer.model_name}</StyledTableCell>
                                                <StyledTableCell>{customer.serial_number}</StyledTableCell>
                                                <StyledTableCell>{customer.mfg_year}</StyledTableCell>
                                                <StyledTableCell>{customer.customer_gmail}</StyledTableCell>
                                                <StyledTableCell>{customer.customer_city}</StyledTableCell>
                                                <StyledTableCell>{customer.company_name}</StyledTableCell>
                                                <StyledTableCell>{new Date(customer.created_at).toLocaleDateString()}</StyledTableCell>
                                            </StyledTableRow>
                                        ))}
                                    </tbody>
                                </StyledTable>
                                 {filteredCustomers.length > customerRowsPerPage && (
                                                                            <div style={{ textAlign: 'right', margin: '10px' }}>
{/*                                             <DashboardButton onClick={handlePrevPage}>Previous</DashboardButton> */}
{/*                                             <DashboardButton onClick={handleNextPage}>Next</DashboardButton> */}
                                            <DashboardButton onClick={handlePrevPage} disabled={currentPage === 1}>Previous</DashboardButton>
                                            <DashboardButton onClick={handleNextPage} disabled={currentPage * customerRowsPerPage >= filteredCustomers.length}>Next</DashboardButton>
                                        </div>
                                    )}
                            </div>
                        )}
                    </TableWrapper>
                </div>
            )}
            {loadProducts && (
                <div style={{ width: '100%' }}>
                    <SearchInput
                        type="text"
                        placeholder="Search by model name..."
                        value={productModelFilter}
                        onChange={(e) => setProductModelFilter(e.target.value)}
                    />
                    <SearchInput
                        type="text"
                        placeholder="Search by serial number..."
                        value={productSerialFilter}
                        onChange={(e) => setProductSerialFilter(e.target.value)}
                    />
                    <TableWrapper>
                        {productsLoading && <Loader />}
                        {productsError && <p>Error fetching data: {productsError.message}</p>}
                        {!productsLoading && !productsError && (
                            <div>
                                <StyledTable>
                                    <thead>
                                        <StyledTableRow>
                                            <StyledTableHeader>Model Name</StyledTableHeader>
                                            <StyledTableHeader>Serial Number</StyledTableHeader>
                                            <StyledTableHeader>Mfg_Year</StyledTableHeader>
                                            <StyledTableHeader>Material URL</StyledTableHeader>
                                            <StyledTableHeader>Created At</StyledTableHeader>
                                        </StyledTableRow>
                                    </thead>
                                    <tbody>
                                        {filteredProducts.slice((currentPage - 1) * rowsPerPage, currentPage * rowsPerPage).map((product, index) => (
                                            <StyledTableRow key={index}>
                                                <StyledTableCell>{product.model_name}</StyledTableCell>
                                                <StyledTableCell>{product.serial_number}</StyledTableCell>
                                                <StyledTableCell>{product.mfg_year}</StyledTableCell>
                                                <StyledTableCell>
                                                    <a href={product.material_url} target="_blank" rel="noopener noreferrer">
                                                        {product.material_url}
                                                    </a>
                                                </StyledTableCell>
                                                <StyledTableCell>{new Date(product.created_at).toLocaleDateString()}</StyledTableCell>
                                            </StyledTableRow>
                                        ))}
                                    </tbody>
                                </StyledTable>
                                {filteredProducts.length > rowsPerPage && (
                                                                        <div style={{ textAlign: 'right', margin: '10px' }}>
                                                                  <DashboardButton onClick={handlePrevPage} disabled={currentPage === 1}> Previous</DashboardButton>
                                                                  <DashboardButton onClick={handleNextPage} disabled={currentPage * rowsPerPage >= filteredProducts.length}>Next</DashboardButton>
                                                   </div>
                                )}

                            </div>
                        )}
                    </TableWrapper>
                    <FormContainer>
                        <h3>Generate Scanner URL for New Material</h3>
                        <StyledLabel>Model Name</StyledLabel>
                        <StyledInput
                            type="text"
                            value={modelName}
                            onChange={(e) => setModelName(e.target.value)}
                        />
                        <StyledLabel>Serial Number</StyledLabel>
                        <StyledInput
                            type="text"
                            value={serialNumber}
                            onChange={(e) => setSerialNumber(e.target.value)}
                        />
                        <StyledLabel>Mfg_Year</StyledLabel>
                        <StyledInput
                            type="text"
                            value={mfg_year}
                            onChange={(e) => setMfgYear(e.target.value)}
                        />
                        <GenerateButton onClick={handleGenerateURL} disabled={isGenerating}>
                            {isGenerating ? 'Generating...' : 'Generate'}
                        </GenerateButton>
                            {isSuccess && (

                                <SuccessMessage>
                                    URL generated successfully:
                                    <a href={generatedURL} target="_blank" rel="noopener noreferrer">
                                        {generatedURL}
                                    </a>
                                </SuccessMessage>
                            )}
                    </FormContainer>
                </div>
            )}
        </DashboardContainer>
    );
};

export default Dashboard;