import React, { useState } from "react";
import "./App.css";

const App = () => {
  // mocked here
  const [feedbacks, setFeedbacks] = useState([
    { id: 1, text: "Add more specific metrics to your achievements.", accepted: null },
    { id: 2, text: "Include more keywords from the job description.", accepted: null },
    { id: 3, text: "Remove irrelevant experience from your resume.", accepted: null },
    { id: 4, text: "Highlight leadership roles in previous jobs.", accepted: null },
    { id: 5, text: "Expand details about your technical skills.", accepted: null },
    { id: 6, text: "Include recent certifications.", accepted: null },
  ]);

  const [isGenerating, setIsGenerating] = useState(false);
  const [isLoadingFeedback, setIsLoadingFeedback] = useState(false);
  const [isUploadComplete, setIsUploadComplete] = useState(false);
  const [resumeFile, setResumeFile] = useState(null);
  const [isResumeUploaded, setIsResumeUploaded] = useState(false);
  const [isJDUploaded, setIsJDUploaded] = useState(false);

  const handleFeedback = (id, accepted) => {
    setFeedbacks((prevFeedbacks) =>
      prevFeedbacks.map((feedback) =>
        feedback.id === id ? { ...feedback, accepted } : feedback
      )
    );
  };

  const handleDone = () => {
    const acceptedFeedback = feedbacks.filter((feedback) => feedback.accepted === true);
    console.log("Accepted Feedback:", acceptedFeedback);

    setIsGenerating(true);

    // Simulate backend API call to generate resume
    setTimeout(() => {
      // Mock resume
      const mockResume =`
# Resume Tailored to Job Description

### Summary
- Metrics added to achievements.
- Relevant keywords incorporated.

### Skills
- Leadership roles emphasized.
- Expanded technical skills.

### Certifications
- Added recent certifications.

---
Generated using Resume Tailor.`
      ;

      const blob = new Blob([mockResume], { type: "text/markdown" });
      const fileURL = URL.createObjectURL(blob);
      setResumeFile(fileURL);

      setIsGenerating(false);
    }, 3000); // Simulate a 3-second delay for API call
  };

  const handleFileUpload = (event, type) => {
    alert(`File uploaded: ${event.target.files[0]?.name}`);

    if (type === "resume") {
      setIsResumeUploaded(true);
    } else if (type === "jd") {
      setIsJDUploaded(true);
    }
  };

  const handleUploadClick = () => {
    if (isResumeUploaded && isJDUploaded) {
      // Simulate feedback loading
      setIsLoadingFeedback(true);
      setTimeout(() => {
        setIsLoadingFeedback(false); // Simulate feedback loading completion
        setIsUploadComplete(true); // Move to feedback phase
      }, 2000); // Simulate a 2-second delay for feedback loading
    } else {
      alert("Please upload both the Resume and Job Description files.");
    }
  };

  return (
    <div className="container">
      {/* Header Section */}
      <h1 className="title">Resume Tailor</h1>

      {/* Upload Section */}
      {!isUploadComplete && (
        <div className="upload-section">
          <button>
            <label>
              Drop Resume
              <input
                type="file"
                onChange={(e) => handleFileUpload(e, "resume")}
                style={{ display: "none" }}
              />
            </label>
          </button>
          <button>
            <label>
              Drop Job Description
              <input
                type="file"
                onChange={(e) => handleFileUpload(e, "jd")}
                style={{ display: "none" }}
              />
            </label>
          </button>
          <button className="upload-button" onClick={handleUploadClick}>
            Upload
          </button>
        </div>
      )}

      {/* Loading Screen for Feedback */}
      {isLoadingFeedback && <p className="loading-feedback">Loading feedback...</p>}

      {/* Feedback Section */}
      {isUploadComplete && !isLoadingFeedback && (
        <div className="feedback-section">
          <p>Here’s some feedback, accept the updates you’re ready to make to your skillset and resume.</p>

          {/* Scrollable container for feedback items */}
          <div className="feedback-container">
            {feedbacks.map((feedback) => (
              <div className="feedback-item" key={feedback.id}>
                {/* Display feedback text */}
                <input
                  type="text"
                  value={feedback.text}
                  readOnly
                  className="feedback-text"
                />

                {/* Accept button with dynamic styling based on selection */}
                <button
                  className="accept-button"
                  style={{ backgroundColor: feedback.accepted === true ? "green" : "" }}
                  onClick={() => handleFeedback(feedback.id, true)}
                >
                  ✓
                </button>

                {/* Reject button with dynamic styling based on selection */}
                <button
                  className="reject-button"
                  style={{ backgroundColor: feedback.accepted === false ? "red" : "" }}
                  onClick={() => handleFeedback(feedback.id, false)}
                >
                  ✗
                </button>
              </div>
            ))}
          </div>

          {/* Display loading state or download link for final resume */}
          {resumeFile ? (
            // Download link for generated resume file
            <a href={resumeFile} download="tailored_resume.md" className="download-link">
              Download Final Resume
            </a>
          ) : (
            // Button to trigger resume generation
            <button className="done-button" onClick={handleDone} disabled={isGenerating}>
              {isGenerating ? "Generating..." : "Done"}
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default App;

// import logo from './logo.svg';
// import './App.css';
//
// function App() {
//   return (
//     <div className="App">
//       <header className="App-header">
//         <img src={logo} className="App-logo" alt="logo" />
//         <p>
//           Edit <code>src/App.js</code> and save to reload.
//         </p>
//         <a
//           className="App-link"
//           href="https://reactjs.org"
//           target="_blank"
//           rel="noopener noreferrer"
//         >
//           Learn React
//         </a>
//       </header>
//     </div>
//   );
// }
//
// export default App;
