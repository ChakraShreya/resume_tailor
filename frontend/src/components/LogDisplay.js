import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './LogDisplay.css';

const LogDisplay = ({ isAnalyzing }) => {
  const [logs, setLogs] = useState([]);
  const [expandedSteps, setExpandedSteps] = useState({});
  const [analysisResults, setAnalysisResults] = useState({
    parsedResume: null,
    parsedJD: null,
    mismatchedSkills: null,
    useCases: null
  });
  const [expandedSections, setExpandedSections] = useState({
  parsedDocs: false,
  mismatchedSkills: false,
  useCases: false
});
  const [steps, setSteps] = useState([
    {
      id: 1,
      name: 'Document Processing',
      status: 'loading',
    },
    {
      id: 2,
      name: 'Skills Comparison',
      status: 'pending',
    },
    {
      id: 3,
      name: 'Skills Research',
      status: 'pending',
    },
    {
      id: 4,
      name: 'Analysis',
      status: 'pending',
    }
  ]);
  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };
  const toggleStep = (stepId) => {
    if (steps.find(s => s.id === stepId)?.status === 'completed') {
      setExpandedSteps(prev => ({
        ...prev,
        [stepId]: !prev[stepId]
      }));
    }
  };

  // Reset everything when analysis starts/stops
  useEffect(() => {
    if (isAnalyzing) {
      setSteps(steps.map(step => ({ ...step, status: 'pending' })));
      setAnalysisResults({ parsedResume: null, parsedJD: null, mismatchedSkills: null, useCases: null });
      setExpandedSteps({});
    }
  }, [isAnalyzing]);

  // Polling logic for logs
  useEffect(() => {
    let interval;
    const fetchLogs = async () => {
      try {
        const response = await axios.get('http://localhost:8000/logs');
        setLogs(response.data.logs);
      } catch (error) {
        console.error('Error fetching logs:', error);
      }
    };

    if (isAnalyzing) {
      fetchLogs();
      interval = setInterval(fetchLogs, 1000);
    }

    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [isAnalyzing]);

  // Process logs effect
  useEffect(() => {
    if (logs && logs.length > 0) {
      const updatedSteps = [...steps];

      logs.forEach(log => {
        if (log.includes('parsing')) {
          updateStepStatus(updatedSteps, 1, 'loading');
        } else if (log.includes('Parsing complete')) {
          updateStepStatus(updatedSteps, 1, 'completed');
          if (log.includes('Resume:') || log.includes('JD:')) {
            try {
              const dataMatch = log.match(/Parsing complete - (?:Resume|JD): ({.*})/);
              if (dataMatch) {
                const parsedData = JSON.parse(dataMatch[1]);
                setAnalysisResults(prev => ({
                  ...prev,
                  [`parsed${log.includes('Resume') ? 'Resume' : 'JD'}`]: parsedData
                }));
              }
            } catch (error) {
              console.error('Error parsing document data:', error);
            }
          }
        } else if (log.includes('comparison')) {
          updateStepStatus(updatedSteps, 2, 'loading');
        } else if (log.includes('Comparison completed')) {
          updateStepStatus(updatedSteps, 2, 'completed');
          try {
            const resultsMatch = log.match(/Results: ({.*})/);
            if (resultsMatch) {
              const comparisonData = JSON.parse(resultsMatch[1]);
              setAnalysisResults(prev => ({
                ...prev,
                mismatchedSkills: comparisonData
              }));
            }
          } catch (error) {
            console.error('Error parsing comparison data:', error);
          }
        } else if (log.includes('Research completed')) {
          updateStepStatus(updatedSteps, 3, 'completed');
          try {
            const useCasesMatch = log.match(/Use Cases: ({.*})/);
            if (useCasesMatch) {
              const useCasesData = JSON.parse(useCasesMatch[1]);
              setAnalysisResults(prev => ({
                ...prev,
                useCases: useCasesData
              }));
            }
          } catch (error) {
            console.error('Error parsing use cases:', error);
          }
        } else if (log.includes('analysis')) {
          updateStepStatus(updatedSteps, 4, 'loading');
        } else if (log.includes('Analysis completed')) {
          updateStepStatus(updatedSteps, 4, 'completed');
        }
      });

      setSteps(updatedSteps);
    }
  }, [logs]);

  const updateStepStatus = (steps, stepId, status) => {
    const step = steps.find(s => s.id === stepId);
    if (step) {
      step.status = status;
    }
  };

  const getIcon = (status) => {
    switch (status) {
      case 'pending':
        return '🕐';
      case 'loading':
        return '⌛';
      case 'completed':
        return '✅';
      case 'failed':
        return '❌';
      default:
        return '🕐';
    }
  };

  const renderStepContent = (step) => {
    if (step.status !== 'completed') return null;

    switch (step.id) {
      case 1: // Document Processing
        return (
          <div className="step-details">
            <div className="parsed-data">
              <h5>Parsed Resume</h5>
              <pre>{JSON.stringify(analysisResults.parsedResume, null, 2)}</pre>
              <h5>Parsed Job Description</h5>
              <pre>{JSON.stringify(analysisResults.parsedJD, null, 2)}</pre>
            </div>
          </div>
        );

      case 2: // Skills Comparison
        return analysisResults.mismatchedSkills && (
          <div className="step-details">
            <div className="skills-comparison">
              <h5>Skills Comparison Results</h5>
              <pre>{JSON.stringify(analysisResults.mismatchedSkills, null, 2)}</pre>
            </div>
          </div>
        );

      case 3: // Skills Research
        return analysisResults.useCases && (
          <div className="step-details">
            <div className="use-cases">
              <h5>Use Cases Research</h5>
              <pre>{JSON.stringify(analysisResults.useCases, null, 2)}</pre>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  // Don't render anything if not analyzing and no results
  if (!isAnalyzing && !analysisResults.mismatchedSkills && !analysisResults.useCases) {
    return null;
  }

  return (
    <div className="log-display">
      {isAnalyzing ? (
        <>
          <h3>Analysis Progress</h3>
          <div className="steps-container">
            {steps.map((step) => (
              <div key={step.id} className={`step-item ${step.status}`}>
                <div
                  className={`step-header ${step.status === 'completed' ? 'clickable' : ''}`}
                  onClick={() => toggleStep(step.id)}
                >
                  <span className="step-icon">{getIcon(step.status)}</span>
                  <div className="step-content">
                    <span className="step-name">{step.name}</span>
                    {step.status === 'completed' && (
                      <span className="expand-icon">
                        {expandedSteps[step.id] ? '▼' : '▶'}
                      </span>
                    )}
                  </div>
                </div>
                {expandedSteps[step.id] && renderStepContent(step)}
              </div>
            ))}
          </div>
        </>
      ) : (
        analysisResults.mismatchedSkills && analysisResults.useCases && (
            <div className="analysis-results">
              <h3>Analysis Results</h3>

              <div className="results-section">
                <div
                    className="section-header clickable"
                    onClick={() => toggleSection('parsedDocs')}
                >
                  <h4>Parsed Documents</h4>
                  <span className="expand-icon">
            {expandedSections.parsedDocs ? '▼' : '▶'}
          </span>
                </div>
                {expandedSections.parsedDocs && (
                    <div className="parsed-documents-grid">
                      <div className="parsed-document">
                        <h5>Resume</h5>
                        <pre className="result-data">
                {JSON.stringify(analysisResults.parsedResume, null, 2)}
              </pre>
                      </div>
                      <div className="parsed-document">
                        <h5>Job Description</h5>
                        <pre className="result-data">
                {JSON.stringify(analysisResults.parsedJD, null, 2)}
              </pre>
                      </div>
                    </div>
                )}
              </div>

              <div className="results-section">
                <div
                    className="section-header clickable"
                    onClick={() => toggleSection('mismatchedSkills')}
                >
                  <h4>Mismatched Skills</h4>
                  <span className="expand-icon">
            {expandedSections.mismatchedSkills ? '▼' : '▶'}
          </span>
                </div>
                {expandedSections.mismatchedSkills && (
                    <pre className="result-data">
            {JSON.stringify(analysisResults.mismatchedSkills, null, 2)}
          </pre>
                )}
              </div>

              <div className="results-section">
                <div
                    className="section-header clickable"
                    onClick={() => toggleSection('useCases')}
                >
                  <h4>Skill Use Cases</h4>
                  <span className="expand-icon">
            {expandedSections.useCases ? '▼' : '▶'}
          </span>
                </div>
                {expandedSections.useCases && (
                    <pre className="result-data">
            {JSON.stringify(analysisResults.useCases, null, 2)}
          </pre>
                )}
              </div>
            </div>
        )
      )}
    </div>
  );
};

export default LogDisplay;