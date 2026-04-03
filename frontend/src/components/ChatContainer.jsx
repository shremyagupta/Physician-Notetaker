import React, { useEffect, useRef } from 'react';

function ChatContainer({ messages }) {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h3>Transcript Log</h3>
      </div>

      <div className="messages-area">
        {messages.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🩺</div>
            <p>Ready to record consultation.</p>
            <span>Start typing below to begin logging the transcript.</span>
          </div>
        ) : (
          messages.map((msg, idx) => {
            const speakerClass = msg.speaker.toLowerCase().replace(' ', '-');
            return (
              <div
                key={idx}
                className={`message-bubble animate-fade-in ${speakerClass}`}
              >
                <div className="speaker-label">{msg.speaker}</div>
                <div className="message-content">{msg.text}</div>
              </div>
            );
          })
        )}
        <div ref={messagesEndRef} />
      </div>

      <style>{`
        .chat-container {
          display: flex;
          flex-direction: column;
          height: 100%;
        }

        .chat-header {
          padding: 1rem 1.5rem;
          border-bottom: 1px solid var(--glass-border);
          background: rgba(255,255,255,0.02);
          border-radius: 16px 16px 0 0;
        }

        .messages-area {
          flex: 1;
          overflow-y: auto;
          padding: 1.5rem;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .empty-state {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 100%;
          color: var(--text-dim);
          text-align: center;
        }

        .empty-icon {
          font-size: 3rem;
          margin-bottom: 1rem;
          opacity: 0.5;
        }

        .empty-state span {
          font-size: 0.85rem;
          margin-top: 0.5rem;
          opacity: 0.7;
        }

        .message-bubble {
          max-width: 80%;
          padding: 1rem;
          border-radius: 12px;
          position: relative;
        }

        .speaker-label {
          font-size: 0.75rem;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          margin-bottom: 0.4rem;
          opacity: 0.8;
        }

        .message-content {
          font-size: 0.95rem;
          line-height: 1.5;
        }

        /* Doctor Styles */
        .doctor {
          align-self: flex-start;
          background: var(--doctor-bg);
          border: 1px solid var(--doctor-border);
          border-bottom-left-radius: 4px;
        }

        .doctor .speaker-label {
          color: var(--primary);
        }

        /* Patient Styles */
        .patient {
          align-self: flex-end;
          background: var(--patient-bg);
          border: 1px solid var(--patient-border);
          border-bottom-right-radius: 4px;
        }

        .patient .speaker-label {
          color: var(--secondary);
        }

        /* AI Assistant Styles */
        .ai-assistant {
          align-self: center;
          background: rgba(139, 92, 246, 0.15);
          border: 1px solid rgba(139, 92, 246, 0.4);
          border-radius: 8px;
          margin: 0.5rem 0;
          font-style: italic;
          box-shadow: 0 4px 12px rgba(139, 92, 246, 0.2);
        }

        .ai-assistant .speaker-label {
          color: var(--accent);
          display: flex;
          align-items: center;
          gap: 0.3rem;
          }        
        
          /* Removed star icon before speaker label */
        }
      `}</style>
    </div>
  );
}

export default ChatContainer;
