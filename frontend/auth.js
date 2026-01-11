import { API_ROOT } from "./config.js";

const spotifyAuthorizeURL = `${API_ROOT}/authorize_spotify`;
const tokenCheckURL = `${API_ROOT}/check_tokens`;
const logoutURL = `${API_ROOT}/logout`;

export async function fetchAccessToken() {
    const result = await fetch(`${API_ROOT}/get_access_token/`,
    {headers: {'Content-Type': 'application/json'},
    credentials: 'include'});
    const data = await result.json();

    return data;
}

async function checkTokens() {
    const result = await fetch(tokenCheckURL, {"credentials": "include"});
    if (result.status !== 200) {
        window.location.href = spotifyAuthorizeURL;
    }
    else if(result.status === 200) {
        window.location.href = "/dashboard.html";
    }
}

export async function fetchWithAuthCheck(url, params){
    const result = await fetch(url, params);
    if (result.status === 401){
        await checkTokens();
    }
    else{
        return result;
    }
}

async function logout(){
    window.location.href = logoutURL;
}

const loginButton = document.getElementById("loginButton");
if (loginButton) {
    loginButton.addEventListener("click", async () => await checkTokens());
}

const logoutButton = document.getElementById("logout-button");
if (logoutButton) {
    logoutButton.addEventListener("click", async () => await logout());
}