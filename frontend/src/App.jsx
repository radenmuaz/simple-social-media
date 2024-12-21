import { createSignal, createEffect, onMount } from "solid-js";
import axios from "axios";
import Home from "./pages/Home";
import Login from "./pages/Login";
import './App.css'

import config from './config';

const API_URL = config.API_URL;


function checkAuth(setLoggedIn, setCurrentUser) {
  const token = localStorage.getItem("jwt");

  if (token)
    axios.get(`${API_URL}/api/check-auth`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    .then(response => {
      console.log(response.data)
      setLoggedIn(true);
      setCurrentUser(response.data.username);
  })
    .catch(() => {
      console.log(response.data)
      setLoggedIn(false);
      setCurrentUser("");
    });

}

function App() {
  const [loggedIn, setLoggedIn] = createSignal(false);
  const [currentUser, setCurrentUser] = createSignal("");

// On mount, check if the user is authenticated
  onMount(async () => {
    checkAuth(setLoggedIn, setCurrentUser);
  });

  return (
    <div class="container">
      <Login 
        loggedIn={loggedIn} 
        setLoggedIn={setLoggedIn} 
        currentUser={currentUser} 
        setCurrentUser={setCurrentUser} 
      />
      <Home  
        loggedIn={loggedIn} 
        setLoggedIn={setLoggedIn} 
        currentUser={currentUser} 
        setCurrentUser={setCurrentUser} 
      />
    </div>
  );
  
}

export default App;
