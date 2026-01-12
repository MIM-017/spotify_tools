# ---------------FAST API CONFIG---------------

ORIGINS = ["http://127.0.0.1:5500"]

# ---------------Playlist Cleaner CONFIG---------------

CLIENT_ID = "03775c1ad3054917ae9f05d01caeb9ed"
REDIRECT_URI = "http://127.0.0.1:8000/authorize_user"

# ---------------Security CONFIG---------------

ACCESS_TOKEN_EXPIRE = 60 * 60 * 24  # Time in hours = 1 day
REFRESH_TOKEN_EXPIRE = 60 * 60 * 24 * 14  # Time in hours = 2 weeks