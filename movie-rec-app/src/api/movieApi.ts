// API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

// Types for API responses
export interface ApiCard {
  id: number;
  image: string;
  title: string;
  description: string;
}

export interface SwipeData {
  cardId: number;
  direction: "left" | "right";
  timestamp: string;
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

  // Example: Get hello message
  async getHello(): Promise<{ message: string }> {
    return this.fetchApi<{ message: string }>("/hello");
  }

  // Example: Fetch cards/movies from the server
  async getCards(): Promise<ApiCard[]> {
    return this.fetchApi<ApiCard[]>("/cards");
  }

  // Example: Get a single card
  async getCard(id: number): Promise<ApiCard> {
    return this.fetchApi<ApiCard>(`/cards/${id}`);
  }

  // Example: Send swipe action to server
  async recordSwipe(data: SwipeData): Promise<{ success: boolean }> {
    return this.fetchApi<{ success: boolean }>("/swipe", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // Example: Get recommendations
  async getRecommendations(userId?: string): Promise<ApiCard[]> {
    const endpoint = userId
      ? `/recommendations?user_id=${userId}`
      : "/recommendations";
    return this.fetchApi<ApiCard[]>(endpoint);
  }

  // Example: Reset user preferences
  async resetPreferences(userId: string): Promise<{ success: boolean }> {
    return this.fetchApi<{ success: boolean }>(`/reset/${userId}`, {
      method: "POST",
    });
  }
}

// Export a singleton instance
export const movieApi = new MovieApiService(API_BASE_URL);
