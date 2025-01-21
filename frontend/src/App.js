import React, { useState } from "react";
import axios from "axios";
import "./App.css";

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
    formData.append("feedbacks", JSON.stringify(acceptedFeedback)); // Add feedbacks as JSON string

    const response = await axios.post("http://127.0.0.1:8000/generate_resume", formData, {
      headers: {
        "Content-Type": "multipart/form-data", // Ensure the content type is multipart/form-data
      },
    });

    const mockResume = response.data.resume;

    const blob = new Blob([mockResume], { type: "text/markdown" });
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

      // Simulate score calculation by sending the resume and JD files to the backend
      const formData = new FormData();
      formData.append("resume", resume);
      formData.append("jd", jd);

      try {
        const scoreResponse = await axios.post("http://127.0.0.1:8000/score", formData);
        setScore(scoreResponse.data.score);
        setIsLoadingFeedback(false);

        // Fetch feedback after getting the score
        const feedbackResponse = await axios.get("http://127.0.0.1:8000/feedbacks");
        setFeedbacks(feedbackResponse.data);

        setIsUploadComplete(true); // Move to feedback phase
      } catch (error) {
        console.error("Error during upload or feedback fetch:", error);
      }
    } else {
      alert("Please upload both the Resume and Job Description files.");
    }
  };

  return (
    <div className="container">
      <h1 className="title">Resume Tailor</h1>

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

      {isLoadingFeedback && <p className="loading-feedback">Loading feedback...</p>}

      {score && <p>Score: {score}</p>}

      {isUploadComplete && !isLoadingFeedback && (
        <div className="feedback-section">
          <p>Here’s some feedback, accept the updates you’re ready to make to your skillset and resume.</p>

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

          {resumeFile ? (
            <a href={resumeFile} download="tailored_resume.md" className="download-link">
              Download Final Resume
            </a>
          ) : (
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




// import React, { useState } from "react";
// import "./App.css";
//
// const App = () => {
//   // mocked here
//   const [feedbacks, setFeedbacks] = useState([
//     { id: 1, text: "Add more specific metrics to your achievements.", accepted: null },
//     { id: 2, text: "Include more keywords from the job description.", accepted: null },
//     { id: 3, text: "Remove irrelevant experience from your resume.", accepted: null },
//     { id: 4, text: "Highlight leadership roles in previous jobs.", accepted: null },
//     { id: 5, text: "Expand details about your technical skills.", accepted: null },
//     { id: 6, text: "Include recent certifications.", accepted: null },
//   ]);
//
//   const [isGenerating, setIsGenerating] = useState(false);
//   const [isLoadingFeedback, setIsLoadingFeedback] = useState(false);
//   const [isUploadComplete, setIsUploadComplete] = useState(false);
//   const [resumeFile, setResumeFile] = useState(null);
//   const [isResumeUploaded, setIsResumeUploaded] = useState(false);
//   const [isJDUploaded, setIsJDUploaded] = useState(false);
//
//   const handleFeedback = (id, accepted) => {
//     setFeedbacks((prevFeedbacks) =>
//       prevFeedbacks.map((feedback) =>
//         feedback.id === id ? { ...feedback, accepted } : feedback
//       )
//     );
//   };
//
//   const handleDone = () => {
//     const acceptedFeedback = feedbacks.filter((feedback) => feedback.accepted === true);
//     console.log("Accepted Feedback:", acceptedFeedback);
//
//     setIsGenerating(true);
//
//     // Simulate backend API call to generate resume
//     setTimeout(() => {
//       // Mock resume
//       const mockResume =`
// # Resume Tailored to Job Description
//
// ### Summary
// - Metrics added to achievements.
// - Relevant keywords incorporated.
//
// ### Skills
// - Leadership roles emphasized.
// - Expanded technical skills.
//
// ### Certifications
// - Added recent certifications.
//
// ---
// Generated using Resume Tailor.`
//       ;
//
//       const blob = new Blob([mockResume], { type: "text/markdown" });
//       const fileURL = URL.createObjectURL(blob);
//       setResumeFile(fileURL);
//
//       setIsGenerating(false);
//     }, 3000); // Simulate a 3-second delay for API call
//   };
//
//   const handleFileUpload = (event, type) => {
//     alert(`File uploaded: ${event.target.files[0]?.name}`);
//
//     if (type === "resume") {
//       setIsResumeUploaded(true);
//     } else if (type === "jd") {
//       setIsJDUploaded(true);
//     }
//   };
//
//   const handleUploadClick = () => {
//     if (isResumeUploaded && isJDUploaded) {
//       // Simulate feedback loading
//       setIsLoadingFeedback(true);
//       setTimeout(() => {
//         setIsLoadingFeedback(false); // Simulate feedback loading completion
//         setIsUploadComplete(true); // Move to feedback phase
//       }, 2000); // Simulate a 2-second delay for feedback loading
//     } else {
//       alert("Please upload both the Resume and Job Description files.");
//     }
//   };
//
//   return (
//     <div className="container">
//       {/* Header Section */}
//       <h1 className="title">Resume Tailor</h1>
//
//       {/* Upload Section */}
//       {!isUploadComplete && (
//         <div className="upload-section">
//           <button>
//             <label>
//               Drop Resume
//               <input
//                 type="file"
//                 onChange={(e) => handleFileUpload(e, "resume")}
//                 style={{ display: "none" }}
//               />
//             </label>
//           </button>
//           <button>
//             <label>
//               Drop Job Description
//               <input
//                 type="file"
//                 onChange={(e) => handleFileUpload(e, "jd")}
//                 style={{ display: "none" }}
//               />
//             </label>
//           </button>
//           <button className="upload-button" onClick={handleUploadClick}>
//             Upload
//           </button>
//         </div>
//       )}
//
//       {/* Loading Screen for Feedback */}
//       {isLoadingFeedback && <p className="loading-feedback">Loading feedback...</p>}
//
//       {/* Feedback Section */}
//       {isUploadComplete && !isLoadingFeedback && (
//         <div className="feedback-section">
//           <p>Here’s some feedback, accept the updates you’re ready to make to your skillset and resume.</p>
//
//           {/* Scrollable container for feedback items */}
//           <div className="feedback-container">
//             {feedbacks.map((feedback) => (
//               <div className="feedback-item" key={feedback.id}>
//                 {/* Display feedback text */}
//                 <input
//                   type="text"
//                   value={feedback.text}
//                   readOnly
//                   className="feedback-text"
//                 />
//
//                 {/* Accept button with dynamic styling based on selection */}
//                 <button
//                   className="accept-button"
//                   style={{ backgroundColor: feedback.accepted === true ? "green" : "" }}
//                   onClick={() => handleFeedback(feedback.id, true)}
//                 >
//                   ✓
//                 </button>
//
//                 {/* Reject button with dynamic styling based on selection */}
//                 <button
//                   className="reject-button"
//                   style={{ backgroundColor: feedback.accepted === false ? "red" : "" }}
//                   onClick={() => handleFeedback(feedback.id, false)}
//                 >
//                   ✗
//                 </button>
//               </div>
//             ))}
//           </div>
//
//           {/* Display loading state or download link for final resume */}
//           {resumeFile ? (
//             // Download link for generated resume file
//             <a href={resumeFile} download="tailored_resume.md" className="download-link">
//               Download Final Resume
//             </a>
//           ) : (
//             // Button to trigger resume generation
//             <button className="done-button" onClick={handleDone} disabled={isGenerating}>
//               {isGenerating ? "Generating..." : "Done"}
//             </button>
//           )}
//         </div>
//       )}
//     </div>
//   );
// };
//
// export default App;
