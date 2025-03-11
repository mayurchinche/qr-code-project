// Loader.jsx
import React from 'react';
import styled from '@emotion/styled';

const LoaderWrapper = styled.div`
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100px;
`;

const Loader = () => (
    <LoaderWrapper>
        <div>Loading...</div>
    </LoaderWrapper>
);

export default Loader;