import os
from typing import Any, Optional

import joblib
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import OneHotEncoder, StandardScaler

TrackDict = dict[str, Any]


class PlaylistGenerator:
    vectorizer: Optional[TfidfVectorizer]
    feature_matrix: Optional[csr_matrix | np.ndarray]
    tracks_df: Optional[pd.DataFrame]
    model_path: str
    genre_encoder: Optional[OneHotEncoder]

    def __init__(self, model_path: Optional[str] = None) -> None:
        self.vectorizer = None
        self.feature_matrix = None
        self.tracks_df = None
        self.scaler = StandardScaler()
        self.genre_encoder = None
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
                "genre",
            ]

            existing_columns = [col for col in columns_to_keep if col in df.columns]
            processed_dfs.append(df[existing_columns])

        # Combine all processed dataframes
        if processed_dfs:
            self.tracks_df = pd.concat(processed_dfs, ignore_index=True)

            if self.tracks_df is not None:
                # Fill missing genres with "Unknown"
                if "genre" in self.tracks_df.columns:
                    self.tracks_df["genre"] = self.tracks_df["genre"].fillna("Unknown")
                else:
                    self.tracks_df["genre"] = "Unknown"

                print(
                    f"Loaded {len(self.tracks_df)} tracks with {self.tracks_df['artist'].nunique()} unique artists"
                )

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

        feature_data = self.tracks_df[available_features].values
        audio_features = self.scaler.fit_transform(feature_data)

        # Process genre features if available
        genre_features = None
        if "genre" in self.tracks_df.columns:
            print("Processing genre features")
            # Convert genres to one-hot encoding
            self.genre_encoder = OneHotEncoder(
                sparse_output=True, handle_unknown="ignore"
            )
            genre_features = self.genre_encoder.fit_transform(self.tracks_df[["genre"]])
            print(f"Created genre features with shape {genre_features.shape}")

        text_features = self._create_text_features()

        # Combine all available features
        all_features = []
        if audio_features is not None:
            all_features.append(audio_features)
            print(f"Added audio features with shape {audio_features.shape}")

        if genre_features is not None:
            all_features.append(genre_features)
            print(f"Added genre features with shape {genre_features.shape}")

        if text_features is not None:
            all_features.append(text_features)
            print(f"Added text features with shape {text_features.shape}")  # type: ignore

        # Set the feature matrix - sparse or dense depending on what we have
        if len(all_features) > 0:
            if isinstance(all_features[0], np.ndarray):
                # Convert sparse matrices to dense if first is dense
                for i in range(1, len(all_features)):
                    if hasattr(all_features[i], "toarray"):
                        all_features[i] = all_features[i].toarray()

                # Combine dense arrays
                self.feature_matrix = (
                    np.hstack(all_features)
                    if len(all_features) > 1
                    else all_features[0]
                )
            else:
                # Convert dense arrays to sparse if first is sparse
                from scipy.sparse import csr_matrix

                for i in range(1, len(all_features)):
                    if not hasattr(all_features[i], "toarray"):
                        all_features[i] = csr_matrix(all_features[i])

                # Combine sparse matrices
                self.feature_matrix = (
                    hstack(all_features) if len(all_features) > 1 else all_features[0]
                )  # type: ignore

            print(f"Final feature matrix shape: {self.feature_matrix.shape}")  # type: ignore
            return True

        return False

    def _create_text_features(self):
        """Helper method to create text features from artist and title"""
        if self.tracks_df is None or self.tracks_df.empty:
            return None

        # Create a text feature by combining title, artist, and genre
        self.tracks_df["features_text"] = (
            self.tracks_df["title"].fillna("")
            + " "
            + self.tracks_df["artist"].fillna("")
            + " "
            + self.tracks_df.get("genre", "").fillna("")  # type: ignore
        )

        # Create TF-IDF features
        self.vectorizer = TfidfVectorizer(max_features=5000, stop_words="english")
        return self.vectorizer.fit_transform(self.tracks_df["features_text"])

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

        if self.tracks_df is None or self.tracks_df.empty:
            print("No data available for training")
            return False

        success = self.preprocess_features()
        if not success:
            print("Failed to process features")
            return False

        if save_model:
            self.save_model()

        return True

    def save_model(self) -> None:
        """Save the model to disk"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)

        model_data = {
            "tracks_df": self.tracks_df,
            "feature_matrix": self.feature_matrix,
            "vectorizer": self.vectorizer,
            "scaler": self.scaler,
            "genre_encoder": self.genre_encoder,
        }

        joblib.dump(model_data, self.model_path)
        print(f"Model saved to {self.model_path}")

    def load_model(self) -> bool:
        """Load the trained model from disk"""
        if not os.path.exists(self.model_path):
            print(f"Model file not found at {self.model_path}")
            return False

        try:
            model_data: dict[str, Any] = joblib.load(self.model_path)
            self.vectorizer = model_data.get("vectorizer")
            self.feature_matrix = model_data.get("feature_matrix")
            self.tracks_df = model_data.get("tracks_df")
            self.scaler = model_data.get("scaler", StandardScaler())
            self.genre_encoder = model_data.get("genre_encoder")

            # Verify loaded components
            if self.tracks_df is None:
                print("Error: tracks_df not found in model file")
                return False

            if self.feature_matrix is None:
                print("Error: feature_matrix not found in model file")
                return False

            # Check data quality
            unique_artists = self.tracks_df["artist"].nunique()
            unique_titles = self.tracks_df["title"].nunique()
            print(
                f"Loaded dataset with {len(self.tracks_df)} tracks, {unique_artists} unique artists, {unique_titles} unique titles"
            )

            if "genre" in self.tracks_df.columns:
                genre_counts = self.tracks_df["genre"].value_counts()
                print(f"Dataset has {self.tracks_df['genre'].nunique()} unique genres")
                print(f"Top 5 genres: {genre_counts.head().to_dict()}")

            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False

    def generate_playlist(
        self, preferences: dict[str, list[str]], num_tracks: int = 10
    ) -> list[TrackDict]:
        """
        Generate a playlist based on user preferences with improved diversity,
        ensuring no duplicate tracks in recommendations.

        Args:
            preferences: Dict with 'artists' and 'genres' as lists
            num_tracks: Number of tracks to include in the playlist

        Returns:
            List of track dictionaries
        """
        # If model loading fails, we cannot proceed
        if not self.load_model():
            print("Failed to load model")
            return []

        # Safety check for required components
        if self.tracks_df is None or self.feature_matrix is None:
            print("Missing required components (tracks_df or feature_matrix)")
            return []

        artists: list[str] = preferences.get("artists", [])
        genres: list[str] = preferences.get("genres", [])
        query_text: str = " ".join(artists + genres)

        # If no preferences, return diversified random tracks
        if not query_text.strip():
            print("No preferences provided, returning diverse random tracks")
            if self.tracks_df.empty:
                return []

            # Group by artist and title to eliminate exact duplicates
            grouped = self.tracks_df.drop_duplicates(subset=["artist", "title"])

            # Group by artist to improve diversity
            artist_groups = grouped.groupby("artist")
            diverse_tracks = []

            # Take up to 2 songs per artist
            for _, group in artist_groups:
                sample_size = min(2, len(group))
                diverse_tracks.append(group.sample(sample_size))

            if diverse_tracks:
                combined = pd.concat(diverse_tracks)
                random_tracks = combined.sample(min(num_tracks, len(combined))).to_dict(
                    "records"
                )

                return random_tracks
            return []

        similarity_scores = None

        # Use vectorizer if available
        if self.vectorizer is not None:
            query_vector = self.vectorizer.transform([query_text])
            feature_dim = self.feature_matrix.shape[1]  # type: ignore
            vector_dim = query_vector.shape[1]  # type: ignore

            if feature_dim > vector_dim:
                from scipy.sparse import csr_matrix, hstack

                padding_size = feature_dim - vector_dim
                padding = csr_matrix((1, padding_size))
                query_vector = hstack([query_vector, padding])
                print(f"Padded query vector to shape: {query_vector.shape}")

            print(f"Query vector shape: {query_vector.shape}")  # type: ignore
            print(f"Feature matrix shape: {self.feature_matrix.shape}")  # type: ignore

            # Calculate similarity scores
            similarity_scores = cosine_similarity(
                query_vector, self.feature_matrix
            ).flatten()
        else:
            # Fallback to alternative approach if vectorizer not available
            print("Vectorizer not available, using alternative similarity method")
            # Filter by exact match on artists or genres
            mask = np.zeros(len(self.tracks_df), dtype=bool)

            for artist in artists:
                artist_lower = artist.lower()
                mask |= (
                    self.tracks_df["artist"]
                    .str.lower()
                    .str.contains(artist_lower, na=False)
                )

            for genre in genres:
                genre_lower = genre.lower()
                if "genre" in self.tracks_df.columns:
                    mask |= (
                        self.tracks_df["genre"]
                        .str.lower()
                        .str.contains(genre_lower, na=False)
                    )

            # Create similarity scores from mask (1.0 for matches, random low scores for others)
            similarity_scores = np.zeros(len(self.tracks_df))
            similarity_scores[mask] = 1.0
            # Add small random values for diversity even among matches
            similarity_scores += np.random.random(len(similarity_scores)) * 0.1

        feature_preferences = preferences.get("features", {})
        if feature_preferences and self.tracks_df is not None:
            feature_score = np.ones(len(self.tracks_df))

            for feature, target_value in feature_preferences.items():  # type: ignore
                if feature in self.tracks_df.columns:
                    # Calculate how close each track's feature is to the target value
                    feature_values = self.tracks_df[feature].fillna(0).values
                    # Convert to normalized distance (0 = far, 1 = close)
                    feature_distance = (
                        1.0 - np.abs(feature_values - float(target_value)) / 1.0  # type: ignore
                    )
                    # Clip values to 0-1 range
                    feature_distance = np.clip(feature_distance, 0, 1)
                    feature_score *= feature_distance

            # Combine with previous similarity scores (30% weight to audio features)
            similarity_scores = (similarity_scores * 0.7) + (feature_score * 0.3)

        # Get appropriate number of tracks
        actual_num_tracks = min(num_tracks, len(similarity_scores))
        if actual_num_tracks == 0:
            print("No tracks available after filtering")
            return []

        # Get a larger pool of candidates for diversity - 3x what we need
        candidate_pool_size = min(num_tracks * 5, len(similarity_scores))
        candidate_indices = np.argsort(similarity_scores)[-candidate_pool_size:][::-1]

        unique_tracks = set()
        artist_count = {}
        selected_indices = []

        # Process candidates in order of similarity
        for idx in candidate_indices:
            artist = str(self.tracks_df.iloc[idx]["artist"]).strip()
            title = str(self.tracks_df.iloc[idx]["title"]).strip()
            track_key = f"{artist.lower()}|{title.lower()}"

            # Skip if we've already selected this track
            if track_key in unique_tracks:
                continue

            # Check artist limit (max 3 songs per artist)
            if artist.lower() in artist_count and artist_count[artist.lower()] >= 3:
                continue

            # This track passes all filters, add it
            unique_tracks.add(track_key)
            artist_count[artist.lower()] = artist_count.get(artist.lower(), 0) + 1
            selected_indices.append(idx)

            if len(selected_indices) >= actual_num_tracks:
                break

        # If we still need more tracks, relax the artist limit
        if len(selected_indices) < actual_num_tracks:
            print(
                f"Relaxing artist limits to get more tracks (have {len(selected_indices)}, need {actual_num_tracks})"
            )
            for idx in candidate_indices:
                # Skip indices we've already selected
                if idx in selected_indices:
                    continue

                # Get artist and title
                artist = str(self.tracks_df.iloc[idx]["artist"]).strip()
                title = str(self.tracks_df.iloc[idx]["title"]).strip()
                track_key = f"{artist.lower()}|{title.lower()}"

                # Skip if we've already selected this track
                if track_key in unique_tracks:
                    continue

                unique_tracks.add(track_key)
                selected_indices.append(idx)

                if len(selected_indices) >= actual_num_tracks:
                    break

        final_indices = list(dict.fromkeys(selected_indices))
        recommended_tracks = self.tracks_df.iloc[final_indices].to_dict("records")
        track_keys = set()
        unique_recommended_tracks = []

        for track in recommended_tracks:
            artist = str(track.get("artist", "")).strip()
            title = str(track.get("title", "")).strip()
            key = f"{artist.lower()}|{title.lower()}"

            if key not in track_keys:
                track_keys.add(key)
                unique_recommended_tracks.append(track)

        if len(unique_recommended_tracks) != len(recommended_tracks):
            print(
                f"WARNING: Removed {len(recommended_tracks) - len(unique_recommended_tracks)} duplicate tracks"
            )

        return unique_recommended_tracks
