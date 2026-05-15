import axios from "axios";

const API_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export const uploadPdf = async (file) => {

  const formData = new FormData();
  formData.append("file", file);

  const response = await axios.post(
    `${API_URL}/upload-pdf`,
    formData
  );

  return response.data;
};


export const askQuestion = async (question, documentText) => {

  const formData = new FormData();
  formData.append("query", question);
  formData.append("document_text", documentText || "");

  const response = await axios.post(
    `${API_URL}/ask-question`,
    formData
  );

  return response.data;
};