import { useState, useEffect } from 'react';

const useFetchCustomers = (url) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
   const fetchData = async () => {
      try {
        console.log("url", url);
        setLoading(true);
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        setData(data);
      } catch (error) {
        setError(error);
      } finally {
        setLoading(false);
      }
    };

    useEffect(() => {
        if (url) {
            fetchData();
        }
    }, [url]);

  return { data, loading, error, refetch:fetchData };
};

export default useFetchCustomers;