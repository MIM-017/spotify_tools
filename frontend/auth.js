import { API_ROOT } from "./config.js";

const spotifyAuthorizeURL = `${API_ROOT}/authorize_spotify`;
const tokenCheckURL = `${API_ROOT}/check_tokens`;
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

async function checkTokens() {
    const result = await fetch(tokenCheckURL, {"credentials": "include"});
    console.log(result.status);
    console.log("Test");
    if (result.status !== 200) {
        window.location.href = spotifyAuthorizeURL;
    }
    else if(result.status === 200) {
        window.location.href = "/dashboard.html";
    }
}

const loginButton = document.getElementById("loginButton");
if (loginButton) {
    loginButton.addEventListener("click", async () => await checkTokens());
}