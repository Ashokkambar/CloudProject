import { useState } from "react";

import PdfUploader from "../components/PdfUploader";
import QuestionInput from "../components/QuestionInput";
import ResponseBox from "../components/ResponseBox";

import "../styles/main.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

function Home() {

  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [uploaded, setUploaded] = useState(false);
  const [documentText, setDocumentText] = useState("");

  const handleUpload = async () => {

    if (!file) {
      alert("Please select a PDF file");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {

      const response = await fetch(`${API_BASE_URL}/upload-pdf`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (data.error) {
        setAnswer(data.error);
        setUploaded(false);
        setDocumentText("");
        return;
      }

      setDocumentText(data.document_text || "");
      setAnswer(data.message || "PDF uploaded successfully.");
      setUploaded(true);

    } catch (error) {

      setAnswer("Error uploading PDF");
    }
  };

  const handleAsk = async () => {

    if (!question) {
      alert("Please enter a question");
      return;
    }

    if (!documentText) {
      alert("Please upload a readable PDF first");
      return;
    }

    try {

      const formData = new FormData();

      formData.append("query", question);
      formData.append("document_text", documentText);

      const response = await fetch(`${API_BASE_URL}/ask-question`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      setAnswer(data.answer);

    } catch (error) {

      setAnswer("Error asking AI");
    }
  };

  return (

    <div className="container">

      <div className="content-box">

        <h1 className="main-title">
          PDF AI Assistant
        </h1>

        <PdfUploader
          file={file}
          setFile={setFile}
        />

        <br />

        <button onClick={handleUpload}>
          {uploaded ? "Re-upload PDF" : "Upload PDF"}
        </button>

        <br /><br />

        <QuestionInput
          question={question}
          setQuestion={setQuestion}
        />

        <br />

        <button onClick={handleAsk}>
          Ask AI
        </button>

        <ResponseBox answer={answer} />

      </div>

    </div>
  );
}

export default Home;
