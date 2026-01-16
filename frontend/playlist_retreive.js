import { API_ROOT } from './config.js';
import { fetchWithAuthCheck } from './auth.js';

const data_table_header = document.getElementById("data-table-header");
const data_table_body = document.getElementById("data-table-body");
const playlists_table_header_template = document.getElementById("playlists-table-header-template").content.cloneNode(true);
const playlist_table_header_template = document.getElementById("playlist-table-header-template").content.cloneNode(true);

const controls = document.getElementById("controls");
const container_name = document.getElementById("container-name");
const return_to_playlists_button_template = document.getElementById("return-to-playlists-button-template").content.cloneNode(true);
let return_to_playlists_button = null;
const check_for_a_play_button_template = document.getElementById("check-for-a-play-button-template").content.cloneNode(true);
let check_for_a_play_button = document.getElementById("check-for-a-play-button");

let controller;

function cancelOngoingFetch(){
    if (controller) controller.abort();

    controller = new AbortController();
    return controller.signal;
}

async function* retrievePlaylists(check_for_a_play = false, signal) {
    try{
        let params = new URLSearchParams({"check_for_a_play": check_for_a_play.toString()});
        let result = await fetchWithAuthCheck(`${API_ROOT}/retrieve_playlists?${params.toString()}`,
            {"method": "GET",
            "credentials": "include",
            "signal": signal}
        );

        if (result.status !== 200) return;

        result = result.body.getReader();

        const decoder = new TextDecoder();
        let buffer = "";
        
        while (true) {
            const { done, value } = await result.read();
            if (done) break;
            buffer += decoder.decode(value, {stream: true});

            const lines = buffer.split('\n');
            buffer = lines.pop();
            
            for (const line of lines) {
                if (line.trim()) {
                    yield JSON.parse(line);
                }
            }
            
        }
        if (buffer.trim()){
            yield JSON.parse(buffer.trim());
        }
    } 
    catch (error) {
        if (error.name === "AbortError") return;

        console.error("Error fetching playlists:", error);
        return;
    }
}

async function* retrieveTracks(playlist_id, check_for_a_play = false, signal) {
    try{
        let params = new URLSearchParams({"check_for_a_play": check_for_a_play.toString()});
        let result = await fetchWithAuthCheck(`${API_ROOT}/retrieve_tracks/${playlist_id}?${params.toString()}`,
            {"method": "GET",
            "credentials": "include",
            "signal": signal});

        if (result.status !== 200) return;

        result = result.body.getReader();

        const decoder = new TextDecoder();
        let buffer = "";
        
        while (true) {
            const { done, value } = await result.read();
            if (done) break;
            buffer += decoder.decode(value, {stream: true});

            const lines = buffer.split('\n');
            buffer = lines.pop();
            
            for (const line of lines) {
                if (line.trim()) {
                    yield JSON.parse(line);
                }
            }
            
        }
        if (buffer.trim()){
            yield JSON.parse(buffer.trim());
        }
    }
    catch (error) {
        if (error.name === "AbortError") return;

        console.error("Error fetching tracks:", error);
        return;
    }
}

async function renderPlaylists(check_for_a_play = false){
    let signal = cancelOngoingFetch();

    let playlistData = retrievePlaylists(check_for_a_play, signal);

    data_table_header.innerHTML = "";
    data_table_header.appendChild(playlists_table_header_template.cloneNode(true));
    data_table_body.innerHTML = "";

    const playlist_template = document.getElementById("playlist-template").content;

    if (return_to_playlists_button) return_to_playlists_button.remove();
    container_name.innerText = "Playlists";

    if (check_for_a_play_button) check_for_a_play_button.onclick = () => renderPlaylists(true);

    let counter = 1;
    for await (const element of playlistData) {
        let playlist = playlist_template.cloneNode(true);
        playlist.querySelector(".playlist-index").textContent = counter++;
        playlist.querySelector(".playlist-name").textContent = element.name;
        playlist.querySelector(".playlist-id").textContent = element.playlist_id;
        playlist.querySelector(".is-a-play").textContent = element.is_a_play === null ? "Unchecked" : element.is_a_play;
        playlist.querySelector(".open-playlist-button").onclick = async () => {
            container_name.innerText = `Playlist: ${element.name}`;
            await renderTracks(element.playlist_id); 
        };
        data_table_body.appendChild(playlist);
    };
}

async function renderTracks(playlist_id, check_for_a_play = false){
    let signal = cancelOngoingFetch();

    let playlistTracks = retrieveTracks(playlist_id, check_for_a_play, signal);

    data_table_header.innerHTML = "";  // Preparing the table for data insertion
    data_table_header.appendChild(playlist_table_header_template.cloneNode(true));
    data_table_body.innerHTML = "";

    const track_template = document.getElementById("track-template").content;  // Getting the track template

    controls.insertBefore(return_to_playlists_button_template.cloneNode(true), controls.querySelector("#logout-button"));  // Adding the return to playlists button
    return_to_playlists_button = controls.querySelector("#return-to-playlists-button");
    return_to_playlists_button.onclick = async () => {await renderPlaylists()};

    if (check_for_a_play_button) check_for_a_play_button.onclick = async () => {
        await addAPlayDataToTracks(playlist_id);
    }

    let counter = 1;
    for await (const element of playlistTracks) {
        let track = track_template.cloneNode(true);
        track.querySelector(".track-index").textContent = counter++;
        track.querySelector(".track-name").textContent = element.name;
        track.querySelector(".artist-name").textContent = element.artists.map(artist => artist.name).join(", ");
        track.querySelector(".album-name").textContent = element.album.name;
        track.querySelector(".is-a-play").textContent = element.is_a_play === null ? "Unchecked" : element.is_a_play;
        track.firstElementChild.setAttribute("track_id", element.track_id);  // Adding the track ID to add A_Play information in the future
        data_table_body.appendChild(track);
    };
};

async function addAPlayDataToTracks(playlist_id){
    let signal = cancelOngoingFetch();

    let playlistTracks = retrieveTracks(playlist_id, true, signal);

    for (const track_row of data_table_body.querySelectorAll(".table-data-row")){  // Adding the loading animation to A-Play field
        track_row.querySelector(".is-a-play").textContent = "Loading..."
    }

    for await (const track of playlistTracks) {
        const track_id = track.track_id;
        data_table_body.querySelector(`[track_id="${track_id}"]`).querySelector(".is-a-play").textContent = track.is_a_play;
    }
}

await renderPlaylists();