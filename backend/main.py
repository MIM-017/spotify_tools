from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from starlette.responses import RedirectResponse

from backend.schemas import Playlist
from backend.security import *
from backend.services.playlist_cleaner import PlaylistCleaner

origins = ["http://127.0.0.1:5500"]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(auth_router)

playlist_cleaner = PlaylistCleaner()


@app.get("/playlist_formatted/{playlist_id}")
async def get_playlist_kuci_formatted(playlist_id: str):
    result = playlist_cleaner.get_playlist_kuci_formatted(playlist_id=playlist_id)
    return list(result)


@app.get("/refine_playlist/{playlist_id}")
async def refine_playlist(playlist_id: str):
    playlist_cleaner.refine_playlist(playlist_id=playlist_id)


@app.get("/retrieve_playlists")
async def retrieve_playlists(check_for_a_play: bool | None = False) -> list[Playlist]:
    return list(playlist_cleaner.get_marked_playlists(
        check_for_a_play=check_for_a_play))  # TODO: Consider converting to a stream for better performance


@app.get("/authorize_spotify")
async def authorize_spotify():
    return RedirectResponse(f"{playlist_cleaner.auth_manager.get_authorize_url()}")
