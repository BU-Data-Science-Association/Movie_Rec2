// API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

// Types for API responses
export interface ApiCard {
  id: number;
  title: string;
  description: string;
  poster_path?: string;
}

export interface FeedbackData {
  movie_id: number;
  reward: number; // 1 for like, -1 for dislike
}

// API service class
class MovieApiService {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  // Generic fetch wrapper with error handling
  private async fetchApi<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        headers: {
          "Content-Type": "application/json",
          ...options?.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error("API call failed:", error);
      throw error;
    }
  }

  // Get next movie recommendation
  async getNextMovie(): Promise<ApiCard> {
    return this.fetchApi<ApiCard>("/next");
  }

  // Send feedback (like/dislike)
  async sendFeedback(
    data: FeedbackData
  ): Promise<{ status: string; movie_id: number; reward: number }> {
    return this.fetchApi<{ status: string; movie_id: number; reward: number }>(
      "/feedback",
      {
        method: "POST",
        body: JSON.stringify(data),
      }
    );
  }
}

// Export a singleton instance
export const movieApi = new MovieApiService(API_BASE_URL);
