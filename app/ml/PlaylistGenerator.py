import os
from typing import Any, Optional

import joblib
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

TrackDict = dict[str, Any]


class PlaylistGenerator:
    vectorizer: Optional[TfidfVectorizer]
    feature_matrix: Optional[csr_matrix | np.ndarray]
    tracks_df: Optional[pd.DataFrame]
    model_path: str

    def __init__(self, model_path: Optional[str] = None) -> None:
        self.vectorizer = None
        self.feature_matrix = None
        self.tracks_df = None
        self.model_path = model_path or os.path.join(
            os.path.dirname(__file__), "models", "playlist_model.joblib"
        )

    def train(self, track_data: list[dict[str, str]]) -> bool:
        """
        Train the recommendation model on the provided tracks data

        Args:
            tracks_data: List of dictionaries with track information (title, artist, genre)
        """
        self.tracks_df = pd.DataFrame(track_data)

        # Create a text feature by combining title, artist, and genre
        # Ensure 'genre' column exists, even if it's created by fillna
        if "genre" not in self.tracks_df.columns:
            self.tracks_df["genre"] = ""  # Add genre column if missing
        self.tracks_df["features"] = (
            self.tracks_df["title"]
            + " "
            + self.tracks_df["artist"]
            + " "
            + self.tracks_df["genre"].fillna("")
        )

        # Create TF-IDF features
        self.vectorizer = TfidfVectorizer(max_features=5000, stop_words="english")
        self.feature_matrix = self.vectorizer.fit_transform(self.tracks_df["features"])  # type: ignore

        # Save the model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        model_data: dict[str, Any] = {
            "vectorizer": self.vectorizer,
            "feature_matrix": self.feature_matrix,
            "tracks_df": self.tracks_df,
        }
        joblib.dump(model_data, self.model_path)

        return True

    def load_model(self) -> bool:
        """Load the trained model from disk"""
        if not os.path.exists(self.model_path):
            return False

        model_data: dict[str, Any] = joblib.load(self.model_path)
        self.vectorizer = model_data["vectorizer"]
        self.feature_matrix = model_data["feature_matrix"]
        self.tracks_df = model_data["tracks_df"]
        return True

    def generate_playlist(
        self, preferences: dict[str, list[str]], num_tracks: int = 10
    ) -> list[TrackDict]:
        """
        Generate a playlist based on user preferences

        Args:
            preferences: Dict with 'artists' and 'genres' as lists
            num_tracks: Number of tracks to include in the playlist

        Returns:
            List of track dictionaries
        """
        # If model loading fails, and especially if tracks_df is None,
        # we cannot proceed to generate even random tracks from it.
        if not self.load_model():
            return []

        # This case should ideally be caught by load_model returning False, but as a safeguard:
        if (
            self.tracks_df is None
            or self.vectorizer is None
            or self.feature_matrix is None
        ):
            return []

        # Create a query vector from preferences
        artists: list[str] = preferences.get("artists", [])
        genres: list[str] = preferences.get("genres", [])

        query_text: str = " ".join(artists + genres)
        if not query_text.strip():
            # If no preferences, return random tracks
            if self.tracks_df.empty:
                return []
            return self.tracks_df.sample(min(num_tracks, len(self.tracks_df))).to_dict(
                "records"
            )

        # Transform the query to the same feature space as tracks
        query_vector: csr_matrix | np.ndarray = self.vectorizer.transform([query_text])  # type: ignore

        # Calculate similarity scores:
        #   cosine_similarity expects 2D arrays
        #   query_vector is [1, n_features]
        #   self.feature_matrix is [n_samples, n_features]
        similarity_scores: np.ndarray = cosine_similarity(
            query_vector, self.feature_matrix
        ).flatten()

        # Get top N track indices
        # Ensure num_tracks does not exceed available tracks after filtering or if similarity_scores is small
        actual_num_tracks = min(num_tracks, len(similarity_scores))
        if actual_num_tracks == 0:
            return []

        # Argsort returns indices that would sort the array.
        # We take the last 'actual_num_tracks' for the highest scores, then reverse them for descending order.
        top_indices: np.ndarray = np.argsort(similarity_scores)[-actual_num_tracks:][
            ::-1
        ]

        recommended_tracks: list[TrackDict] = self.tracks_df.iloc[top_indices].to_dict(
            "records"
        )

        return recommended_tracks


# Singleton instance for app-wide use
generator = PlaylistGenerator()
