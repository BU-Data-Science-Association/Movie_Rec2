import React, { useState, useEffect } from "react";
import "./App.css";
import { movieApi } from "./api/movieApi";

interface Card {
  id: number;
  title: string;
  description: string;
  poster_path?: string;
}

type SwipeDirection = "left" | "right" | null;

function App(): React.ReactElement {
  const [currentCard, setCurrentCard] = useState<Card | null>(null);
  const [swipeDirection, setSwipeDirection] = useState<SwipeDirection>(null);
  const [isAnimating, setIsAnimating] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [allDone, setAllDone] = useState<boolean>(false);

  // Fetch next movie recommendation
  const fetchNextMovie = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const movie = await movieApi.getNextMovie();

      // Check if backend sent "All movies seen" message
      if ((movie as any).message === "All movies seen") {
        setAllDone(true);
        setCurrentCard(null);
      } else {
        setCurrentCard(movie);
        setAllDone(false);
      }
    } catch (err) {
      setError("Failed to fetch next movie");
      console.error("API Error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch first movie on mount
  useEffect(() => {
    fetchNextMovie();
  }, []);

  const handleSwipe = async (direction: "left" | "right"): Promise<void> => {
    if (isAnimating || !currentCard) return;

    setIsAnimating(true);
    setSwipeDirection(direction);

    // Send feedback to backend (1 for like/right, -1 for dislike/left)
    const reward = direction === "right" ? 1 : -1;

    try {
      await movieApi.sendFeedback({
        movie_id: currentCard.id,
        reward: reward,
      });
      console.log(
        `Feedback sent: ${direction} (reward: ${reward}) for "${currentCard.title}"`
      );
    } catch (err) {
      console.error("Failed to send feedback:", err);
      setError("Failed to send feedback to server");
    }

    // Animate and fetch next movie
    setTimeout(async () => {
      setSwipeDirection(null);
      setIsAnimating(false);
      await fetchNextMovie();
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
        ) : allDone ? (
          <div className="end-message">
            <h2>All movies seen!</h2>
            <p>No more recommendations available.</p>
          </div>
        ) : currentCard ? (
          <div className="card-container">
            <div
              className={`card ${
                swipeDirection === "left" ? "swipe-left" : ""
              } ${swipeDirection === "right" ? "swipe-right" : ""}`}
            >
              <div className="card-content">
                {currentCard.poster_path && (
                  <div className="card-poster-container">
                    <img
                      src={`https://image.tmdb.org/t/p/w500${currentCard.poster_path}`}
                      alt={currentCard.title}
                      className="card-poster"
                      onError={(e) => {
                        e.currentTarget.style.display = "none";
                      }}
                    />
                  </div>
                )}
                <div className="card-text">
                  <h2 className="card-title">{currentCard.title}</h2>
                  <p className="card-description">{currentCard.description}</p>
                </div>
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
                disabled={isAnimating}
              >
                ✗ Dislike
              </button>
              <button
                className="action-button right-button"
                onClick={handleRightClick}
                disabled={isAnimating}
              >
                ✓ Like
              </button>
            </div>
          </div>
        ) : (
          <div className="loading">No movie available</div>
        )}
      </div>
    </div>
  );
}

export default App;
