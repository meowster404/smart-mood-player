import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from difflib import SequenceMatcher
import re

def get_spotify_client():
    """Initializes and returns a Spotipy client."""
    # Try to load dotenv if not already loaded
    try:
        from dotenv import load_dotenv
        import os
        # Get current working directory
        cwd = os.getcwd()
        env_file = os.path.join(cwd, '.env')
        if os.path.exists(env_file):
            load_dotenv(env_file)
            print(f"[INFO] Loaded .env file from: {env_file}")
        else:
            print(f"[WARNING] .env file not found at: {env_file}")
    except ImportError:
        print("[WARNING] python-dotenv not available, using existing environment variables")

    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")

    print(f"[DEBUG] Spotify Client ID: {client_id[:5]}... (length: {len(client_id) if client_id else 0})")
    print(f"[DEBUG] Spotify Client Secret: {client_secret[:5]}... (length: {len(client_secret) if client_secret else 0})")

    if not client_id or not client_secret:
        print("[ERROR] Missing Spotify credentials. Please check your .env file.")
        print("You need to set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET in your .env file.")
        print("Get these from https://developer.spotify.com/dashboard")
        return None

    if len(client_id) < 10 or len(client_secret) < 10:
        print("[WARNING] Spotify credentials appear to be too short. Please check your .env file.")
        return None

    try:
        print("[INFO] Creating Spotify client...")
        client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        print("[SUCCESS] Successfully created Spotify client")
        return sp
    except Exception as e:
        print(f"[ERROR] Error connecting to Spotify: {e}")
        print("Please check your Spotify API credentials in the .env file.")
        return None

def normalize_name(name):
    """Normalize artist/track names for better matching."""
    # Convert to lowercase and remove special characters
    normalized = re.sub(r'[^\w\s]', '', name.lower())
    # Remove extra spaces
    normalized = ' '.join(normalized.split())
    return normalized

def string_similarity(a, b):
    """Calculate string similarity ratio."""
    return SequenceMatcher(None, normalize_name(a), normalize_name(b)).ratio()

def _clean_unicode_text(text):
    """Clean Unicode characters that cause encoding issues."""
    if not text:
        return "Unknown"
    try:
        # Test if the text can be encoded
        text.encode('utf-8')
        # Remove common problematic Unicode characters
        import re
        # Remove emojis and other Unicode symbols
        text = re.sub(r'[^\x00-\x7F]+', '', text)
        return text.strip() if text.strip() else "Unknown"
    except (UnicodeEncodeError, UnicodeDecodeError):
        # If there are encoding issues, return a safe fallback
        return "Unknown"

def clean_unicode_text(text):
    """Clean Unicode characters that cause encoding issues."""
    return _clean_unicode_text(text)

def extract_song_and_artist(query):
    """Extract song title and artist from user query with improved pattern matching."""
    # Clean the query first
    query = query.strip().lower()

    # Common patterns in user queries - ordered by specificity (most specific first)
    patterns = [
        # Most specific: "play X by Y" or "play X from Y"
        (r"(?i)play\s+(.+?)\s+(?:by|from|of)\s+(.+)", 2),
        # "I want to hear X by Y" or "I want X by Y"
        (r"(?i)i\s+want\s+(?:to\s+)?(?:hear|listen\s+to|play)\s+(.+?)\s+(?:by|from)\s+(.+)", 2),
        # "can you play X by Y"
        (r"(?i)can\s+you\s+play\s+(.+?)\s+(?:by|from)\s+(.+)", 2),
        # "search for X by Y" or "find X by Y"
        (r"(?i)(?:search|find|look)\s+for\s+(.+?)\s+(?:by|from)\s+(.+)", 2),
        # "X by Y" (most common pattern)
        (r"(?i)(.+?)\s+(?:by|from)\s+(.+)", 2),
        # Artist-only queries: "play songs by X" or "find music by X"
        (r"(?i)(?:play\s+songs?|find\s+(?:songs?|music)|show\s+(?:me\s+)?songs?|listen\s+to\s+songs?)\s+(?:by|from)\s+(.+)", 1, "artist"),
        # Song-only queries: "play X", "search for X"
        (r"(?i)(?:play|search\s+for)\s+(.+)", 1, "song"),
        # "listen to X" - could be either song or artist, default to song
        (r"(?i)listen\s+to\s+(.+)", 1, "song"),
    ]

    for pattern_info in patterns:
        if len(pattern_info) == 3:
            pattern, expected_groups, entity_type = pattern_info
        else:
            pattern, expected_groups = pattern_info
            entity_type = "auto"

        match = re.search(pattern, query)
        if match:
            groups = match.groups()
            if len(groups) == expected_groups:
                if expected_groups == 2:
                    # Both song and artist
                    song_title = groups[0].strip()
                    artist_name = groups[1].strip()
                    return song_title, artist_name
                elif expected_groups == 1:
                    entity = groups[0].strip()
                    
                    if entity_type == "artist":
                        return None, entity
                    elif entity_type == "song":
                        return entity, None
                    else:
                        # Auto-detect based on content
                        # Check if it looks like an artist name (shorter, common artist patterns)
                        if len(entity.split()) <= 2 and not any(word in entity for word in ['song', 'track', 'music']):
                            # Likely an artist
                            return None, entity
                        else:
                            # Likely a song title
                            return entity, None

    # If no pattern matches, assume the whole query is a song title
    return query, None

def search_for_track(sp, query, limit=5):
    """Enhanced track search with improved accuracy and multiple search strategies."""
    try:
        print(f"[DEBUG] Searching for track with query: '{query}'")

        # Try to extract song title and artist from query
        song_title, artist_name = extract_song_and_artist(query)
        try:
            print(f"[DEBUG] Extracted - Song: '{song_title}', Artist: '{artist_name}'")
        except UnicodeEncodeError:
            print(f"[DEBUG] Extracted song and artist (contains Unicode characters)")

        # Strategy 1: If we have both song and artist, try exact match first
        if artist_name and song_title:
            print("[DEBUG] Strategy 1: Searching with both song and artist")
            exact_query = f"track:\"{song_title}\" artist:\"{artist_name}\""
            results = sp.search(q=exact_query, type='track', limit=limit)

            if results and results.get('tracks', {}).get('items'):
                tracks = [_format_track(item) for item in results['tracks']['items'][:limit]]
                print(f"[DEBUG] Found {len(tracks)} tracks with exact match")
                return tracks

        # Strategy 2: Try searching for just the song title
        if song_title:
            print("[DEBUG] Strategy 2: Searching for song title only")
            results = sp.search(q=song_title, type='track', limit=limit*2)

            if results and results.get('tracks', {}).get('items'):
                scored_tracks = []
                seen_tracks = set()  # Track duplicates by (name, artist) combination
                
                for item in results['tracks']['items'][:limit*2]:
                    # Create a unique identifier for this track
                    track_id = (item.get('name', '').lower(), item.get('artists', [{}])[0].get('name', '').lower())
                    
                    # Skip if we've already seen this track
                    if track_id in seen_tracks:
                        continue
                    seen_tracks.add(track_id)
                    
                    score = calculate_track_score(item, song_title, artist_name)
                    scored_tracks.append((score, _format_track(item)))

                # Sort by score and return top results
                scored_tracks.sort(key=lambda x: (x[0], x[1]['popularity']), reverse=True)
                return [track for score, track in scored_tracks[:limit]]

        # Strategy 3: If we have artist name, search for artist and get top tracks
        if artist_name:
            print("[DEBUG] Strategy 3: Searching for artist top tracks")
            artist_tracks = search_for_artist_top_tracks(sp, artist_name)
            if artist_tracks:
                # Filter tracks that contain the song title if we have it
                if song_title:
                    filtered_tracks = [track for track in artist_tracks if song_title.lower() in track['name'].lower()]
                    if filtered_tracks:
                        return filtered_tracks[:limit]
                return artist_tracks[:limit]

        # Strategy 4: Fallback - search for the original query
        print("[DEBUG] Strategy 4: Fallback search with original query")
        results = sp.search(q=query, type='track', limit=limit*2)

        if results and results.get('tracks', {}).get('items'):
            scored_tracks = []
            for item in results['tracks']['items'][:limit*2]:
                score = calculate_track_score(item, song_title or query, artist_name)
                scored_tracks.append((score, _format_track(item)))

            # Sort by score and return top results
            scored_tracks.sort(key=lambda x: (x[0], x[1]['popularity']), reverse=True)
            return [track for score, track in scored_tracks[:limit]]

        print("[DEBUG] No tracks found")
        return []

    except Exception as e:
        print(f"[ERROR] Error searching for tracks: {e}")
        return []

def calculate_track_score(item, song_title, artist_name):
    """Calculate relevance score for a track."""
    if not isinstance(item, dict) or not item.get('artists'):
        return 0.0

    track_name = item.get('name', '').lower()
    track_artist = item['artists'][0].get('name', '').lower()

    score = 0.0

    # Exact matches get highest scores
    if song_title and song_title.lower() == track_name:
        score += 1.0

    if artist_name and artist_name.lower() == track_artist:
        score += 0.8

    # Partial matches
    if song_title:
        song_words = set(song_title.lower().split())
        track_words = set(track_name.split())
        song_matches = len(song_words.intersection(track_words))
        if song_words:
            score += 0.6 * (song_matches / len(song_words))

    if artist_name:
        artist_words = set(artist_name.lower().split())
        track_artist_words = set(track_artist.split())
        artist_matches = len(artist_words.intersection(track_artist_words))
        if artist_words:
            score += 0.4 * (artist_matches / len(artist_words))

    # Boost popular tracks
    popularity = item.get('popularity', 0) / 100.0
    score += 0.2 * popularity

    return min(score, 1.0)  # Cap at 1.0

def _format_track(item):
    """Helper function to format track data consistently with Unicode safety."""
    if not item.get('artists'):
        return {
            'name': item.get('name', 'Unknown Track'),
            'artist': 'Unknown Artist',
            'url': item.get('external_urls', {}).get('spotify', '#'),
            'popularity': item.get('popularity', 0)
        }

    # Get all artists as a single string for better display
    artists = []
    for artist in item['artists']:
        artist_name = artist.get('name', 'Unknown Artist')
        # Clean any problematic Unicode characters
        try:
            # Test if the name can be encoded
            artist_name.encode('utf-8')
            artists.append(artist_name)
        except UnicodeEncodeError:
            # Replace problematic characters
            clean_name = artist_name.encode('ascii', 'ignore').decode('ascii')
            artists.append(clean_name if clean_name else 'Unknown Artist')

    primary_artist = artists[0] if artists else 'Unknown Artist'

    # Clean track name as well
    track_name = item.get('name', 'Unknown Track')
    try:
        track_name.encode('utf-8')
    except UnicodeEncodeError:
        track_name = track_name.encode('ascii', 'ignore').decode('ascii')
        if not track_name:
            track_name = 'Unknown Track'

    return {
        'name': track_name,
        'artist': primary_artist,
        'all_artists': artists,  # Keep all artists for reference
        'url': item.get('external_urls', {}).get('spotify', '#'),
        'popularity': item.get('popularity', 0)
    }

def search_for_artist_top_tracks(sp, artist_name):
    """Enhanced artist search with better name matching and fuzzy search."""
    try:
        print(f"[DEBUG] Searching for artist: '{artist_name}'")

        # Search for artist with various name formats and fuzzy matching
        search_results = []

        # Try different name variations and search strategies
        name_variations = [
            artist_name,
            artist_name.upper(),
            artist_name.lower(),
            # Handle cases like "LiSA" vs "LISA"
            re.sub(r'([A-Z])([A-Z]+)', r'\1\2.lower()', artist_name),
            # Try without special characters
            re.sub(r'[^\w\s]', '', artist_name),
        ]

        # Also try partial matches if exact doesn't work
        if len(artist_name.split()) > 1:
            # For multi-word artist names, try individual words
            words = artist_name.split()
            for word in words:
                if len(word) > 2:  # Only meaningful words
                    name_variations.append(word)

        for variation in name_variations:
            if not variation or len(variation) < 2:
                continue

            try:
                # Search for exact artist match
                results = sp.search(q=f"artist:\"{variation}\"", type='artist', limit=5)
                if results and 'artists' in results and results['artists']['items']:
                    for artist in results['artists']['items']:
                        similarity = string_similarity(artist['name'], artist_name)
                        # Boost similarity for exact matches
                        if artist['name'].lower() == artist_name.lower():
                            similarity = 1.0
                        search_results.append((similarity, artist))

                # Also try general search if no exact match
                if not search_results:
                    general_results = sp.search(q=variation, type='artist', limit=3)
                    if general_results and 'artists' in general_results and general_results['artists']['items']:
                        for artist in general_results['artists']['items']:
                            similarity = string_similarity(artist['name'], artist_name)
                            search_results.append((similarity, artist))

            except Exception as e:
                print(f"[WARNING] Error searching for artist variation '{variation}': {e}")
                continue

        if not search_results:
            print(f"[DEBUG] No artist matches found for: {artist_name}")
            return []

        # Sort by similarity and get the best match
        search_results.sort(key=lambda x: (x[0], x[1]['popularity']), reverse=True)
        best_match = search_results[0][1]

        print(f"[DEBUG] Best artist match: '{best_match['name']}' (similarity: {search_results[0][0]:.2f})")

        # Get top tracks for the best matching artist
        top_tracks_results = sp.artist_top_tracks(best_match['uri'])

        tracks = []
        if top_tracks_results and top_tracks_results.get('tracks'):
            for track in top_tracks_results['tracks']:
                if isinstance(track, dict) and track.get('artists'):
                    tracks.append(_format_track(track))

            # Sort by popularity
            tracks.sort(key=lambda x: x['popularity'], reverse=True)

        print(f"[DEBUG] Found {len(tracks)} top tracks for artist")
        return tracks[:10]  # Return top 10 tracks

    except Exception as e:
        print(f"[ERROR] Error searching for artist top tracks: {e}")
        return []

def search_for_playlists(sp, query, limit=10):
    """Enhanced playlist search with better relevance ranking and fallback terms."""
    try:
        # Try the original query first
        results = sp.search(q=query, type='playlist', limit=limit*2)
        playlists = []

        if results and 'playlists' in results:
            items = results['playlists']['items']

            # Score and sort playlists
            scored_playlists = []
            for item in items:
                if not isinstance(item, dict):
                    continue

                # Calculate relevance score based on multiple factors
                name_match = string_similarity(item.get('name', ''), query)
                followers = item.get('followers', {}).get('total', 0)
                track_count = item.get('tracks', {}).get('total', 0)

                # Combined score considering popularity and relevance
                score = (name_match * 0.5) + (min(followers/1000, 1) * 0.3) + (min(track_count/100, 1) * 0.2)

                scored_playlists.append((score, {
                    'name': clean_unicode_text(item.get('name', 'Unknown Playlist')),
                    'owner': clean_unicode_text(item.get('owner', {}).get('display_name', 'Unknown Creator')),
                    'url': item.get('external_urls', {}).get('spotify', '#'),
                    'tracks_total': track_count,
                    'followers': followers
                }))

            # Sort by score and limit results
            scored_playlists.sort(key=lambda x: x[0], reverse=True)
            playlists = [playlist for score, playlist in scored_playlists[:limit]]

        # If no good results, try fallback search terms
        if not playlists or len(playlists) < 3:
            fallback_queries = [
                "music",  # Very generic fallback
                "songs",  # Alternative generic term
                "playlist"  # Most generic fallback
            ]

            for fallback_query in fallback_queries:
                if len(playlists) >= limit:
                    break

                try:
                    fallback_results = sp.search(q=fallback_query, type='playlist', limit=limit)
                    if fallback_results and 'playlists' in fallback_results:
                        for item in fallback_results['playlists']['items'][:limit-len(playlists)]:
                            if not isinstance(item, dict):
                                continue

                            # Check if we already have this playlist
                            if not any(p['url'] == item.get('external_urls', {}).get('spotify', '#') for p in playlists):
                                playlists.append({
                                    'name': clean_unicode_text(item.get('name', 'Unknown Playlist')),
                                    'owner': clean_unicode_text(item.get('owner', {}).get('display_name', 'Unknown Creator')),
                                    'url': item.get('external_urls', {}).get('spotify', '#'),
                                    'tracks_total': item.get('tracks', {}).get('total', 0),
                                    'followers': item.get('followers', {}).get('total', 0)
                                })
                except Exception as e:
                    print(f"Error in fallback playlist search: {e}")
                    continue

        return playlists[:limit]  # Ensure we don't exceed the limit
    except Exception as e:
        print(f"An error occurred while searching for playlists: {e}")
        return []