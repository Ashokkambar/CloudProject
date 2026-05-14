import React from "react";

function PdfUploader({ file, setFile }) {

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    setFile(selectedFile);
  };

  return (
    <div>


      {file ? (
        <p>Uploaded File: {file.name}</p>
      ) : (
        <input
          type="file"
          accept="application/pdf"
          onChange={handleFileChange}
        />
      )}

    </div>
  );
}

export default PdfUploader;