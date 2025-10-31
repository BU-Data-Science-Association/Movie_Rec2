import { useState, useEffect } from "react";

function App() {
  const [movie, setMovie] = useState(null);
  const [loading, setLoading] = useState(true);

  // Fetch next recommended movie from FastAPI
  async function fetchNext() {
    setLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/next");
      const data = await res.json();
      setMovie(data);
    } catch (err) {
      console.error("❌ Error fetching movie:", err);
    } finally {
      setLoading(false);
    }
  }

  // Send feedback (like/dislike)
  async function sendFeedback(reward) {
    if (!movie) return;
    try {
      await fetch("http://127.0.0.1:8000/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ movie_id: movie.id, reward }),
      });
      fetchNext(); // immediately load next movie
    } catch (err) {
      console.error("❌ Error sending feedback:", err);
    }
  }

  // Load the first movie when app starts
  useEffect(() => {
    fetchNext();
  }, []);

  // Render states
  if (loading) return <h2 style={{ textAlign: "center" }}>Loading...</h2>;
  if (!movie) return <h2 style={{ textAlign: "center" }}>No movies found.</h2>;

  return (
    <div style={{ maxWidth: "600px", margin: "auto", textAlign: "center" }}>
      <h1>{movie.title}</h1>
      <p>{movie.description?.slice(0, 300)}...</p>

      <div>
        <button
          style={{ margin: "10px", padding: "10px 20px" }}
          onClick={() => sendFeedback(1)}
        >
          👍 Like
        </button>

        <button
          style={{ margin: "10px", padding: "10px 20px" }}
          onClick={() => sendFeedback(0)}
        >
          👎 Dislike
        </button>
      </div>
    </div>
  );
}

export default App;
