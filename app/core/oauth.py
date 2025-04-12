from google.oauth2 import id_token
from google.auth.transport import requests
from spotipy.oauth2 import SpotifyOAuth
from app.core.config import settings

class GoogleAuth:
    @staticmethod
    async def verify_token(token: str) -> dict:
        try:
            idinfo = id_token.verify_oauth2_token(
                token, requests.Request(), settings.GOOGLE_CLIENT_ID
            )
            return {
                "email": idinfo["email"],
                "name": idinfo.get("name"),
                "picture": idinfo.get("picture")
            }
        except Exception as e:
            raise ValueError(f"Invalid token: {str(e)}")

class SpotifyAuth:
    @staticmethod
    def get_auth_url():
        sp_oauth = SpotifyOAuth(
            client_id=settings.SPOTIFY_CLIENT_ID,
            client_secret=settings.SPOTIFY_CLIENT_SECRET,
            redirect_uri="http://localhost:8000/api/v1/auth/spotify/callback",
            scope="user-read-private user-read-email"
        )
        return sp_oauth.get_authorize_url()

    @staticmethod
    def get_access_token(code: str):
        sp_oauth = SpotifyOAuth(
            client_id=settings.SPOTIFY_CLIENT_ID,
            client_secret=settings.SPOTIFY_CLIENT_SECRET,
            redirect_uri="http://localhost:8000/api/v1/auth/spotify/callback"
        )
        return sp_oauth.get_access_token(code) 