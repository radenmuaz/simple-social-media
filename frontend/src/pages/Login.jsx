import { createSignal } from "solid-js";
import axios from "axios";

import config from '../config';

const API_URL = config.API_URL;

function Login({loggedIn, setLoggedIn, currentUser, setCurrentUser}) {
  const [username, setUsername] = createSignal("");
  const [password, setPassword] = createSignal("");
  const [signupUsername, setSignupUsername] = createSignal("");
  const [signupEmail, setSignupEmail] = createSignal("");
  const [signupPassword, setSignupPassword] = createSignal("");
  const [retypePassword, setRetypePassword] = createSignal("");

  const [error, setError] = createSignal(null);

  
  const handleLogin = () => {

    axios.post(`${API_URL}/api/login`, { username: username(), password: password() })
      .then(response => {
        localStorage.setItem("jwt", response.data.access_token);  // Save token to localStorage
        setLoggedIn(true);
        setCurrentUser(response.data.username);
        window.location.reload();
    })
      .catch(() => setError("Login failed!"));
  };

  const handleLogout = () => {

    axios.post(`${API_URL}/api/logout`, { username: username(), password: password() })
      .then(response => {
        localStorage.setItem("jwt", null);
        setLoggedIn(false);
        setCurrentUser("");
        window.location.reload();

    })
      .catch(() => setError("Login failed!"));
  };

  const handleSignup = () => {
    if (signupPassword() !== retypePassword()) {
      setError("Passwords do not match!");
      return;
    }

    axios
      .post(`${API_URL}/api/signup`, {
        username: signupUsername(),
        email: signupEmail(),
        password: signupPassword(),
      })
      .then((response) => {
        setSignupUsername("")
        setSignupEmail("")
        setSignupPassword("")
        setRetypePassword("")
        setError("Signed up, try login")
      })
      .catch(() => setError("Signup failed!"));
  };

  return (
    <>
      {loggedIn() ? (
        <>
          <p>Logged in as: {currentUser()}</p>
          <div>
            <button onClick={handleLogout} class="logout-button">Logout</button>
          </div>
        </>
      ) : (
        <>
          <div class="login-signup">
            <h1>Socmed</h1>
            
            <div>
              <h2>Login</h2>
              <div>
                <input 
                  type="text" 
                  placeholder="Username" 
                  onInput={(e) => setUsername(e.target.value)} 
                />
              </div>
              <div>
                <input 
                  type="password" 
                  placeholder="Password" 
                  onInput={(e) => setPassword(e.target.value)} 
                />
              </div>
              <div>
                <button onClick={handleLogin}>Login</button>
              </div>
            </div>
  
            <div>
              <h2>Signup</h2>
              <div>
                <input 
                  type="text" 
                  placeholder="Username" 
                  value={signupUsername()} 
                  onInput={(e) => setSignupUsername(e.target.value)} 
                />
              </div>
              <div>
                <input 
                  type="text" 
                  placeholder="Email" 
                  value={signupEmail()}  
                  onInput={(e) => setSignupEmail(e.target.value)} 
                />
              </div>
              <div>
                <input 
                  type="password" 
                  placeholder="Password" 
                  value={signupPassword()} 
                  onInput={(e) => setSignupPassword(e.target.value)} 
                />
              </div>
              <div>
                <input 
                  type="password" 
                  placeholder="Retype Password"  
                  value={retypePassword()} 
                  onInput={(e) => setRetypePassword(e.target.value)} 
                />
              </div>
              <div>
                <button onClick={handleSignup}>Sign Up</button>
              </div>
              <h1>{error() && <p class="error">{error()}</p>}</h1>
            </div>
          </div>
        </>
      )}
    </>
  );
  
}

export default Login;
