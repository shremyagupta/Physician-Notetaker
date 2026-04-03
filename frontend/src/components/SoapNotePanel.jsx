import React, { useState, useEffect, useRef } from 'react';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

function SoapNotePanel({ results, isGenerating, isEmergency }) {
    const [isEditing, setIsEditing] = useState(false);
    const [editableNote, setEditableNote] = useState(null);
    const [showAppointmentDialog, setShowAppointmentDialog] = useState(false);
    const reportRef = useRef(null);

    // Update internal state when external results change
    useEffect(() => {
        if (results && !results.error) {
            setEditableNote(JSON.parse(JSON.stringify(results)));
        }
    }, [results]);

    if (!results && !isGenerating) {
        return (
            <div className="soap-panel empty">
                <div className="empty-icon">📝</div>
                <h2>Clinical Report</h2>
                <p className="subtitle">Finish the session to generate professional medical notes in SOAP format automatically.</p>
                <style>{`
          .soap-panel.empty {
            display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; text-align: center; padding: 2rem; color: var(--text-dim);
          }
          .soap-panel.empty h2 { color: var(--text-main); margin: 1rem 0 0.5rem; }
          .subtitle { max-width: 300px; line-height: 1.5; }
          .empty-icon { font-size: 4rem; opacity: 0.4; filter: grayscale(1); }
        `}</style>
            </div>
        );
    }

    if (results?.error) {
        return (
            <div className="soap-panel error-panel">
                <h2>Error</h2>
                <p>{results.error}</p>
                <style>{`
                    .error-panel { padding: 2rem; color: #ef4444; text-align: center; }
                `}</style>
            </div>
        );
    }

    const handleEditChange = (category, field, value) => {
        setEditableNote(prev => ({
            ...prev,
            [category]: {
                ...prev[category],
                [field]: value
            }
        }));
    };

    const handleSavePdf = async () => {
        if (!reportRef.current) return;

        try {
            const element = reportRef.current;
            const canvas = await html2canvas(element, {
                scale: 2,
                useCORS: true,
                scrollY: -window.scrollY,
            });

            const imgData = canvas.toDataURL('image/png');
            const pdf = new jsPDF('p', 'mm', 'a4');
            const pdfWidth = pdf.internal.pageSize.getWidth();
            const pdfHeight = (canvas.height * pdfWidth) / canvas.width;

            let position = 0;
            let heightLeft = pdfHeight;

            // Add the first page
            pdf.addImage(imgData, 'PNG', 0, position, pdfWidth, pdfHeight);
            heightLeft -= pdf.internal.pageSize.getHeight();

            // Add extra pages if content is taller than one page
            while (heightLeft > 0) {
                position = heightLeft - pdfHeight;
                pdf.addPage();
                pdf.addImage(imgData, 'PNG', 0, position, pdfWidth, pdfHeight);
                heightLeft -= pdf.internal.pageSize.getHeight();
            }

            const filename = `medical_report_${new Date().toISOString().slice(0, 10)}.pdf`;
            pdf.save(filename);
        } catch (err) {
            console.error('Failed to save PDF:', err);
        }
    };

    const renderEditableField = (category, field, label) => {
        if (!editableNote || !editableNote[category]) return null;
        const value = editableNote[category][field] || "";
        
        return (
            <div className="form-group" key={field}>
                <label>{label}</label>
                {isEditing ? (
                    <textarea 
                        value={value} 
                        onChange={(e) => handleEditChange(category, field, e.target.value)}
                        rows={field.includes('History') || field.includes('Treatment') ? 4 : 2}
                    />
                ) : (
                    <p>{value}</p>
                )}
            </div>
        );
    };

    return (
        <div className="soap-panel filled">
            <div className="panel-header no-print">
                <div className="title-group">
                    <h2>Medical Report</h2>
                </div>
                <div className="actions">
                    <button className="action-btn print-btn" onClick={handleSavePdf} title="Save report as PDF">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                            <polyline points="7 10 12 15 17 10" />
                            <line x1="12" y1="3" x2="12" y2="15" />
                        </svg>
                    </button>
                    <button
                        className="action-btn book-btn"
                        type="button"
                        onClick={() => setShowAppointmentDialog(true)}
                        title="Book an appointment"
                    >
                        Book appointment
                    </button>
                </div>
            </div>

            <div className="report-container printable-report" ref={reportRef}>
                {isGenerating ? (
                    <div className="skeleton-loader no-print">
                        {[1, 2, 3, 4].map(i => (
                            <div key={i} style={{ marginBottom: '2rem' }}>
                                <div className="skeleton-title" style={{ height: '20px', width: '150px', background: '#e2e8f0', marginBottom: '1rem' }}></div>
                                <div className="skeleton-line" style={{ height: '12px', background: '#f1f5f9', borderRadius: '4px', marginBottom: '0.5rem' }}></div>
                                <div className="skeleton-line" style={{ height: '12px', background: '#f1f5f9', borderRadius: '4px', width: '80%' }}></div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="note-content animate-fade-in">
                        <header className="report-header">
                            {isEmergency && (
                                <div className="soap-emergency-banner no-print">
                                    <span className="icon">⚠️</span>
                                    <span>
                                        <strong>Emergency alert:</strong> This summary suggests a potentially critical
                                        condition. Ensure the patient has urgent access to in-person medical care.
                                    </span>
                                </div>
                            )}
                            <h1>Medical SOAP Note</h1>
                            <div className="patient-meta">
                                <span><strong>Patient:</strong> {editableNote?.Medical_NER?.Patient_Name || "Patient"}</span>
                                <span><strong>Date:</strong> {new Date().toLocaleDateString()}</span>
                            </div>
                        </header>

                        <div className="report-section">
                            <h3 className="section-title">SUBJECTIVE</h3>
                            {renderEditableField('SOAP_Note', 'Chief_Complaint', 'Chief Complaint')}
                            {renderEditableField('SOAP_Note', 'History_of_Present_Illness', 'History of Present Illness')}
                        </div>

                        <div className="report-section">
                            <h3 className="section-title">OBJECTIVE</h3>
                            {renderEditableField('SOAP_Note', 'Physical_Exam', 'Physical Exam Findings')}
                            {renderEditableField('SOAP_Note', 'Observations', 'Clinical Observations')}
                        </div>

                        <div className="report-section">
                            <h3 className="section-title">ASSESSMENT</h3>
                            {renderEditableField('SOAP_Note', 'Diagnosis', 'Primary Diagnosis')}
                            {renderEditableField('SOAP_Note', 'Severity', 'Clinical Severity')}

                            {/* Clinical Coding - ICD-10 */}
                            {editableNote?.Clinical_Coding?.length > 0 && (
                                <div className="coding-list">
                                    <label>ICD-10-CM Codes</label>
                                    <ul>
                                        {editableNote.Clinical_Coding.map((code, idx) => (
                                            <li key={idx}>
                                                <span className="code-tag">{code.code}</span>
                                                <span className="code-desc">{code.description}</span>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>

                        <div className="report-section">
                            <h3 className="section-title">PLAN</h3>
                            {renderEditableField('SOAP_Note', 'Treatment', 'Treatment Plan')}
                            {renderEditableField('SOAP_Note', 'Follow-Up', 'Follow-Up Instructions')}
                        </div>

                        <footer className="report-footer">
                            <p>Electronically generated and signed by AI Notetaker System</p>
                        </footer>
                    </div>
                )}
            </div>

            <style>{`
        .soap-panel { display: flex; flex-direction: column; height: 100%; border-radius: 16px; overflow: hidden; }
        .panel-header { display: flex; justify-content: space-between; align-items: center; padding: 1rem 1.5rem; background: rgba(255,255,255,0.02); border-bottom: 1px solid var(--glass-border); }
        .title-group { display: flex; align-items: center; gap: 1rem; }
        .badge { font-size: 0.65rem; padding: 0.2rem 0.5rem; background: var(--accent); color: white; border-radius: 4px; font-weight: 700; }
        
        .actions { display: flex; gap: 0.5rem; }
        .action-btn { background: rgba(255,255,255,0.05); border: 1px solid var(--glass-border); color: var(--text-dim); cursor: pointer; padding: 0.6rem; border-radius: 8px; transition: all 0.2s; display: flex; align-items: center; justify-content: center; }
        .action-btn:hover { background: rgba(255,255,255,0.1); color: white; }
        .save-btn { background: #10b981; color: white; border: none; }
        .save-btn:hover { background: #059669; }

        .book-btn { padding: 0.6rem 0.9rem; font-size: 0.85rem; font-weight: 500; }

        .report-container { flex: 1; padding: 2rem; overflow-y: auto; background: white; color: #1e293b; }
        .report-header { border-bottom: 2px solid #334155; margin-bottom: 2rem; padding-bottom: 1rem; }
        .report-header h1 { font-size: 1.5rem; color: #1e293b; margin: 0; }
        .patient-meta { display: flex; justify-content: space-between; margin-top: 1rem; font-size: 0.9rem; color: #475569; }

        .soap-emergency-banner { margin-bottom: 0.75rem; padding: 0.5rem 0.75rem; border-radius: 0.5rem; background: rgba(248, 113, 113, 0.15); border: 1px solid rgba(248, 113, 113, 0.7); color: #b91c1c; display: flex; gap: 0.5rem; align-items: flex-start; font-size: 0.85rem; }
        .soap-emergency-banner .icon { font-size: 1.1rem; }

        .report-section { margin-bottom: 2rem; }
        .section-title { font-size: 0.9rem; font-weight: 700; color: #3b82f6; letter-spacing: 0.1em; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.3rem; margin-bottom: 1rem; }
        
        .form-group { margin-bottom: 1rem; }
        .form-group label { display: block; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; color: #64748b; margin-bottom: 0.4rem; }
        .form-group p { font-size: 0.95rem; margin: 0; white-space: pre-wrap; line-height: 1.6; color: #334155; }
        .form-group textarea { width: 100%; padding: 0.8rem; border: 1px solid #cbd5e1; border-radius: 6px; font-family: inherit; font-size: 0.95rem; background: #f8fafc; color: #334155; resize: vertical; }
        .form-group textarea:focus { outline: none; border-color: #3b82f6; ring: 2px #3b82f6; }

        .coding-list { background: #f1f5f9; padding: 1rem; border-radius: 8px; margin-top: 1rem; }
        .coding-list label { display: block; font-size: 0.75rem; font-weight: 600; color: #64748b; margin-bottom: 0.5rem; }
        .coding-list ul { list-style: none; padding: 0; margin: 0; }
        .coding-list li { display: flex; align-items: center; gap: 0.8rem; margin-bottom: 0.4rem; font-size: 0.9rem; }
        .code-tag { background: #3b82f6; color: white; padding: 0.1rem 0.4rem; border-radius: 4px; font-weight: 700; font-family: monospace; }
        .code-desc { color: #334155; }

        .report-footer { margin-top: 4rem; padding-top: 1rem; border-top: 1px solid #e2e8f0; font-size: 0.8rem; color: #94a3b8; text-align: center; }

        .appointment-dialog-backdrop { position: fixed; inset: 0; background: rgba(15,23,42,0.55); display: flex; align-items: center; justify-content: center; z-index: 40; }
        .appointment-dialog { background: #0f172a; border-radius: 12px; padding: 1.5rem; width: 100%; max-width: 360px; box-shadow: 0 20px 40px rgba(15,23,42,0.6); color: #e5e7eb; }
        .appointment-dialog h3 { margin: 0 0 0.5rem; font-size: 1.05rem; }
        .appointment-dialog p { margin: 0 0 1rem; font-size: 0.9rem; color: #9ca3af; }
        .appointment-options { display: flex; flex-direction: column; gap: 0.5rem; margin-bottom: 1rem; }
        .appointment-link { display: block; width: 100%; text-align: center; padding: 0.6rem 0.9rem; border-radius: 8px; text-decoration: none; font-size: 0.9rem; font-weight: 500; }
        .appointment-link.propto { background: #3b82f6; color: white; }
        .appointment-link.propto:hover { background: #2563eb; }
        .appointment-link.lybrate { background: #f97316; color: white; }
        .appointment-link.lybrate:hover { background: #ea580c; }
        .appointment-dialog-actions { display: flex; justify-content: flex-end; }
        .appointment-cancel-btn { background: transparent; border: none; color: #9ca3af; font-size: 0.85rem; cursor: pointer; padding: 0.3rem 0.6rem; }
        .appointment-cancel-btn:hover { color: #e5e7eb; }

        @media print {
          .no-print { display: none !important; }
          .soap-panel { height: auto; display: block; }
          .report-container { padding: 0; overflow: visible; }
          .printable-report { color: black !important; background: white !important; width: 100% !important; }
          @page { margin: 2cm; }
        }

        .skeleton-loader { animation: pulse 1.5s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 0.5; } 50% { opacity: 1; } }
      `}</style>
            {showAppointmentDialog && (
                <div className="appointment-dialog-backdrop" onClick={() => setShowAppointmentDialog(false)}>
                    <div className="appointment-dialog" onClick={(e) => e.stopPropagation()}>
                        <h3>Book appointment</h3>
                        <p>Select a platform to continue your booking.</p>
                        <div className="appointment-options">
                            <a
                                href="https://www.practo.com"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="appointment-link propto"
                            >
                                Book on Propto
                            </a>
                            <a
                                href="https://www.lybrate.com"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="appointment-link lybrate"
                            >
                                Book on Lybrate
                            </a>
                        </div>
                        <div className="appointment-dialog-actions">
                            <button
                                type="button"
                                className="appointment-cancel-btn"
                                onClick={() => setShowAppointmentDialog(false)}
                            >
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default SoapNotePanel;
