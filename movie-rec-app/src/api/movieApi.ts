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

export interface WeightChange {
  feature_index: number;
  feature_name: string;
  before: number;
  after: number;
  change: number;
}

export interface FeatureWeight {
  feature_index: number;
  feature_name: string;
  weight: number;
}

export interface Analytics {
  top_weights: FeatureWeight[];
  confidence: number;
  stats: {
    total_interactions: number;
    average_reward: number;
    movies_rated: number;
    movies_remaining: number;
  };
}

export interface FeedbackResponse {
  status: string;
  movie_id: number;
  reward: number;
  changes: WeightChange[];
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
  async sendFeedback(data: FeedbackData): Promise<FeedbackResponse> {
    return this.fetchApi<FeedbackResponse>("/feedback", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // Get analytics data
  async getAnalytics(): Promise<Analytics> {
    return this.fetchApi<Analytics>("/analytics");
  }
}

// Export a singleton instance
export const movieApi = new MovieApiService(API_BASE_URL);
