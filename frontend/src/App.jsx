import React, { useEffect, useState } from 'react';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import Header from './components/Header';
import ChatContainer from './components/ChatContainer';
import MessageInput from './components/MessageInput';
import SoapNotePanel from './components/SoapNotePanel';

function App() {
  const [messages, setMessages] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSuggesting, setIsSuggesting] = useState(false);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [isEmergencyCase, setIsEmergencyCase] = useState(false);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [patientProfile, setPatientProfile] = useState({
    name: '',
    age: '',
    weight: '',
    mainProblem: '',
    symptoms: '',
  });

  const autoDownloadReport = async () => {
    try {
      const element = document.querySelector('.printable-report');
      if (!element) return;

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

      pdf.addImage(imgData, 'PNG', 0, position, pdfWidth, pdfHeight);
      heightLeft -= pdf.internal.pageSize.getHeight();

      while (heightLeft > 0) {
        position = heightLeft - pdfHeight;
        pdf.addPage();
        pdf.addImage(imgData, 'PNG', 0, position, pdfWidth, pdfHeight);
        heightLeft -= pdf.internal.pageSize.getHeight();
      }

      const filename = `medical_report_${new Date().toISOString().slice(0, 10)}.pdf`;
      pdf.save(filename);
    } catch (err) {
      console.error('Failed to auto-download medical report:', err);
    }
  };

  const questionSteps = [
    {
      id: 'name',
      minLength: 3,
      allowYesNo: false,
      text: () =>
        "Hello, I'm your virtual doctor. To begin, may I have your full name?",
    },
    {
      id: 'age',
      minLength: 1,
      allowYesNo: false,
      text: (profile) =>
        profile.name
          ? `Thank you, ${profile.name}. How old are you?`
          : 'How old are you?',
    },
    {
      id: 'weight',
      minLength: 1,
      allowYesNo: false,
      text: () =>
        'What is your current weight? You can answer in kilograms or pounds.',
    },
    {
      id: 'mainProblem',
      minLength: 5,
      allowYesNo: false,
      text: () => 'What brings you in today? What is the main problem?',
    },
    {
      id: 'symptoms',
      minLength: 10,
      allowYesNo: false,
      text: () =>
        'Please describe your main symptoms in as much detail as you can.',
    },
    {
      id: 'duration',
      minLength: 3,
      allowYesNo: false,
      text: () => 'When did these symptoms start?',
    },
    {
      id: 'triggers',
      minLength: 5,
      allowYesNo: false,
      text: () =>
        'Have you noticed anything that makes the symptoms better or worse?',
    },
    {
      id: 'history',
      minLength: 5,
      allowYesNo: false,
      text: () =>
        'Do you have any long-term medical conditions or take regular medicines?',
    },
    {
      id: 'allergies',
      minLength: 0,
      allowYesNo: true,
      text: () =>
        'Do you have any allergies to medicines or foods that you know of?',
    },
    {
      id: 'other',
      minLength: 5,
      allowYesNo: false,
      text: () =>
        'Is there anything else you would like me to know about how you are feeling?',
    },
    {
      id: 'closing',
      text: (profile) =>
        profile.name
          ? `Thank you, ${profile.name}. I will now summarise your case and prepare your notes and suggestions.`
          : 'Thank you for the information. I will now summarise your case and prepare your notes and suggestions.',
    },
  ];

  // Start a scripted doctor-led conversation when the app loads
  useEffect(() => {
    const firstStep = questionSteps[0];
    setMessages([
      {
        speaker: 'Doctor',
        text: firstStep.text(patientProfile),
        timestamp: new Date(),
      },
    ]);
    setCurrentStepIndex(0);
    setAnalysisResults(null);
  }, []);

  const handleSendMessage = (message) => {
    setMessages((prev) => [...prev, message]);

    if (message.speaker === 'Patient') {
      setCurrentStepIndex((prevIndex) => {
        const step = questionSteps[prevIndex] || {};
        const rawAnswer = message.text || '';
        const answer = rawAnswer.trim();
        const compact = answer.replace(/\s+/g, '');
        const lower = answer.toLowerCase();

        const isYesNo = ['yes', 'no', 'y', 'n', 'yeah', 'nope'].includes(lower);
        const minLength = typeof step.minLength === 'number' ? step.minLength : 0;
        const allowYesNo = !!step.allowYesNo;

        const isGarbage =
          minLength > 0 &&
          compact.length < minLength &&
          !(allowYesNo && isYesNo);

        if (isGarbage) {
          // Repeat the same question after a short pause
          setTimeout(() => {
            setMessages((prevMessages) => [
              ...prevMessages,
              {
                speaker: 'Doctor',
                text: `I didn't fully understand your answer. ${step.text({ ...patientProfile })}`,
                timestamp: new Date(),
              },
            ]);
          }, 1000);
          return prevIndex;
        }

        // Valid answer: store basic profile details
        setPatientProfile((prevProfile) => {
          const updated = { ...prevProfile };
          if (step.id === 'name') {
            updated.name = answer;
          } else if (step.id === 'age') {
            updated.age = answer;
          } else if (step.id === 'weight') {
            updated.weight = answer;
          } else if (step.id === 'mainProblem') {
            updated.mainProblem = answer;
          } else if (step.id === 'symptoms') {
            updated.symptoms = answer;
          }
          return updated;
        });

        const nextIndex = prevIndex + 1;

        if (nextIndex >= 0 && nextIndex < questionSteps.length) {
          const nextStep = questionSteps[nextIndex];
          const isClosing = nextStep.id === 'closing';

          // Ask the next doctor question after a 1 second wait
          setTimeout(() => {
            setMessages((prevMessages) => {
              const nextText = nextStep.text({ ...patientProfile });

              // Avoid posting the same doctor question twice in a row
              const last = prevMessages[prevMessages.length - 1];
              if (last && last.speaker === 'Doctor' && last.text === nextText) {
                return prevMessages;
              }

              const updatedMessages = [
                ...prevMessages,
                {
                  speaker: 'Doctor',
                  text: nextText,
                  timestamp: new Date(),
                },
              ];

              if (isClosing) {
                // After the closing message, automatically generate the report
                setTimeout(() => {
                  handleEndSession(updatedMessages);
                }, 1500);
              }

              return updatedMessages;
            });
          }, 1000);

          return nextIndex;
        }

        // No more scripted questions: generate the report automatically
        setTimeout(() => {
          handleEndSession();
        }, 1000);

        return prevIndex;
      });
    }
  };

  const computeEmergencyFromResults = (results) => {
    if (!results) return false;

    const diagnosis = (results.SOAP_Note && results.SOAP_Note.Diagnosis) ||
                      (results.Medical_NER && results.Medical_NER.Diagnosis) ||
                      '';
    const nerSymptomsArray = (results.Medical_NER && results.Medical_NER.Symptoms) || [];
    const nerSymptoms = Array.isArray(nerSymptomsArray) ? nerSymptomsArray.join(' ') : String(nerSymptomsArray || '');
    const severity = (results.SOAP_Note && results.SOAP_Note.Severity) || '';

    const textToScan = `${diagnosis} ${nerSymptoms} ${severity}`.toLowerCase();

    const criticalKeywords = [
      'cancer',
      'carcinoma',
      'blood cancer',
      'leukemia',
      'vomiting blood',
      'blood vomit',
      'hematemesis',
      'chest pain',
      'shortness of breath',
      'difficulty breathing',
      'severe abdominal pain',
      'stroke',
      'paralysis',
      'shock',
      'septic',
      'critical',
      'life-threatening',
      'icu',
    ];

    return criticalKeywords.some((kw) => textToScan.includes(kw));
  };

  const handleSuggestMedicine = async () => {
    if (messages.length === 0) return;
    setIsSuggesting(true);
    try {
      const transcriptText = messages.map(msg => `${msg.speaker}: ${msg.text}`).join('\n');

      const response = await fetch('http://localhost:8000/api/suggest-medicine', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ transcript: transcriptText })
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();

      if (data.suggestion) {
        handleSendMessage({
          speaker: 'AI Assistant',
          text: data.suggestion,
          timestamp: new Date()
        });
      }
    } catch (error) {
      console.error("Failed to get suggestion:", error);
      handleSendMessage({
        speaker: 'AI Assistant',
        text: `Error: Could not retrieve suggestion. ${error.message}`,
        timestamp: new Date()
      });
    } finally {
      setIsSuggesting(false);
    }
  };

  const handleEndSession = async (finalMessages = null) => {
    const sourceMessages = finalMessages || messages;
    if (!sourceMessages || sourceMessages.length === 0) return;

    setIsGenerating(true);

    try {
      // Build the transcript text from the messages array
      const transcriptText = sourceMessages.map(msg => `${msg.speaker}: ${msg.text}`).join('\n');

      const response = await fetch('http://localhost:8000/api/generate-notes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ transcript: transcriptText })
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();

      // Update the UI with the complete results object
      if (data.results) {
        setAnalysisResults(data.results);
        setIsEmergencyCase(computeEmergencyFromResults(data.results));
        // Automatically download the complete medical report once it is generated
        setTimeout(() => {
          autoDownloadReport();
        }, 800);
      } else {
        setAnalysisResults({ error: "Error: Could not retrieve analysis results from the server." });
      }
    } catch (error) {
      console.error("Failed to generate notes:", error);
      setAnalysisResults({
        error: `Error: Could not connect to the backend server. Make sure it is running on http://localhost:8000.\\n\\nDetails: ${error.message}`,
      });
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className={`app-layout ${isEmergencyCase ? 'emergency-mode' : ''}`}>
      <Header />
      <main className="main-content">
        {isEmergencyCase && (
          <div className="emergency-banner no-print">
            <span style={{ fontSize: '1.1rem' }}>⚠️</span>
            <div>
              <strong>Emergency notice:</strong> Based on the reported symptoms, this case may
              require urgent in-person medical assessment. This tool is for documentation
              support only and is not a substitute for emergency care.
            </div>
          </div>
        )}
          <div className="workspace">
          {/* Left panel: Chat Interface */}
          <div className="chat-panel glass-panel">
            <ChatContainer messages={messages} />
            <MessageInput
              onSendMessage={handleSendMessage}
              onEndSession={handleEndSession}
              isGenerating={isGenerating}
              isSuggesting={isSuggesting}
              onSuggestMedicine={handleSuggestMedicine}
            />
          </div>

          {/* Right panel: SOAP Note Results */}
          <div className="results-panel glass-panel">
            <SoapNotePanel
              results={analysisResults}
              isGenerating={isGenerating}
              isEmergency={isEmergencyCase}
            />
          </div>
        </div>
      </main>

      <style>{`
        .app-layout {
          display: flex;
          flex-direction: column;
          height: 100vh;
          overflow: hidden;
        }
        .app-layout.emergency-mode {
          background:
            radial-gradient(circle at top, rgba(248, 113, 113, 0.22), transparent 55%),
            radial-gradient(circle at bottom, rgba(127, 29, 29, 0.18), rgba(15, 23, 42, 1));
        }
        
        .main-content {
          flex: 1;
          padding: 1.5rem;
          height: calc(100vh - 70px);
        }

        .emergency-banner {
          max-width: 1600px;
          margin: 0 auto 0.75rem;
          padding: 0.75rem 1rem;
          border-radius: 0.75rem;
          border: 1px solid rgba(248, 113, 113, 0.9);
          background: rgba(127, 29, 29, 0.55);
          color: #fee2e2;
          font-size: 0.9rem;
          display: flex;
          gap: 0.6rem;
          align-items: flex-start;
        }

        .workspace {
          display: flex;
          gap: 1.5rem;
          height: 100%;
          max-width: 1600px;
          margin: 0 auto;
        }

        .chat-panel {
          flex: 1;
          display: flex;
          flex-direction: column;
          height: 100%;
          overflow: hidden;
        }

        .results-panel {
          flex: 1;
          display: flex;
          flex-direction: column;
          height: 100%;
          overflow: hidden;
        }

        @media (max-width: 1024px) {
          .workspace {
            flex-direction: column;
          }
          .main-content {
            height: auto;
            overflow-y: auto;
          }
          .chat-panel, .results-panel {
            flex: none;
            height: 600px;
            margin-bottom: 1rem;
          }
        }
      `}</style>
    </div>
  );
}

export default App;
