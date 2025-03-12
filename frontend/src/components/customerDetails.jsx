import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const CustomerDetails = () => {
    const [customers, setCustomers] = useState([]);
    const [currentPage, setCurrentPage] = useState(1);
    const rowsPerPage = 10; // Show 10-15 rows per page
    const navigate = useNavigate();
    const API_URL = import.meta.env.VITE_API_URL;

    useEffect(() => {
        fetchCustomers();
    }, []);

    const fetchCustomers = async () => {
        try {
            const response = await axios.get(`${API_URL}/get_customer_queries`);
            setCustomers(response.data);
        } catch (error) {
            console.error('Error fetching customer data:', error);
        }
    };

    const totalPages = Math.ceil(customers.length / rowsPerPage);
    const currentRows = customers.slice((currentPage - 1) * rowsPerPage, currentPage * rowsPerPage);

    const handleNextPage = () => {
        if (currentPage < totalPages) {
            setCurrentPage(currentPage + 1);
        }
    };

    const handlePrevPage = () => {
        if (currentPage > 1) {
            setCurrentPage(currentPage - 1);
        }
    };

    return (
        <div style={{ padding: '20px' }}>
            <h2>Customer Details</h2>
            <button onClick={() => navigate('/dashboard')} style={{ marginBottom: '10px' }}>Back to Dashboard</button>
            <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '600px' }}>
                    <thead>
                        <tr>
                            <th>Model Name</th>
                            <th>Serial Number</th>
                            <th>Email</th>
                            <th>City</th>
                            <th>Company Name</th>
                            <th>Date</th>
                        </tr>
                    </thead>
                    <tbody>
                        {currentRows.map((customer, index) => (
                            <tr key={index}>
                                <td>{customer.model_name}</td>
                                <td>{customer.serial_number}</td>
                                <td>{customer.customer_gmail}</td>
                                <td>{customer.customer_city}</td>
                                <td>{customer.company_name}</td>
                                <td>{new Date(customer.created_at).toLocaleDateString()}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
            <div style={{ marginTop: '10px', display: 'flex', justifyContent: 'space-between' }}>
                <button onClick={handlePrevPage} disabled={currentPage === 1}>Previous</button>
                <span>Page {currentPage} of {totalPages}</span>
                <button onClick={handleNextPage} disabled={currentPage === totalPages}>Next</button>
            </div>
        </div>
    );
};

export default CustomerDetails;
