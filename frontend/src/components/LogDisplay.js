import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './LogDisplay.css';

const LogDisplay = ({ isAnalyzing }) => {
  const [logs, setLogs] = useState([]);
  const [analysisResults, setAnalysisResults] = useState({
    mismatchedSkills: null,
    useCases: null
  });
  const [steps, setSteps] = useState([
    {
      id: 1,
      name: 'Document Processing',
      status: 'pending',
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

  // Reset everything when analysis starts/stops
  useEffect(() => {
    if (isAnalyzing) {
      setSteps(steps.map(step => ({ ...step, status: 'pending' })));
      setAnalysisResults({ mismatchedSkills: null, useCases: null });
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
        if (log.includes('Parsing')) {
          updateStepStatus(updatedSteps, 1, 'loading');
        } else if (log.includes('Parsing complete')) {
          updateStepStatus(updatedSteps, 1, 'completed');
        } else if (log.includes('comparison')) {
          updateStepStatus(updatedSteps, 2, 'loading');
        } else if (log.includes('Comparison completed')) {
          updateStepStatus(updatedSteps, 2, 'completed');
          // Extract mismatched skills
          if (log.includes('Identified mismatched skills:')) {
            try {
              console.log("here")
              const skillsMatch = log.match(/Identified mismatched skills: ({.*})/);
              console.log(skillsMatch)
              if (skillsMatch) {
                const skillsData = JSON.parse(skillsMatch[1]);
                console.log(skillsData)
                setAnalysisResults(prev => ({
                  ...prev,
                  mismatchedSkills: skillsData
                }));
              }
            } catch (error) {
              console.error('Error parsing skills data:', error);
            }
          }
        } else if (log.includes('missing skills') || log.includes('research')) {
          updateStepStatus(updatedSteps, 3, 'loading');
        } else if (log.includes('Research completed')) {
          updateStepStatus(updatedSteps, 3, 'completed');
          if (log.includes('Use Cases :')) {
            try {
              const useCasesMatch = log.match(/Use Cases : ({.*})/);
              console.log(useCasesMatch)
              if (useCasesMatch) {
                const useCasesData = JSON.parse(useCasesMatch[1]);
                console.log(useCasesData)
                setAnalysisResults(prev => ({
                  ...prev,
                  useCases: useCasesData
                }));
              }
            } catch (error) {
              console.error('Error parsing use cases:', error);
            }
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
                <span className="step-icon">{getIcon(step.status)}</span>
                <div className="step-content">
                  <span className="step-name">{step.name}</span>
                </div>
              </div>
            ))}
          </div>
        </>
      ) : (
        analysisResults.mismatchedSkills && analysisResults.useCases && (
          <div className="analysis-results">
            <h3>Analysis Results</h3>
            <div className="results-section">
              <h4>Mismatched Skills</h4>
              <pre className="result-data">
                {JSON.stringify(analysisResults.mismatchedSkills, null, 2)}
              </pre>
            </div>
            <div className="results-section">
              <h4>Skill Use Cases</h4>
              <pre className="result-data">
                {JSON.stringify(analysisResults.useCases, null, 2)}
              </pre>
            </div>
          </div>
        )
      )}
    </div>
  );
};

export default LogDisplay;