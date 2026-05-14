import React from "react";

function QuestionInput({ question, setQuestion }) {

  return (
    <div>
      <h3>Ask Question</h3>

      <input
        type="text"
        placeholder="Enter your question"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        style={{ width: "300px", padding: "8px" }}
      />
    </div>
  );
}

export default QuestionInput;