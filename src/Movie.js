import React, { useEffect, useState } from "react";
import Papa from "papaparse";

const IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w300";

export default function MovieList() {
  const [movies, setMovies] = useState([]);
  const [current, setCurrent] = useState(0);

  // Load movies from CSV once on mount
  useEffect(() => {
    fetch("/movies.csv")
      .then((res) => res.text())
      .then((csvText) => {
        // Parse CSV text to JSON array of movie objects
        const parsed = Papa.parse(csvText, {
          header: true,
          skipEmptyLines: true,
        });
        setMovies(parsed.data);
      });
  }, []);

  const handleNext = () => {
    if (current < movies.length - 1) {
      setCurrent((prev) => prev + 1);
    }
  };

  const currentMovie = movies[current];

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      {currentMovie ? (
        <div className="bg-white p-6 rounded-xl shadow-lg max-w-md text-center">
          <h2 className="text-2xl font-bold mb-4">{currentMovie.title}</h2>

          {currentMovie.poster_path && (
            <img
              src={`${IMAGE_BASE_URL}${currentMovie.poster_path}`}
              alt={currentMovie.title}
              className="mx-auto mb-4 rounded-md"
            />
          )}

          <p className="text-gray-700 text-sm mb-6">{currentMovie.overview}</p>

          <div className="flex justify-between px-8">
            <button
              onClick={handleNext}
              className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
            >
              👎 Dislike
            </button>
            <button
              onClick={handleNext}
              className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
            >
              👍 Like
            </button>
          </div>
        </div>
      ) : (
        <p className="text-center text-gray-500">Loading...</p>
      )}
    </div>
  );
}
