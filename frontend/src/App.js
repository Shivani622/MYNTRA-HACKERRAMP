

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
import './App.css'; 

function App() {
  const [inputText, setInputText] = useState('');
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);

  const { transcript, resetTranscript, listening } = useSpeechRecognition();

  useEffect(() => {
    setInputText(transcript);
  }, [transcript]);

  const handleTextSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    try {
      const response = await axios.post('http://127.0.0.1:5000/recommend', {
        input_sentence: inputText,
      });
      setRecommendations(response.data.products);  
    } catch (error) {
      console.error('Error getting recommendations:', error);
    }
    setLoading(false);
  };

  // Function to handle voice input
  const handleVoiceCommand = () => {
    resetTranscript();
    SpeechRecognition.startListening({ continuous: true });
  };

  // Function to stop listening and get recommendations
  const stopListening = async () => {
    SpeechRecognition.stopListening();
    setLoading(true);
    try {
      const response = await axios.post('http://127.0.0.1:5000/recommend', {
        input_sentence: transcript,
      });
      setRecommendations(response.data.products); 
    } catch (error) {
      console.error('Error getting recommendations:', error);
    }
    setLoading(false);
  };

  if (!SpeechRecognition.browserSupportsSpeechRecognition()) {
    return <div>Your browser does not support speech recognition.</div>;
  }

  return (
    <div className="App">
      <nav className="navbar">
        <div className="navbar-brand">MyApp</div>
        <div className="navbar-links">
          <a href="#home">WishList</a>
          <a href="#about">Bag</a>
          <a href="#contact">Contact</a>
        </div>
      </nav>
      <h1>Voice Assistant</h1>
      <form onSubmit={handleTextSubmit}>
        < div className="button-container">

          <button className="button start-button" type="submit" disabled={loading}>
            {loading ? 'Stop Speaking' : 'Start Speaking' }
          </button>

          <button
            className="button submit-button"
            onClick={listening ? stopListening : handleVoiceCommand}
            disabled={loading}
            >
            {listening ? 'Loading...' : 'Submit'}
          </button>

          
          
          </div>
      </form>
      <div className="recommendations-container">
        {recommendations.map((rec, index) => (
          <div key={index} className="recommendation">
            <h2>Product ID: {rec.product_id}</h2>
            <h3>Name: {rec.product_name}</h3>
            <img src={rec.product_description} alt={rec.product_name} />
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;


