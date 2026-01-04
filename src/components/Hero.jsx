import React from 'react';

const Hero = () => {
  return (
    <div className="bg-light text-center py-5 mb-5">
      <div className="container py-5">
        <h1 className="display-4 fw-bold mb-3">Make Sense of Your Chats</h1>
        <p className="lead mb-4 text-muted">
          Instantly summarize long conversation threads, extract action items, and get clarity with AI-powered analysis.
        </p>
        <a href="#tool" className="btn btn-primary btn-lg px-5">
          Try It Now
        </a>
      </div>
    </div>
  );
};

export default Hero;
