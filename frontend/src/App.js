import React, { useState } from "react";
import axios from "axios";
import "./App.css";
import LogDisplay from "./components/LogDisplay";

const App = () => {
  const [feedbacks, setFeedbacks] = useState([]);
  const [score, setScore] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [resumeFile, setResumeFile] = useState(null);
  const [isUploadComplete, setIsUploadComplete] = useState(false);
  const [isLoadingFeedback, setIsLoadingFeedback] = useState(false);
  const [isResumeUploaded, setIsResumeUploaded] = useState(false);
  const [isJDUploaded, setIsJDUploaded] = useState(false);
  const [resume, setResume] = useState(null);
  const [jd, setJD] = useState(null);


  const handleFeedback = (id, accepted) => {
    setFeedbacks((prevFeedbacks) =>
      prevFeedbacks.map((feedback) =>
        feedback.id === id ? { ...feedback, accepted } : feedback
      )
    );
  };

  const handleDone = async () => {
    const acceptedFeedback = feedbacks.filter((feedback) => feedback.accepted === true);
    console.log("Accepted Feedback:", acceptedFeedback);

    setIsGenerating(true);

    try {
      const formData = new FormData();
      formData.append("resume", resume);
      formData.append("jd", jd);
      formData.append("feedbacks", JSON.stringify(acceptedFeedback)); // Send feedback to backend

      const response = await axios.post("http://127.0.0.1:8000/generate_resume", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      const tailoredResume = response.data.resume; // Assuming the backend returns the tailored resume

      const blob = new Blob([tailoredResume], { type: "text/markdown" });
      const fileURL = URL.createObjectURL(blob);
      setResumeFile(fileURL);
    } catch (error) {
      console.error("Error generating resume:", error);
    }

    setIsGenerating(false);
  };

  const handleFileUpload = (event, type) => {
    const file = event.target.files[0];
    alert(`File uploaded: ${file.name}`);

    if (type === "resume") {
      setIsResumeUploaded(true);
      setResume(file);
    } else if (type === "jd") {
      setIsJDUploaded(true);
      setJD(file);
    }
  };

  const handleUploadClick = async () => {
    if (isResumeUploaded && isJDUploaded) {
      setIsLoadingFeedback(true);
      // setLogs([]);

      const formData = new FormData();
      formData.append("resume", resume);
      formData.append("jd", jd);

      try {
        const response = await axios.post("http://127.0.0.1:8000/analyze", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });

        console.log("Analysis Response:", response.data);

        setScore(response.data.score);
        setFeedbacks(response.data.feedback);

        setIsLoadingFeedback(false);
        setIsUploadComplete(true);
      } catch (error) {
        console.error("Error during upload or feedback fetch:", error);
        setIsLoadingFeedback(false);
      }
    } else {
      alert("Please upload both the Resume and Job Description files.");
    }
  };

  return (
    <div className="container">
      <h1 className="title">Resume Tailor</h1>

      {/* File Upload Section */}
      {!isUploadComplete && (
        <div className="upload-section">
          <button>
            <label>
              Upload Resume
              <input
                type="file"
                onChange={(e) => handleFileUpload(e, "resume")}
                style={{ display: "none" }}
              />
            </label>
          </button>
          <button>
            <label>
              Upload Job Description
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

    {/*  <LogDisplay isAnalyzing={isLoadingFeedback} />*/}
      <LogDisplay isAnalyzing={true}/>

      {/* Display Score */}
      {score !== null && <p className="score">Score: {score}%</p>}

      {/* Feedback Section */}
      {isUploadComplete && !isLoadingFeedback && (
        <div className="feedback-section">
          <p>Review the feedback and select the changes you'd like to apply:</p>

          <div className="feedback-container">
            {feedbacks.map((feedback) => (
              <div className="feedback-item" key={feedback.id}>
                <input
                  type="text"
                  value={feedback.text}
                  readOnly
                  className="feedback-text"
                />

                <button
                  className="accept-button"
                  style={{ backgroundColor: feedback.accepted === true ? "green" : "" }}
                  onClick={() => handleFeedback(feedback.id, true)}
                >
                  ✓
                </button>

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

          {/* Resume Download Section */}
          {resumeFile ? (
            <a href={resumeFile} download="tailored_resume.md" className="download-link">
              Download Tailored Resume
            </a>
          ) : (
            <button className="done-button" onClick={handleDone} disabled={isGenerating}>
              {isGenerating ? "Generating..." : "Generate Tailored Resume"}
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default App;