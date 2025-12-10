import { API_ROOT } from './config.js';
import { getAccessToken } from './auth.js';

async function retrievePlaylists() {
    try{
        let params = new URLSearchParams({"check_for_a_play": document.getElementById("check-for-a-play").checked.toString()});
        let result = await fetch(`${API_ROOT}/retrieve_playlists/?${params.toString()}`,
            {headers: {'Content-Type': 'application/json',
            authorization: `Bearer ${getAccessToken()}`}
        });

        if (result.status !== 200) return null;

        result = await result.json();
        return result;

    } catch (error) {
        console.log("Error fetching playlists:", error);
        return null;
    }
}

document.getElementById("retrieve").addEventListener("click", async () => retrievePlaylists());