import { API_ROOT } from "./config.js";

const spotifyAuthorizeURL = `${API_ROOT}/authorize_spotify/`;
let _accessToken = null;

export async function fetchAccessToken() {
    const result = await fetch(`${API_ROOT}/get_access_token/`,
    {headers: {'Content-Type': 'application/json'},
    credentials: 'include'});
    const data = await result.json();

    return data;
}

export function setAccessToken(token) {
    _accessToken = token;
}

export function getAccessToken() {
    return _accessToken;
}

const loginButton = document.getElementById("loginButton");
if (loginButton) {
    loginButton.addEventListener("click", () => {window.location.href = spotifyAuthorizeURL;});
}