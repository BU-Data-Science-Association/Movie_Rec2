import React, { useState, useEffect } from "react";
import "./App.css";
import { movieApi } from "./api/movieApi";

interface Card {
  id: number;
  image: string;
  title: string;
  description: string;
}

type SwipeDirection = "left" | "right" | null;

function App(): React.ReactElement {
  const [currentIndex, setCurrentIndex] = useState<number>(0);
  const [swipeDirection, setSwipeDirection] = useState<SwipeDirection>(null);
  const [isAnimating, setIsAnimating] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const cards: Card[] = [
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

  // Example: Fetch data from FastAPI on component mount
  useEffect(() => {
    const fetchApiData = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // Example API call to test connection
        const response = await movieApi.getHello();
        console.log("FastAPI says:", response.message);

        // You can fetch cards here instead of using hardcoded data
        // const fetchedCards = await movieApi.getCards();
        // setCards(fetchedCards);
      } catch (err) {
        setError("Failed to connect to API server");
        console.error("API Error:", err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchApiData();
  }, []);

  const handleSwipe = async (direction: "left" | "right"): Promise<void> => {
    if (isAnimating || currentIndex >= cards.length) return;

    setIsAnimating(true);
    setSwipeDirection(direction);

    // Optional: Send swipe data to FastAPI server
    try {
      await movieApi.recordSwipe({
        cardId: cards[currentIndex].id,
        direction: direction,
        timestamp: new Date().toISOString(),
      });
      console.log(
        `Swipe ${direction} recorded for card ${cards[currentIndex].id}`
      );
    } catch (err) {
      console.error("Failed to record swipe:", err);
    }

    setTimeout(() => {
      setCurrentIndex(currentIndex + 1);
      setSwipeDirection(null);
      setIsAnimating(false);
    }, 500);
  };

  const handleLeftClick = (): void => {
    // Left action (reject/dislike)
    console.log("Left button clicked");
    handleSwipe("left");
  };

  const handleRightClick = (): void => {
    // Right action (accept/like)
    console.log("Right button clicked");
    handleSwipe("right");
  };

  return (
    <div className="App">
      <div className="app-container">
        <h1 className="app-title">Movie Recommender</h1>

        {error && (
          <div
            className="error-message"
            style={{
              color: "white",
              background: "rgba(255, 0, 0, 0.7)",
              padding: "10px",
              borderRadius: "8px",
              marginBottom: "20px",
            }}
          >
            {error}
          </div>
        )}

        {isLoading ? (
          <div
            className="loading"
            style={{ color: "white", fontSize: "1.5rem" }}
          >
            Loading...
          </div>
        ) : currentIndex < cards.length ? (
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
