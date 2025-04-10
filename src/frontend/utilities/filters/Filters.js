import { useEffect, useState } from 'react';
import axios from 'axios';

/**
 * Custom hook to fetch filter options for vessels.
 * @param {string} apiEndpoint - API endpoint to fetch filter options.
 * @returns {Object} - Contains filter options, selected filters, loading state, and error message.
 * @description This hook fetches filter options from the API and manages the selected filters state.
 */

const useFetchFilters = (apiEndpoint) => {
    const [filterOptions, setFilterOptions] = useState({
        types: [],
        origins: [],
        statuses: []
    });

    const [selectedFilters, setSelectedFilters] = useState({
        types: [],
        origins: [],
        statuses: []
    });

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        let isMounted = true; 
        setLoading(true);

        axios.get(apiEndpoint)
            .then((response) => {
                if (isMounted) {
                    const data = response.data;
                    setFilterOptions(data);

                    setSelectedFilters({
                        ...selectedFilters,
                        types: data.types,
                        statuses: data.current_status
                    });
                }
            })
            .catch((error) => {
                if (isMounted) {
                    setError(`Error fetching vessel data: ${error.message}`);
                }
            })
            .finally(() => {
                if (isMounted) setLoading(false);
            });

        return () => {
            isMounted = false;
        };
    }, [apiEndpoint]);

    return { filterOptions, selectedFilters, setSelectedFilters, loading, error };
};

export default useFetchFilters;
