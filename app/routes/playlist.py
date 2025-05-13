import os
import uuid

import pandas as pd
from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user, login_required

from app.ml.playlist_generator import PlaylistGenerator
from app.models import Playlist, PlaylistTrack, Track, db

playlist_bp = Blueprint("playlist", __name__)

model_path = os.path.join(
    os.path.dirname(__file__), "../ml/pretrained/playlist_model.joblib"
)
generator = PlaylistGenerator(model_path=model_path)


def init_app(app):
    with app.app_context():
        try:
            if not generator.load_model():
                app.logger.warning(
                    "Failed to load recommendation model. Some features may be unavailable."
                )
            else:
                app.logger.info("Recommendation model loaded successfully.")
        except Exception as e:
            app.logger.error(f"Error loading recommendation model: {str(e)}")


@playlist_bp.route("/features", methods=["GET"])
def get_audio_features():
    """Get available audio features and their ranges."""
    try:
        if generator.tracks_df is None:
            if not generator.load_model():
                return jsonify({"error": "Recommendation model not available"}), 500

        feature_list = [
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

        # Calculate stats for features that exist in our dataset
        features = {}
        for feature in feature_list:
            if feature in generator.tracks_df.columns:
                features[feature] = {
                    "min": float(generator.tracks_df[feature].min()),
                    "max": float(generator.tracks_df[feature].max()),
                    "mean": float(generator.tracks_df[feature].mean()),
                    "description": get_feature_description(feature),
                }

        return jsonify({"features": features})
    except Exception as e:
        current_app.logger.error(f"Error fetching audio features: {str(e)}")
        return jsonify({"error": "Failed to fetch audio features"}), 500


@playlist_bp.route("/generate", methods=["POST"])
def generate_playlist():
    """Generate a playlist based on preferences with improved debugging."""
    try:
        if generator.tracks_df is None:
            if not generator.load_model():
                return jsonify({"error": "Recommendation model not available"}), 500

        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Log the incoming request data for debugging
        current_app.logger.info("Playlist generation request:")
        current_app.logger.info(f"- Name: {data.get('name', 'Not provided')}")
        current_app.logger.info(f"- Genres: {data.get('genres', [])}")
        current_app.logger.info(f"- Artists: {data.get('artists', [])}")
        current_app.logger.info(f"- Track count: {data.get('trackCount', 20)}")
        current_app.logger.info(f"- Features: {data.get('features', {})}")

        playlist_name = data.get("name", "My QueMe Playlist")
        genres = data.get("genres", [])
        artists = data.get("artists", [])
        track_count = data.get("trackCount", 20)
        feature_preferences = data.get("features", {})

        # Validate inputs
        if not genres and not artists and not feature_preferences:
            return jsonify(
                {
                    "error": "At least one genre, artist, or audio feature preference is required"
                }
            ), 400

        preferences = {"genres": genres, "artists": artists}

        # Log model state
        if generator.tracks_df is not None:
            current_app.logger.info(f"Model has {len(generator.tracks_df)} tracks")
            if "genre" in generator.tracks_df.columns:
                genres_in_model = (
                    generator.tracks_df["genre"].dropna().unique()[:10]
                )  # Show first 10
                current_app.logger.info(f"Sample genres in model: {genres_in_model}")

        # Generate recommendations
        current_app.logger.info("Calling generate_playlist method...")
        recommended_tracks = generator.generate_playlist(
            preferences=preferences, num_tracks=track_count
        )
        current_app.logger.info(
            f"Received {len(recommended_tracks)} recommended tracks"
        )

        formatted_tracks = []
        for track in recommended_tracks:
            # Get artist and title, handling potential missing values
            artist_name = track.get("artist", None)
            if pd.isna(artist_name):
                artist_name = "Unknown Artist"

            title_name = track.get("title", None)
            if pd.isna(title_name):
                title_name = "Unknown Track"

            # Create a formatted track object
            formatted_track = {
                "id": track.get(
                    "id", str(uuid.uuid4())
                ),  # Generate an ID if none exists
                "title": title_name,
                "artist": artist_name,
                "album": track.get("album", "Unknown Album")
                if not pd.isna(track.get("album", None))
                else "Unknown Album",
            }

            for feature in [
                "danceability",
                "energy",
                "loudness",
                "speechiness",
                "acousticness",
                "instrumentalness",
                "liveness",
                "valence",
                "tempo",
            ]:
                if feature in track and not pd.isna(track[feature]):
                    formatted_track[feature] = float(track[feature])

            formatted_tracks.append(formatted_track)

        if formatted_tracks:
            sample_tracks = formatted_tracks[:3]
            current_app.logger.info("Sample of returned tracks:")
            for i, track in enumerate(sample_tracks):
                current_app.logger.info(
                    f"{i + 1}. {track['artist']} - {track['title']}"
                )

        playlist = {
            "playlist_name": playlist_name,
            "genres": genres,
            "artists": artists,
            "features": feature_preferences,
            "tracks": formatted_tracks,
        }

        return jsonify(playlist)
    except Exception as e:
        current_app.logger.error(f"Error generating playlist: {str(e)}")
        import traceback

        current_app.logger.error(traceback.format_exc())
        return jsonify({"error": f"Failed to generate playlist: {str(e)}"}), 500


@playlist_bp.route("/save", methods=["POST"])
@login_required
def save_playlist():
    """Save a generated playlist to the database."""
    try:
        data = request.json

        if not data:
            return jsonify({"error": "No data provided"}), 400

        playlist_name = data.get("playlist_name")
        tracks = data.get("tracks", [])

        if not playlist_name or not tracks:
            return jsonify({"error": "Playlist name and tracks are required"}), 400

        # Create new playlist
        new_playlist = Playlist(
            id=uuid.uuid4(), name=playlist_name, user_id=current_user.id
        )

        db.session.add(new_playlist)
        db.session.flush()  # Flush to get the playlist ID

        # Add tracks to the database
        for index, track_data in enumerate(tracks):
            # Check if track already exists
            existing_track = Track.query.filter_by(
                title=track_data["title"], artist=track_data["artist"]
            ).first()

            if existing_track:
                track = existing_track
            else:
                # Create new track
                track = Track(
                    id=uuid.uuid4(),
                    title=track_data["title"],
                    artist=track_data["artist"],
                    genre=track_data.get("genre", ""),
                )
                db.session.add(track)
                db.session.flush()  # Flush to get the track ID

            playlist_track = PlaylistTrack(
                id=uuid.uuid4(),
                playlist_id=new_playlist.id,
                track_id=track.id,
                position=index,
            )
            db.session.add(playlist_track)

        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": "Playlist saved successfully",
                "playlist_id": str(new_playlist.id),
            }
        )

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error saving playlist: {str(e)}")
        return jsonify({"error": f"Failed to save playlist: {str(e)}"}), 500


def get_feature_description(feature):
    """Get a user-friendly description for an audio feature."""
    descriptions = {
        "danceability": "How suitable a track is for dancing based on tempo, rhythm stability, beat strength, and overall regularity",
        "energy": "A perceptual measure of intensity and activity. Energetic tracks feel fast, loud, and noisy",
        "loudness": "The overall loudness of a track in decibels (dB), averaged across the entire track",
        "speechiness": "Presence of spoken words in a track. Values above 0.66 describe tracks that are probably made entirely of spoken words",
        "acousticness": "A confidence measure of whether the track is acoustic",
        "instrumentalness": "Predicts whether a track contains no vocals. Values above 0.5 represent instrumental tracks",
        "liveness": "Detects the presence of an audience in the recording. Higher values represent an increased probability of the track being performed live",
        "valence": "A measure of the musical positiveness conveyed by a track. High valence sounds more positive (happy, cheerful, euphoric)",
        "tempo": "The overall estimated tempo of a track in beats per minute (BPM)",
    }
    return descriptions.get(feature, "No description available")
