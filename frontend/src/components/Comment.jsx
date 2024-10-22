import axios from "axios";
import { createSignal } from "solid-js";

import config from '../config';

const API_URL = config.API_URL;

function Comment({ comment, postId, fetchPosts, currentUser }) {
  const [isEditing, setIsEditing] = createSignal(false);
  const [editedContent, setEditedContent] = createSignal(comment.content);
  const handleDeleteComment = async () => {
    const confirmDelete = window.confirm("Delete this comment?");
    if (!confirmDelete) return;
    const token = localStorage.getItem("jwt"); // Function to get the JWT token
    await axios.delete(`${API_URL}/api/comment/${comment.id}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    fetchPosts(); // Refresh the posts after deletion
  };

  const handleEditComment = async () => {
    const token = localStorage.getItem("jwt");
    await axios.put(`${API_URL}/api/comment/${comment.id}/`, {
      content: editedContent()
    }, {
      headers: { Authorization: `Bearer ${token}` }
    });
    setIsEditing(false); // Exit edit mode
    fetchPosts(); // Refresh the posts after editing
  };

  return (
    <div class="comment">
      <p><strong>{comment.author.username}</strong>: </p>
      {isEditing() ? (
        <div>
          <input
            type="text"
            value={editedContent()}
            onInput={(e) => setEditedContent(e.target.value)}
          />
          <button class="edit-button" onClick={handleEditComment}>Save</button>
          <button onClick={() => setIsEditing(false)}>Cancel</button>
        </div>
      ) : (
        <>
          <p>{comment.content}</p>
          <p>({new Date(comment.created_at + "Z").toLocaleString(undefined, { hour12: true })})</p>
          {currentUser === comment.author.username && (
            <button class="edit-button"  onClick={() => setIsEditing(true)}>Edit</button>
          )}
        </>
      )}
      
      {currentUser === comment.author.username && (
        <button onClick={handleDeleteComment}>Delete</button>
      )}
    </div>
  );
  
}

export default Comment;
