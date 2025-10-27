import React, { useState } from "react";
import "./App.css";

function App() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [swipeDirection, setSwipeDirection] = useState(null);
  const [isAnimating, setIsAnimating] = useState(false);

  const cards = [
    {
      id: 1,
      image: "https://via.placeholder.com/400x500/FF6B6B/FFFFFF?text=Card+1",
      title: "Card 1",
      description: "This is the first card with some sample text.",
    },
    {
      id: 2,
      image: "https://via.placeholder.com/400x500/4ECDC4/FFFFFF?text=Card+2",
      title: "Card 2",
      description: "This is the second card with different content.",
    },
    {
      id: 3,
      image: "https://via.placeholder.com/400x500/45B7D1/FFFFFF?text=Card+3",
      title: "Card 3",
      description: "This is the third card with more information.",
    },
    {
      id: 4,
      image: "https://via.placeholder.com/400x500/96CEB4/FFFFFF?text=Card+4",
      title: "Card 4",
      description: "This is the fourth card in the deck.",
    },
    {
      id: 5,
      image: "https://via.placeholder.com/400x500/FFEAA7/333333?text=Card+5",
      title: "Card 5",
      description: "This is the fifth and final card.",
    },
  ];

  const handleSwipe = (direction) => {
    if (isAnimating || currentIndex >= cards.length) return;

    setIsAnimating(true);
    setSwipeDirection(direction);

    setTimeout(() => {
      setCurrentIndex(currentIndex + 1);
      setSwipeDirection(null);
      setIsAnimating(false);
    }, 500);
  };

  const handleLeftClick = () => {
    // Placeholder for left action (reject/dislike)
    console.log("Left button clicked");
    handleSwipe("left");
  };

  const handleRightClick = () => {
    // Placeholder for right action (accept/like)
    console.log("Right button clicked");
    handleSwipe("right");
  };

  return (
    <div className="App">
      <div className="app-container">
        <h1 className="app-title">Movie Recommender</h1>

        {currentIndex < cards.length ? (
          <div className="card-container">
            <div
              className={`card ${
                swipeDirection === "left" ? "swipe-left" : ""
              } ${swipeDirection === "right" ? "swipe-right" : ""}`}
            >
              <div className="card-image-container">
                <img
                  src={cards[currentIndex].image}
                  alt={cards[currentIndex].title}
                  className="card-image"
                />
              </div>
              <div className="card-content">
                <h2 className="card-title">{cards[currentIndex].title}</h2>
                <p className="card-description">
                  {cards[currentIndex].description}
                </p>
              </div>
              {swipeDirection && (
                <div className={`swipe-overlay ${swipeDirection}`}>
                  <div className="swipe-text">
                    {swipeDirection === "left" ? "NOPE" : "LIKE"}
                  </div>
                </div>
              )}
            </div>

            <div className="button-container">
              <button
                className="action-button left-button"
                onClick={handleLeftClick}
              >
                Left
              </button>
              <button
                className="action-button right-button"
                onClick={handleRightClick}
              >
                Right
              </button>
            </div>
          </div>
        ) : (
          <div className="end-message">
            <h2>No more cards!</h2>
            <button className="reset-button" onClick={() => setCurrentIndex(0)}>
              Reset
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
