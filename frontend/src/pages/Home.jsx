import { createSignal, onMount } from "solid-js";
import axios from "axios";
import Post from "../components/Post";

import config from '../config';

const API_URL = config.API_URL;

function Home({loggedIn, setLoggedIn, currentUser, setCurrentUser}) {
  const [posts, setPosts] = createSignal([]);
  const [caption, setCaption] = createSignal("");
  const [file, setFile] = createSignal(null);
  const [filename, setFilename] = createSignal("");


  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setFilename(selectedFile.name); // Store the filename
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const formData = new FormData();
    if (file())
      formData.append("file", file());
    formData.append("caption", caption());

    const token = localStorage.getItem("jwt");
    console.log(formData.get('caption'))

    try {
      await axios.post(`${API_URL}/api/post`, formData, {
        headers: {
          "Authorization": `Bearer ${token}`,
          // "Content-Type": "multipart/form-data"
        }
      });
      setCaption(""); // Reset form after submission
      setFile(null);
      fetchPosts(); // Fetch updated posts after submission
    } catch (error) {
      console.error("Error uploading post:", error);
    }
  };
  
  const fetchPosts = () => {
    axios.get(`${API_URL}/api/post`)
      .then(response => 
        {
        console.log("here");
        console.log(response.data);
        setPosts(response.data);
        console.log("there");
      })
      .catch((e) => {
        console.log("error",e)
        // localStorage.removeItem("jwt");
        // setLoggedIn(false);
        // setCurrentUser("");
      });
  };

  onMount(fetchPosts);  // Fetch posts when the component is mounted

  

  return (
    <div class="container feed">
      <div>
        {loggedIn() ? (
          <div>
      <h2>Write a new post:</h2>
      <form onSubmit={handleSubmit}>
              <input 
                type="text" 
                value={caption()} 
                onInput={(e) => setCaption(e.target.value)} 
                placeholder="What's up"
                class="caption-input"
                required 
              />
               <label class="file-label">
               Choose a picture
              <input 
                type="file" 
                accept="image/*" 
                onChange={handleFileChange} 
              />
              </label>
              {filename() && <p>Selected file: {filename()}</p>} {/* Show the filename */}
              <button class="upload-button"type="submit">Upload Post</button>
            </form>
          </div>
        ) : (
          <h3>Log in to write new post</h3>
        )}
      </div>
  
      <div>
        <h2>Feed</h2>
        {posts().sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).map(post => (
          <Post 
            key={post.id} 
            post={post} 
            fetchPosts={fetchPosts} 
            currentUser={currentUser()} 
            loggedIn={loggedIn} 
          />
        ))}
      </div>
    </div>
  );
  
}

export default Home;
