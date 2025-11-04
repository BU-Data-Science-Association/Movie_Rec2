import React from "react";
import { Analytics, WeightChange } from "../api/movieApi";
import "./AnalyticsPanel.css";

interface AnalyticsPanelProps {
  analytics: Analytics | null;
  recentChanges: WeightChange[] | null;
  isLoading: boolean;
}

const AnalyticsPanel: React.FC<AnalyticsPanelProps> = ({
  analytics,
  recentChanges,
  isLoading,
}) => {
  if (isLoading) {
    return (
      <div className="analytics-panel">
        <h2>Algorithm Learning</h2>
        <p>Loading analytics...</p>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="analytics-panel">
        <h2>Algorithm Learning</h2>
        <p>Start rating movies to see how the algorithm learns!</p>
      </div>
    );
  }

  return (
    <div className="analytics-panel">
      <h2>Algorithm Learning</h2>

      {/* Stats Section */}
      <div className="stats-section">
        <div className="stat-item">
          <span className="stat-label">Movies Rated:</span>
          <span className="stat-value">{analytics.stats.movies_rated}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Avg Reward:</span>
          <span className="stat-value">
            {analytics.stats.average_reward.toFixed(2)}
          </span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Confidence:</span>
          <span className="stat-value">
            {(analytics.confidence * 100).toFixed(1)}%
          </span>
        </div>
      </div>

      {/* Top Feature Weights */}
      <div className="weights-section">
        <h3>Top Feature Weights</h3>
        <p className="help-text">
          Positive weights = features you like, Negative = features you dislike
        </p>
        <div className="weights-list">
          {analytics.top_weights.map((weight, index) => (
            <div key={weight.feature_index} className="weight-item">
              <span className="weight-rank">#{index + 1}</span>
              <span className="weight-feature" title={weight.feature_name}>
                {weight.feature_name}
              </span>
              <div className="weight-bar-container">
                <div
                  className={`weight-bar ${
                    weight.weight >= 0 ? "positive" : "negative"
                  }`}
                  style={{
                    width: `${Math.min(Math.abs(weight.weight) * 100, 100)}%`,
                  }}
                />
              </div>
              <span
                className={`weight-value ${
                  weight.weight >= 0 ? "positive" : "negative"
                }`}
              >
                {weight.weight.toFixed(3)}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Changes */}
      {recentChanges && recentChanges.length > 0 && (
        <div className="changes-section">
          <h3>Last Update Changed:</h3>
          <div className="changes-list">
            {recentChanges.map((change) => (
              <div key={change.feature_index} className="change-item">
                <span className="change-feature" title={change.feature_name}>
                  {change.feature_name}
                </span>
                <div className="change-values">
                  <span className="change-before">
                    {change.before.toFixed(3)}
                  </span>
                  <span className="change-arrow">→</span>
                  <span className="change-after">
                    {change.after.toFixed(3)}
                  </span>
                  <span
                    className={`change-delta ${
                      change.change >= 0 ? "positive" : "negative"
                    }`}
                  >
                    ({change.change >= 0 ? "+" : ""}
                    {change.change.toFixed(3)})
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalyticsPanel;
