import random
import uuid

import spotipy
from flask import current_app, session
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth


class SpotifyService:
    def __init__(self, client_id=None, client_secret=None, redirect_uri=None):
        """Initialize Spotify service with credentials."""
        self.client_id = client_id or current_app.config.get("SPOTIFY_CLIENT_ID")
        self.client_secret = client_secret or current_app.config.get(
            "SPOTIFY_CLIENT_SECRET"
        )
        self.redirect_uri = redirect_uri or current_app.config.get(
            "SPOTIFY_REDIRECT_URI"
        )

        # For application-only authentication (no user context)
        self.client_credentials_manager = SpotifyClientCredentials(
            client_id=self.client_id, client_secret=self.client_secret
        )

        # Client for app-only operations
        self.sp_client = spotipy.Spotify(
            client_credentials_manager=self.client_credentials_manager
        )

    def get_auth_url(self, state=None):
        """Get authorization URL for user authentication."""
        if not state:
            state = str(uuid.uuid4())

        scope = "user-library-read playlist-read-private playlist-modify-private playlist-modify-public user-top-read"
        auth_manager = SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=scope,
            state=state,
        )

        auth_url = auth_manager.get_authorize_url()
        session["spotify_auth_state"] = state
        return auth_url

    def get_user_token(self, code):
        """Exchange authorization code for access token."""
        auth_manager = SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
        )

        token_info = auth_manager.get_access_token(code)
        session["spotify_token_info"] = token_info
        return token_info

    def get_user_client(self):
        """Get Spotify client with user authentication."""
        token_info = session.get("spotify_token_info")

        if not token_info:
            return None

        # Check if token needs refresh
        auth_manager = SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
        )

        if auth_manager.is_token_expired(token_info):
            token_info = auth_manager.refresh_access_token(token_info["refresh_token"])
            session["spotify_token_info"] = token_info

        return spotipy.Spotify(auth=token_info["access_token"])

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    #                Browse API Methods                      #
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    def get_categories(self, limit=50, country=None):
        """Get a list of Spotify categories, used as a proxy for genres."""
        try:
            results = self.sp_client.categories(limit=limit, country=country)
            return results["categories"]["items"]
        except Exception as e:
            current_app.logger.error(f"Error getting categories: {str(e)}")
            return []

    def get_category_playlists(self, category_id, limit=20):
        """Get playlists for a specific category."""
        try:
            results = self.sp_client.category_playlists(
                category_id=category_id, limit=limit
            )
            return results["playlists"]["items"]
        except Exception as e:
            current_app.logger.error(f"Error getting category playlists: {str(e)}")
            return []

    def get_featured_playlists(self, limit=20, country=None):
        """Get Spotify featured playlists."""
        try:
            results = self.sp_client.featured_playlists(limit=limit, country=country)
            return results["playlists"]["items"]
        except Exception as e:
            current_app.logger.error(f"Error getting featured playlists: {str(e)}")
            return []

    def get_new_releases(self, limit=20, country=None):
        """Get new album releases featured in Spotify."""
        try:
            results = self.sp_client.new_releases(limit=limit, country=country)
            return results["albums"]["items"]
        except Exception as e:
            current_app.logger.error(f"Error getting new releases: {str(e)}")
            return []

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    #                  Search API Methods                    #
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    def search_tracks(self, query, limit=50):
        """Search for tracks on Spotify."""
        try:
            results = self.sp_client.search(q=query, type="track", limit=limit)
            return results["tracks"]["items"]
        except Exception as e:
            current_app.logger.error(f"Error searching tracks: {str(e)}")
            return []

    def search_playlists(self, query, limit=20):
        """Search for playlists on Spotify."""
        try:
            results = self.sp_client.search(q=query, type="playlist", limit=limit)
            return results["playlists"]["items"]
        except Exception as e:
            current_app.logger.error(f"Error searching playlists: {str(e)}")
            return []

    def search_artists(self, query, limit=20):
        """Search for artists on Spotify."""
        try:
            results = self.sp_client.search(q=query, type="artist", limit=limit)
            return results["artists"]["items"]
        except Exception as e:
            current_app.logger.error(f"Error searching artists: {str(e)}")
            return []

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    #               Genre-Related Methods                    #
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    def get_genre_list(self):
        """
        Get a curated list of common music genres.
        This is a static list since the genre_seeds endpoint is deprecated.
        """
        return [
            "pop",
            "rock",
            "hip hop",
            "rap",
            "electronic",
            "dance",
            "r&b",
            "soul",
            "indie",
            "folk",
            "country",
            "jazz",
            "blues",
            "classical",
            "metal",
            "punk",
            "alternative",
            "ambient",
            "reggae",
            "funk",
            "disco",
            "house",
            "techno",
            "trance",
            "edm",
            "trap",
            "latin",
            "salsa",
            "k-pop",
            "j-pop",
            "anime",
            "soundtrack",
            "instrumental",
        ]

    def find_tracks_by_genre(self, genre, limit=30):
        """
        Find tracks for a specific genre by:
        1. Searching for playlists with the genre name
        2. Getting tracks from those playlists
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

                for item in playlist_tracks["items"]:
                    if item["track"]:  # Ensure there's a valid track
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
                features.extend(batch_features)
            return features
        except Exception as e:
            current_app.logger.error(f"Error getting track features: {str(e)}")
            return []

    # === Artist Methods ===

    def get_artist_top_tracks(self, artist_id, country="US"):
        """Get an artist's top tracks."""
        try:
            results = self.sp_client.artist_top_tracks(artist_id, country=country)
            return results["tracks"]
        except Exception as e:
            current_app.logger.error(f"Error getting artist top tracks: {str(e)}")
            return []

    def get_related_artists(self, artist_id):
        """Get artists related to a given artist."""
        try:
            results = self.sp_client.artist_related_artists(artist_id)
            return results["artists"]
        except Exception as e:
            current_app.logger.error(f"Error getting related artists: {str(e)}")
            return []

    def get_artist_recommendations(self, artist_name, limit=30):
        """
        Get track recommendations based on an artist by:
        1. Finding the artist
        2. Getting their top tracks
        3. Getting related artists and their top tracks
        """
        try:
            # Find the artist
            artists = self.search_artists(artist_name, limit=1)
            if not artists:
                return []

            artist_id = artists[0]["id"]

            # Get artist's top tracks
            top_tracks = self.get_artist_top_tracks(artist_id)

            # Get related artists
            related_artists = self.get_related_artists(artist_id)

            # Get top tracks from related artists
            more_tracks = []
            for related in related_artists[:5]:  # Limit to 5 related artists
                related_top = self.get_artist_top_tracks(related["id"])
                more_tracks.extend(related_top[:3])  # Take top 3 tracks from each

                if len(top_tracks) + len(more_tracks) >= limit:
                    break

            # Combine and limit
            all_tracks = top_tracks + more_tracks
            random.shuffle(all_tracks)  # Shuffle for variety

            return all_tracks[:limit]

        except Exception as e:
            current_app.logger.error(f"Error getting artist recommendations: {str(e)}")
            return []

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    #               User-Specific Methods                    #
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    def get_user_top_tracks(self, time_range="medium_term", limit=20):
        """Get a user's top tracks. Requires authentication."""
        sp = self.get_user_client()
        if not sp:
            raise ValueError("User authentication required")

        try:
            return sp.current_user_top_tracks(limit=limit, time_range=time_range)[
                "items"
            ]
        except Exception as e:
            current_app.logger.error(f"Error getting user top tracks: {str(e)}")
            return []

    def get_user_top_artists(self, time_range="medium_term", limit=20):
        """Get a user's top artists. Requires authentication."""
        sp = self.get_user_client()
        if not sp:
            raise ValueError("User authentication required")

        try:
            return sp.current_user_top_artists(limit=limit, time_range=time_range)[
                "items"
            ]
        except Exception as e:
            current_app.logger.error(f"Error getting user top artists: {str(e)}")
            return []

    def get_personalized_tracks(self, limit=30):
        """
        Get personalized track recommendations based on user's top artists and tracks.

        This is a replacement for the recommendations endpoint, using top artists
        and their related artists to build recommendations.
        """
        sp = self.get_user_client()
        if not sp:
            raise ValueError("User authentication required")

        try:
            # Get user's top artists
            top_artists = self.get_user_top_artists(limit=5)

            if not top_artists:
                return []

            all_tracks = []

            # For each top artist, get their top tracks and tracks from related artists
            for artist in top_artists:
                # Get artist's top tracks
                artist_tracks = self.get_artist_top_tracks(artist["id"])
                all_tracks.extend(artist_tracks[:3])  # Add up to 3 top tracks

                # Get related artists and their top tracks
                related_artists = self.get_related_artists(artist["id"])
                for related in related_artists[
                    :2
                ]:  # Limit to 2 related artists per top artist
                    related_tracks = self.get_artist_top_tracks(related["id"])
                    all_tracks.extend(
                        related_tracks[:2]
                    )  # Add up to 2 tracks per related artist

            # Deduplicate and limit
            unique_tracks = []
            track_ids = set()

            for track in all_tracks:
                if track["id"] not in track_ids:
                    track_ids.add(track["id"])
                    unique_tracks.append(track)

                    if len(unique_tracks) >= limit:
                        break

            # Shuffle for variety
            random.shuffle(unique_tracks)

            return unique_tracks[:limit]

        except Exception as e:
            current_app.logger.error(f"Error getting personalized tracks: {str(e)}")
            return []

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    #                Playlist Methods                        #
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    def create_playlist(self, name, description="", public=False):
        """Create a new playlist for a user. Requires user authentication."""
        sp = self.get_user_client()
        if not sp:
            raise ValueError("User authentication required")

        try:
            user_info = sp.current_user()
            user_id = user_info["id"]

            return sp.user_playlist_create(
                user_id, name, public=public, description=description
            )
        except Exception as e:
            current_app.logger.error(f"Error creating playlist: {str(e)}")
            raise

    def add_tracks_to_playlist(self, playlist_id, track_uris):
        """Add tracks to a playlist. Requires user authentication."""
        sp = self.get_user_client()
        if not sp:
            raise ValueError("User authentication required")

        try:
            # Add tracks in batches (Spotify limits to 100 tracks per request)
            for i in range(0, len(track_uris), 100):
                batch = track_uris[i : i + 100]
                sp.playlist_add_items(playlist_id, batch)

            return True
        except Exception as e:
            current_app.logger.error(f"Error adding tracks to playlist: {str(e)}")
            raise
