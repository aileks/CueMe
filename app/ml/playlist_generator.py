import os
from typing import Any, Optional

import joblib
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler

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
        self.scaler = StandardScaler()
        self.model_path = model_path or os.path.join(
            os.path.dirname(__file__), "ml", "playlist_model.joblib"
        )

    def load_data(self, csv_files):
        """
        Load data from multiple CSV files and standardize column names

        Args:
            csv_files: List of paths to CSV files
        """
        processed_dfs = []

        for file_path in csv_files:
            df = pd.read_csv(file_path)

            # NOTE: This is specific to my local training data
            if "artists" in df.columns and "track_name" in df.columns:
                df = df.rename(columns={"artists": "artist", "track_name": "title"})
            elif "Artist" in df.columns and "Track" in df.columns:
                df = df.rename(columns={"Artist": "artist", "Track": "title"})

            columns_to_keep = [
                "artist",
                "title",
                "danceability",
                "energy",
                "key",
                "loudness",
                "speechiness",
                "acousticness",
                "instrumentalness",
                "liveness",
                "valence",
                "tempo",
            ]

            existing_columns = [col for col in columns_to_keep if col in df.columns]
            processed_dfs.append(df[existing_columns])

        # Combine all processed dataframes
        if processed_dfs:
            self.tracks_df = pd.concat(processed_dfs, ignore_index=True)
            return True

        return False

    def preprocess_features(self):
        """
        Preprocess track features for recommendation
        """
        if self.tracks_df is None:
            return False

        numeric_features = [
            "danceability",
            "energy",
            "loudness",
            "speechiness",
            "acousticness",
            "instrumentalness",
            "liveness",
            "valence",
            "tempo",
        ]

        # Keep only features that exist in our dataset
        available_features = [
            f for f in numeric_features if f in self.tracks_df.columns
        ]

        if not available_features:
            print("No audio features found in the dataset")
            return False

        # Fill missing values with the mean
        for feature in available_features:
            if feature in self.tracks_df.columns:
                self.tracks_df[feature] = self.tracks_df[feature].fillna(
                    self.tracks_df[feature].mean()
                )

        # Extract feature matrix
        feature_data = self.tracks_df[available_features].values

        # Normalize features
        self.feature_matrix = self.scaler.fit_transform(feature_data)

        print(f"Preprocessed {len(available_features)} audio features")
        return True

    def train(
        self, track_data: Optional[list[dict[str, str]]] = None, save_model: bool = True
    ) -> bool:
        """
        Train the recommendation model on the provided tracks data or loaded data

        Args:
            track_data: Optional list of dictionaries with track information
            save_model: Whether to save the model after training

        Returns:
            Boolean indicating success
        """
        # If track_data is provided, use it, otherwise use the data already loaded
        if track_data is not None:
            self.tracks_df = pd.DataFrame(track_data)

        # Check if we have data to work with
        if self.tracks_df is None or self.tracks_df.empty:
            print("No data available for training")
            return False

        # First, try to process audio features
        audio_features_available = self.preprocess_features()

        # If audio features are not available, fall back to text-based features
        if not audio_features_available:
            # Create a text feature by combining title, artist, and genre
            if "genre" not in self.tracks_df.columns:
                self.tracks_df["genre"] = ""  # Add genre column if missing
            self.tracks_df["features"] = (
                self.tracks_df["title"].fillna("")
                + " "
                + self.tracks_df["artist"].fillna("")
                + " "
                + self.tracks_df["genre"].fillna("")
            )

            # Create TF-IDF features
            self.vectorizer = TfidfVectorizer(max_features=5000, stop_words="english")
            self.feature_matrix = self.vectorizer.fit_transform(
                self.tracks_df["features"]
            )  # type: ignore

        # Save the model
        if save_model:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            model_data: dict[str, Any] = {
                "vectorizer": self.vectorizer,
                "feature_matrix": self.feature_matrix,
                "tracks_df": self.tracks_df,
                "scaler": self.scaler,
                "uses_audio_features": audio_features_available,
            }
            joblib.dump(model_data, self.model_path)

        return True

    def save_model(self) -> None:
        """Save the model to disk"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)

        model_data = {
            "tracks_df": self.tracks_df,
            "feature_matrix": self.feature_matrix,  # Audio features if available
            "text_feature_matrix": getattr(
                self, "text_feature_matrix", None
            ),  # Text features
            "vectorizer": self.vectorizer,
            "scaler": self.scaler,
        }

        joblib.dump(model_data, self.model_path)
        print(f"Model saved to {self.model_path}")

    def load_model(self) -> bool:
        """Load the trained model from disk"""
        if not os.path.exists(self.model_path):
            return False

        model_data: dict[str, Any] = joblib.load(self.model_path)
        self.vectorizer = model_data.get("vectorizer")
        self.feature_matrix = model_data.get("feature_matrix")
        self.text_feature_matrix = model_data.get("text_feature_matrix")
        self.tracks_df = model_data.get("tracks_df")
        self.scaler = model_data.get("scaler", StandardScaler())

        return True

    def generate_playlist(
        self, preferences: dict[str, list[str]], num_tracks: int = 10
    ) -> list[TrackDict]:
        """
        Generate a playlist based on user preferences with improved debugging

        Args:
            preferences: Dict with 'artists' and 'genres' as lists
            num_tracks: Number of tracks to include in the playlist

        Returns:
            List of track dictionaries
        """
        # If model loading fails, and especially if tracks_df is None,
        # we cannot proceed to generate even random tracks from it.
        if not self.load_model():
            print("Failed to load model")
            return []

        # This case should ideally be caught by load_model returning False, but as a safeguard:
        if (
            self.tracks_df is None
            or self.vectorizer is None
            or self.feature_matrix is None
        ):
            print(
                "Missing required components (tracks_df, vectorizer, or feature_matrix)"
            )
            return []

        # Create a query vector from preferences
        artists: list[str] = preferences.get("artists", [])
        genres: list[str] = preferences.get("genres", [])

        # Debug log the preferences
        print(f"Generating playlist with preferences:")
        print(f"- Artists: {artists}")
        print(f"- Genres: {genres}")

        query_text: str = " ".join(artists + genres)

        # If no preferences, return random tracks
        if not query_text.strip():
            print("No preferences provided, returning random tracks")
            if self.tracks_df.empty:
                return []

            random_tracks = self.tracks_df.sample(
                min(num_tracks, len(self.tracks_df))
            ).to_dict("records")
            print(f"Random selection: {len(random_tracks)} tracks")
            return random_tracks

        # Debug log the query text
        print(f"Query text: '{query_text}'")

        # Transform the query to the same feature space as tracks
        query_vector = self.vectorizer.transform([query_text])

        # Log shape information
        print(f"Query vector shape: {query_vector.shape}")
        print(f"Feature matrix shape: {self.feature_matrix.shape}")

        # Calculate similarity scores
        similarity_scores = cosine_similarity(
            query_vector, self.feature_matrix
        ).flatten()

        # Log similarity score information
        print(
            f"Similarity scores range: {similarity_scores.min():.4f} to {similarity_scores.max():.4f}"
        )
        print(f"Mean similarity: {similarity_scores.mean():.4f}")
        print(f"Number of scores > 0.5: {sum(similarity_scores > 0.5)}")
        print(f"Number of scores > 0.2: {sum(similarity_scores > 0.2)}")

        # Get top N track indices
        actual_num_tracks = min(num_tracks, len(similarity_scores))
        if actual_num_tracks == 0:
            print("No tracks available after filtering")
            return []

        # Get top indices
        top_indices = np.argsort(similarity_scores)[-actual_num_tracks:][::-1]

        # Log top similarity scores
        print(
            f"Top 5 similarity scores: {[f'{similarity_scores[i]:.4f}' for i in top_indices[:5]]}"
        )

        # Get recommended tracks
        recommended_tracks = self.tracks_df.iloc[top_indices].to_dict("records")

        # Debug log some of the recommended tracks
        print(f"Recommended {len(recommended_tracks)} tracks, first 3:")
        for i, track in enumerate(recommended_tracks[:3]):
            print(
                f"{i + 1}. {track.get('artist', 'Unknown')} - {track.get('title', 'Unknown')} (score: {similarity_scores[top_indices[i]]:.4f})"
            )

        return recommended_tracks
