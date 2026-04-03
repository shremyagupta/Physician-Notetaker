import React, { useState } from 'react';

function MessageInput({ onSendMessage, onEndSession, isGenerating, isSuggesting, onSuggestMedicine }) {
  const [text, setText] = useState("");
  const [imageFile, setImageFile] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text.trim()) return;

    onSendMessage({
      speaker: 'Patient',
      text: text.trim(),
      timestamp: new Date(),
      imageName: imageFile ? imageFile.name : undefined,
    });

    setText("");
    setImageFile(null);
  };

  return (
    <div className="input-area">
      <form className="input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Type your answer..."
          autoFocus
        />
        <button type="submit" className="btn btn-primary send-btn" disabled={!text.trim() || isSuggesting}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </form>

      <div className="upload-row">
        <label className="upload-label">
          Attach image (e.g. skin rash, allergy)
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setImageFile(e.target.files && e.target.files[0] ? e.target.files[0] : null)}
          />
        </label>
        {imageFile && (
          <span className="upload-filename no-print">Selected: {imageFile.name}</span>
        )}
      </div>

      <div className="action-area">
        <button
          className="btn btn-primary suggest-btn"
          onClick={onSuggestMedicine}
          disabled={isGenerating || isSuggesting}
          type="button"
          style={{ marginRight: '1rem', background: 'linear-gradient(135deg, #8b5cf6, #3b82f6)' }}
        >
          {isSuggesting ? (
            <span className="generating-text">
              <span className="spinner"></span> AI Thinking...
            </span>
          ) : (
            <>AI Suggest Medicine</>
          )}
        </button>
        <button
          className="btn btn-secondary end-session-btn"
          onClick={onEndSession}
          disabled={isGenerating || isSuggesting}
        >
          {isGenerating ? (
            <span className="generating-text">
              <span className="spinner"></span> Preparing Medical Report...
            </span>
          ) : (
            <>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="9" y1="9" x2="15" y2="15"></line>
                <line x1="15" y1="9" x2="9" y2="15"></line>
              </svg>
              End Session & Download Medical Report
            </>
          )}
        </button>
      </div>

      <style>{`
        .input-area {
          padding: 1.5rem;
          border-top: 1px solid var(--glass-border);
          background: rgba(15, 23, 42, 0.4);
          border-radius: 0 0 16px 16px;
        }

        .input-form {
          display: flex;
          gap: 0.5rem;
          margin-bottom: 1.5rem;
        }

        .input-form input {
          flex: 1;
          background: rgba(0, 0, 0, 0.2);
        }

        .send-btn {
          padding: 0 1.2rem;
          border-radius: 8px;
        }
        
        .send-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
          box-shadow: none;
        }

        .action-area {
          display: flex;
          justify-content: center;
        }

        .upload-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 0.75rem;
          margin-bottom: 1rem;
          font-size: 0.8rem;
          color: var(--text-dim);
        }

        .upload-label input[type="file"] {
          display: block;
          margin-top: 0.25rem;
          font-size: 0.8rem;
        }

        .upload-filename {
          font-size: 0.8rem;
          color: var(--text-main);
        }

        .end-session-btn {
          width: 100%;
          color: #ef4444; /* red tint */
          border-color: rgba(239, 68, 68, 0.3);
        }

        .end-session-btn:hover:not(:disabled) {
          background: rgba(239, 68, 68, 0.1);
          border-color: rgba(239, 68, 68, 0.5);
        }

        .end-session-btn:disabled {
          color: var(--text-dim);
          border-color: var(--glass-border);
          cursor: not-allowed;
        }

        .generating-text {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .spinner {
          width: 16px;
          height: 16px;
          border: 2px solid rgba(255,255,255,0.3);
          border-radius: 50%;
          border-top-color: white;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

export default MessageInput;
