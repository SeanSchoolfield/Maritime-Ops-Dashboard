import { useState } from 'react';

const FiltersUI = ({ onClose }) => {
    const [showVesselTypes, setShowVesselTypes] = useState(false);
    const [showOrigin, setShowOrigin] = useState(false);
    const [showStatus, setShowStatus] = useState(false);
    const [countryOfOrigin, setCountryOfOrigin] = useState('');

    // Implementation of checkbox change handler, requires DB implementation to be fully functional.
    const handleCheckboxChange = (event) => { 
        const { name, checked } = event.target;
     };

    // Implementation of country of origin change handler, requires DB implementation to be fully functional.
    const handleCountryChange = (event) => {
        setCountryOfOrigin(event.target.value);
    }

    return (

        <div className="filter-panel">
            <h3>Filters</h3>
            <button onClick={onClose}>Close</button>
            <button onClick={() => setShowVesselTypes(!showVesselTypes)}> Vessel Type </button>
            <button onClick={() => setShowOrigin(!showOrigin)}> Country of Origin </button>
            <button onClick={() => setShowStatus(!showStatus)}> Status </button>

            {showVesselTypes && ( 
                <div className="subwindow">
                    <h4>Vessel Types</h4>
                    <label>
                        <input type="checkbox" name="tanker" onChange={handleCheckboxChange} />
                        Tanker
                    </label>
                    <label>
                        <input type="checkbox" name="cargo" onChange={handleCheckboxChange} />
                        Cargo
                    </label>
                    <label>
                        <input type="checkbox" name="fishing" onChange={handleCheckboxChange} />
                        Fishing
                    </label>
                    {/* Add more vessel types, should align with DB values */}
                </div>
             )}

             {showOrigin && ( 
                <div className="subwindow">
                    <h4>Country of Origin</h4>
                    <label>
                        <input 
                            type="checkbox" 
                            value={countryOfOrigin} 
                            onChange={handleCountryChange} 
                            placeholder='Enter country of origin'    
                        />
                        
                    </label>

                </div>
              )}

            {showStatus && ( 
                <div className="subwindow">
                    <h4>Status</h4>
                    <label>
                        <input type="checkbox" name="docked" onChange={handleCheckboxChange} />
                        Docked
                    </label>
                    <label>
                        <input type="checkbox" name="underway" onChange={handleCheckboxChange} />
                        Underway
                    </label>
                    <label>
                        <input type="checkbox" name="unknown" onChange={handleCheckboxChange} />
                        Unknown
                    </label>
                    {/* Add more statuses */}
                </div>
              )}
        </div>
    );
};

export default FiltersUI