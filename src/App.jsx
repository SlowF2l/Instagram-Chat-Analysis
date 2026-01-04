import React from 'react';
import Header from './components/Header';
import Hero from './components/Hero';
import RecapTool from './components/RecapTool';
import './App.css';

function App() {
  return (
    <div className="App">
      <Header />
      <Hero />
      <RecapTool />
      
      <footer className="text-center py-4 text-muted mt-5 border-top">
        <div className="container">
          <p className="mb-0">&copy; 2024 ChatRecap. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
