import React, { useState } from 'react';

const RecapTool = () => {
  const [inputText, setInputText] = useState('');
  const [summary, setSummary] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSummarize = () => {
    if (!inputText.trim()) return;

    setIsLoading(true);
    setSummary(null);

    // Simulate API call
    setTimeout(() => {
      const mockSummary = `
        <strong>Key Points:</strong><br/>
        - The conversation started with a greeting.<br/>
        - Main topic appears to be related to: "${inputText.slice(0, 20)}..."<br/>
        - Consensus reached on next steps.<br/><br/>
        <strong>Action Items:</strong><br/>
        - Review the documents.<br/>
        - Schedule a follow-up meeting.
      `;
      setSummary(mockSummary);
      setIsLoading(false);
    }, 1500);
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setInputText(e.target.result);
      };
      reader.readAsText(file);
    }
  };

  return (
    <div id="tool" className="container mb-5">
      <div className="row justify-content-center">
        <div className="col-lg-8">
          <div className="card shadow-sm">
            <div className="card-header bg-white">
              <h3 className="h5 mb-0">Chat Summarizer</h3>
            </div>
            <div className="card-body">
              <div className="mb-3">
                <label htmlFor="chatInput" className="form-label">Paste conversation log here</label>
                <textarea
                  className="form-control"
                  id="chatInput"
                  rows="6"
                  placeholder="[10:00] Alice: Hey Bob, did you see the report?..."
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                ></textarea>
              </div>
              <button 
                className="btn btn-primary w-100 mb-2" 
                onClick={handleSummarize}
                disabled={isLoading || !inputText.trim()}
              >
                {isLoading ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Analyzing...
                  </>
                ) : 'Summarize'}
              </button>
              <div className="input-group">
                <input 
                  type="file" 
                  className="form-control" 
                  id="chatFileUpload" 
                  accept=".txt,.log"
                  onChange={handleFileUpload}
                  disabled={isLoading}
                />
                <button 
                  className="btn btn-outline-secondary" 
                  type="button" 
                  onClick={() => document.getElementById('chatFileUpload').click()}
                  disabled={isLoading}
                >
                  Upload Chat Log
                </button>
              </div>
            </div>
            {summary && (
              <div className="card-footer bg-light">
                <h5 className="h6">Summary Result:</h5>
                <div className="alert alert-success mb-0" dangerouslySetInnerHTML={{ __html: summary }}></div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RecapTool;
