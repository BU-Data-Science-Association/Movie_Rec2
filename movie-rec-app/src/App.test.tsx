import { render, screen } from "@testing-library/react";
import App from "./App";

test("renders Movie Recommender title", () => {
  render(<App />);
  const titleElement = screen.getByText(/Movie Recommender/i);
  expect(titleElement).toBeInTheDocument();
});
