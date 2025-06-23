import React, { useEffect, useState } from "react";

const API_KEY = "9d1945ec91bdb64dcfc8b5b52cc57e5a";
const IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w300";

export default function MovieList() {
  const [movies, setMovies] = useState([]);
  const [page, setPage] = useState(1);

  const fetchPopularMovies = async (pageNumber) => {
    const res = await fetch(
      `https://api.themoviedb.org/3/movie/popular?api_key=${API_KEY}&language=en-US&page=${pageNumber}`
    );
    const data = await res.json();

    const movieList = data.results.map((movie) => ({
      id: movie.id,
      title: movie.title,
      overview: movie.overview,
      genre_ids: movie.genre_ids,
      poster_path: movie.poster_path,
    }));

    setMovies((prev) => [...prev, ...movieList]);
  };

  useEffect(() => {
    fetchPopularMovies(page);
  }, [page]);

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h2 className="text-3xl font-bold mb-6">Popular Movies</h2>

      <div className="space-y-8">
        {movies.map((movie) => (
          <div
            key={movie.id}
            className="p-4 bg-white shadow rounded-xl flex flex-col items-center relative"
          >
            <h3 className="text-xl font-semibold text-center mb-2">{movie.title}</h3>

            {movie.poster_path && (
              <img
                src={`${IMAGE_BASE_URL}${movie.poster_path}`}
                alt={movie.title}
                className="rounded-md mb-4 w-[200px]"
              />
            )}

            <p className="text-sm text-gray-700 text-center mb-4 px-4">
              {movie.overview}
            </p>

            <div className="flex justify-between w-full px-8 mt-auto">
              <button className="text-red-600 hover:text-red-800 font-bold text-lg">
                👎 Dislike
              </button>
              <button className="text-green-600 hover:text-green-800 font-bold text-lg">
                👍 Like
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="text-center mt-8">
        <button
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          onClick={() => setPage((prev) => prev + 1)}
        >
          Load More
        </button>
      </div>
    </div>
  );
}
