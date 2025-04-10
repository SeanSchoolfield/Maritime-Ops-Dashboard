import React from "react";

/**
 * ConfirmationDialog component for displaying a confirmation dialog.
 * @param {Object} props - Component props.
 * @param {string} props.message - The message to display in the dialog.
 * @param {Function} props.onConfirm - Callback function to call when the user confirms.
 * @param {Function} props.onCancel - Callback function to call when the user cancels.
 * @returns {JSX.Element} - The rendered ConfirmationDialog component.
 */
const ConfirmationDialog = ({ message, onConfirm, onCancel }) => {
    return (
        <div className="confirmation-dialog">
            <div className="confirmation-dialog-content">
                <p>{message}</p>
                <div className="confirmation-dialog-buttons">
                    <button onClick={onConfirm}>Confirm</button>
                    <button onClick={onCancel}>Cancel</button>
                </div>
            </div>
        </div>
    );
};

export default ConfirmationDialog;