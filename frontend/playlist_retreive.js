import { API_ROOT } from './config.js';
import { getAccessToken } from './auth.js';

async function retrievePlaylists() {
    try{
        let result = await fetch(`${API_ROOT}/retrieve_playlists/`,
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

let playlists = await retrievePlaylists();
console.log(playlists);
