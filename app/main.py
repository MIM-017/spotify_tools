import spotipy
import playlist_cleaner
#
p = playlist_cleaner.PlaylistCleaner()
# print(p.get_marked_playlists("41gDnmL2BjwU7KfXtDIGAa"))
p.refine_playlist(playlist_id="78yNIoqgKrDOQMXWPKDO0P")
result = p.check_playlist("78yNIoqgKrDOQMXWPKDO0P")
for i in result:
    print(i)

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

from pydantic import Field