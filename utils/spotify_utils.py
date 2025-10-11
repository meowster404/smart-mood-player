# utils/spotify_utils.py
import os, spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def get_spotify_client():
    """Initializes and returns a Spotipy client."""
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")

    if not client_id or not client_secret:
        return None

    try:
        client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        return sp
    except Exception as e:
        print(f"Error connecting to Spotify: {e}")
        return None

def search_for_playlists(sp, query, limit=10):
    """Searches for playlists based on a query."""
    try:
        results = sp.search(q=query, type='playlist', limit=limit)
        playlists = []
        # --- ERROR FIX ---
        # Safely access nested data using .get() to prevent crashes on empty results
        playlists_data = results.get('playlists')
        if playlists_data:
            items = playlists_data.get('items')
            if items:
                for item in items:
                    # Ensure the item is a valid dictionary before accessing keys
                    if isinstance(item, dict):
                        playlists.append({
                            'name': item.get('name', 'Unknown Playlist'),
                            'owner': item.get('owner', {}).get('display_name', 'Unknown Artist'),
                            'url': item.get('external_urls', {}).get('spotify', '#'),
                        })
        return playlists
        # --- END FIX ---
    except Exception as e:
        print(f"An error occurred while searching for playlists: {e}")
        return []


def search_for_track(sp, track_name, limit=10):
    """Searches for a specific track by name."""
    try:
        results = sp.search(q=f"track:{track_name}", type='track', limit=limit)
        tracks = []
        # --- ERROR FIX ---
        tracks_data = results.get('tracks')
        if tracks_data:
            items = tracks_data.get('items')
            if items:
                for item in items:
                    if isinstance(item, dict) and item.get('artists'):
                        tracks.append({
                            'name': item.get('name', 'Unknown Track'),
                            'artist': item.get('artists')[0].get('name', 'Unknown Artist'),
                            'url': item.get('external_urls', {}).get('spotify', '#'),
                        })
        return tracks
        # --- END FIX ---
    except Exception as e:
        print(f"An error occurred while searching for tracks: {e}")
        return []


def search_for_artist_top_tracks(sp, artist_name):
    """Searches for an artist and returns their top tracks."""
    try:
        results = sp.search(q=f"artist:{artist_name}", type='artist', limit=1)
        # --- ERROR FIX ---
        artists_data = results.get('artists')
        if not artists_data or not artists_data.get('items'):
            return []
        # --- END FIX ---

        artist_uri = artists_data['items'][0]['uri']
        top_tracks_results = sp.artist_top_tracks(artist_uri)

        tracks = []
        if top_tracks_results and top_tracks_results.get('tracks'):
            for track in top_tracks_results['tracks']:
                 if isinstance(track, dict) and track.get('artists'):
                    tracks.append({
                        'name': track.get('name', 'Unknown Track'),
                        'artist': track.get('artists')[0].get('name', 'Unknown Artist'),
                        'url': track.get('external_urls', {}).get('spotify', '#'),
                    })
        return tracks
    except Exception as e:
        print(f"An error occurred while searching for artist top tracks: {e}")
        return []