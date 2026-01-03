import { API_ROOT } from './config.js';

const data_table_header = document.getElementById("data-table-header");
const data_table_body = document.getElementById("data-table-body");
const playlists_table_header_template = document.getElementById("playlists-table-header-template").content.cloneNode(true);
const playlist_table_header_template = document.getElementById("playlist-table-header-template").content.cloneNode(true);

const controls = document.getElementById("controls");
const container_name = document.getElementById("container-name");
const return_to_playlists_button_template = document.getElementById("return-to-playlists-button-template").content.cloneNode(true);
let return_to_playlists_button = null;

async function* retrievePlaylists() {
    try{
        let params = new URLSearchParams({"check_for_a_play": "false"});
        let result = await fetch(`${API_ROOT}/retrieve_playlists?${params.toString()}`,
            {"method": "GET",
            "credentials": "include"}
        );

        if (result.status !== 200) return null;

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
        console.error("Error fetching playlists:", error);
        return null;
    }
}

async function* retrieveTracks(playlist_id) {
    try{
        let result = await fetch(`${API_ROOT}/retrieve_tracks/${playlist_id}`,
            {"method": "GET",
            "credentials": "include"
            });

        if (result.status !== 200) return null;

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
        console.error("Error fetching tracks:", error);
        return null;
    }
}

async function renderPlaylists(){
    let playlistData = await retrievePlaylists();

    data_table_header.innerHTML = "";
    data_table_header.appendChild(playlists_table_header_template);
    data_table_body.innerHTML = "";

    const playlist_template = document.getElementById("playlist-template").content;

    if (return_to_playlists_button) return_to_playlists_button.remove();
    container_name.innerText = "Playlists";

    for await (const element of playlistData) {
        let playlist = playlist_template.cloneNode(true);
        playlist.querySelector(".playlist-name").textContent = element.name;
        playlist.querySelector(".playlist-id").textContent = element.playlist_id;
        playlist.querySelector(".is-a-play").textContent = element.is_a_play === null ? "Unckecked" : element.is_a_play;
        playlist.querySelector(".open-playlist-button").onclick = async () => {
            container_name.innerText = `Playlist: ${element.name}`;
            await renderTracks(element.playlist_id); 
        };
        data_table_body.appendChild(playlist);
    };
}

async function renderTracks(playlist_id){
    let playlistTracks = await retrieveTracks(playlist_id);

    data_table_header.innerHTML = "";
    data_table_header.appendChild(playlist_table_header_template);
    data_table_body.innerHTML = "";

    const track_template = document.getElementById("track-template").content;

    controls.appendChild(return_to_playlists_button_template.cloneNode(true));
    controls.querySelector("#return-to-playlists-button").onclick = async () => {await renderPlaylists()};
    return_to_playlists_button = controls.querySelector("#return-to-playlists-button");

    for await (const element of playlistTracks) {
        let track = track_template.cloneNode(true);
        track.querySelector(".track-name").textContent = element.name;
        track.querySelector(".artist-name").textContent = element.artist_name;
        track.querySelector(".album-name").textContent = element.album_name;
        track.querySelector(".track-category").textContent = element.is_a_play;
        data_table_body.appendChild(track);
    };
};


await renderPlaylists();