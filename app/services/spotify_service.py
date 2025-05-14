import random

import spotipy
from flask import current_app
from spotipy.oauth2 import SpotifyClientCredentials


class SpotifyService:
    def __init__(self, client_id=None, client_secret=None):
        """Initialize Spotify service with credentials."""
        self.client_id = client_id or current_app.config.get("SPOTIFY_CLIENT_ID")
        self.client_secret = client_secret or current_app.config.get(
            "SPOTIFY_CLIENT_SECRET"
        )

        # For application-only authentication (no user context)
        self.client_credentials_manager = SpotifyClientCredentials(
            client_id=self.client_id, client_secret=self.client_secret
        )

        # Client for app-only operations
        self.sp_client = spotipy.Spotify(
            client_credentials_manager=self.client_credentials_manager
        )

    def search_tracks(self, query, limit=50):
        """Search for tracks on Spotify."""
        try:
            results = self.sp_client.search(q=query, type="track", limit=limit)
            if results and "tracks" in results:
                return results["tracks"]["items"]
            return []
        except Exception as e:
            current_app.logger.error(f"Error searching tracks: {str(e)}")
            return []

    def search_playlists(self, query, limit=20):
        """Search for playlists on Spotify."""
        try:
            results = self.sp_client.search(q=query, type="playlist", limit=limit)
            if results and "playlists" in results:
                return results["playlists"]["items"]
            return []
        except Exception as e:
            current_app.logger.error(f"Error searching playlists: {str(e)}")
            return []

    def get_genre_list(self):
        """Get a list of common music genres."""
        try:
            # Get Spotify's recommendation genres
            available_genres = self.sp_client.recommendation_genre_seeds()
            genres = available_genres.get("genres", []) if available_genres else []

            additional_genres = [
                "rock",
                "pop",
                "hip hop",
                "rap",
                "r&b",
                "country",
                "jazz",
                "classical",
                "electronic",
                "dance",
                "reggae",
                "blues",
                "indie",
                "alternative",
                "folk",
                "metal",
                "punk",
            ]

            for genre in additional_genres:
                if genre not in genres:
                    genres.append(genre)

            # Sort alphabetically
            genres.sort()
            return genres

        except Exception as e:
            current_app.logger.error(f"Error getting genre list: {str(e)}")
            # Return a fallback list of common genres
            return [
                "rock",
                "pop",
                "hip hop",
                "rap",
                "r&b",
                "country",
                "jazz",
                "classical",
                "electronic",
                "dance",
                "reggae",
                "blues",
                "indie",
                "alternative",
                "folk",
                "metal",
                "punk",
            ]

    def find_tracks_by_genre(self, genre, limit=30):
        """
        Find tracks for a specific genre by:
        1. Searching for playlists with the genre name
        2. Getting tracks from those playlists
        3. Falling back to direct search if needed
        """
        try:
            # Search for playlists with the genre name
            playlists = self.search_playlists(f"genre:{genre}", limit=10)

            if not playlists:
                # Try a more generic search
                playlists = self.search_playlists(genre, limit=10)

            if not playlists:
                # If still no playlists, direct track search
                return self.search_tracks(f"genre:{genre}", limit=limit)

            # Randomly select playlists to get a diverse set
            selected_playlists = random.sample(playlists, min(3, len(playlists)))

            all_tracks = []
            for playlist in selected_playlists:
                playlist_id = playlist["id"]
                playlist_tracks = self.sp_client.playlist_items(
                    playlist_id,
                    fields="items.track(id,name,artists,album,preview_url,external_urls)",
                    limit=20,
                )

                if playlist_tracks and "items" in playlist_tracks:
                    for item in playlist_tracks["items"]:
                        if item.get("track"):  # Ensure there's a valid track
                            all_tracks.append(item["track"])

                            # Stop if we've reached the limit
                            if len(all_tracks) >= limit:
                                break

                if len(all_tracks) >= limit:
                    break

            # If we didn't get enough tracks, supplement with direct search
            if len(all_tracks) < limit:
                direct_tracks = self.search_tracks(
                    f"genre:{genre}", limit=limit - len(all_tracks)
                )
                all_tracks.extend(direct_tracks)

            return all_tracks

        except Exception as e:
            current_app.logger.error(f"Error finding tracks by genre: {str(e)}")
            # Fallback to direct search
            return self.search_tracks(genre, limit=limit)

    def get_track_features(self, track_ids):
        """Get audio features for multiple tracks."""
        if not track_ids:
            return []

        try:
            # Spotify limits batch requests to 100 tracks
            features = []
            for i in range(0, len(track_ids), 100):
                batch = track_ids[i : i + 100]
                batch_features = self.sp_client.audio_features(batch)
                if batch_features:
                    features.extend(batch_features)
            return features
        except Exception as e:
            current_app.logger.error(f"Error getting track features: {str(e)}")
            return []
