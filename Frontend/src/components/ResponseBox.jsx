function ResponseBox({ answer }) {
  return (
    <div className="response-box">
      <h2>AI Response</h2>
      <div className="answer-text">{answer}</div>
    </div>
  );
}

export default ResponseBox;
