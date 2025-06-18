import React, { useEffect, useState } from "react";

const API_KEY = "9d1945ec91bdb64dcfc8b5b52cc57e5a";

export default function MovieTable() {
  const [movies, setMovies] = useState([]);
  const [page, setPage] = useState(1);

  const fetchPopularMovies = async (pageNumber) => {
    const res = await fetch(
      `https://api.themoviedb.org/3/movie/popular?api_key=${API_KEY}&language=en-US&page=${pageNumber}`
    );
    const data = await res.json();

    // For each movie, we only need title, overview, and genre_ids
    const movieList = data.results.map((movie) => ({
      id: movie.id,
      title: movie.title,
      overview: movie.overview,
      genre_ids: movie.genre_ids,
    }));

    setMovies((prev) => [...prev, ...movieList]);
  };

  useEffect(() => {
    fetchPopularMovies(page);
  }, [page]);

  // Genre mapping based on TMDb genre IDs (can be expanded)
  const genreMap = {
    28: "Action",
  12: "Adventure",
  16: "Animation",
  35: "Comedy",
  80: "Crime",
  99: "Documentary",
  18: "Drama",
  10751: "Family",
  14: "Fantasy",
  36: "History",
  27: "Horror",
  10402: "Music",
  9648: "Mystery",
  10749: "Romance",
  878: "Science Fiction",
  10770: "TV Movie",
  53: "Thriller",
  10752: "War",
  37: "Western"
    // Add more as needed
  };

  const getGenres = (ids) =>
    ids.map((id) => genreMap[id] || "Unknown").join(", ");

  return (
    <div className="p-4 max-w-5xl mx-auto">
      <h2 className="text-2xl font-bold mb-4">Popular Movies</h2>
      <table className="w-full border border-gray-300">
        <thead>
          <tr className="bg-gray-100">
            <th className="border px-4 py-2 text-left">Title</th>
            <th className="border px-4 py-2 text-left">Genres</th>
            <th className="border px-4 py-2 text-left">Description</th>
          </tr>
        </thead>
        <tbody>
          {movies.map((movie) => (
            <tr key={movie.id} className="border-t border-gray-300">
              <td className="border px-4 py-2 font-medium">{movie.title}</td>
              <td className="border px-4 py-2">{getGenres(movie.genre_ids)}</td>
              <td className="border px-4 py-2 text-sm text-gray-700">
                {movie.overview}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <button
        className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        onClick={() => setPage((prev) => prev + 1)}
      >
        Load More
      </button>
    </div>
  );
}
