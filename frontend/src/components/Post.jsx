import { createSignal } from "solid-js";
import Comment from "./Comment";
import axios from "axios";

import config from '../config';

const API_URL = config.API_URL;
const IMAGE_URL = config.IMAGE_URL;

function Post({ post, fetchPosts, currentUser, loggedIn }) {
  const [commentContent, setCommentContent] = createSignal("");
  const [isEditing, setIsEditing] = createSignal(false);
  const [editedCaption, setEditedCaption] = createSignal(post.caption);

  const handleDeletePost = async () => {
    const confirmDelete = window.confirm("Delete this post?");
    if (!confirmDelete) return;
    const token = localStorage.getItem("jwt");
    await axios.delete(`${API_URL}/api/post/${post.id}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    fetchPosts(); // Refresh the posts after deletion
  };

  const handleEditPost = async () => {
    const token = localStorage.getItem("jwt");
    await axios.put(`${API_URL}/api/post/${post.id}/`, {
      caption: editedCaption()
    }, {
      headers: { Authorization: `Bearer ${token}` }
    });
    setIsEditing(false); // Exit edit mode
    fetchPosts(); // Refresh the posts after editing
  };

  const handleAddComment = async (post_id) => {
    const token = localStorage.getItem("jwt");

    await axios.post(`${API_URL}/api/comment`, {
      post_id: post_id,
      content: commentContent()
    }, {
      headers: { Authorization: `Bearer ${token}` }
    });
    setCommentContent(""); // Clear input after adding
    fetchPosts(); // Refresh the posts
  };
  console.log(post)
  console.log(post.image_path)

  return (
    <div class="post">
      <p><strong>{post.author.username}</strong></p>
      {isEditing() ? (
        <div>
          <input
            type="text"
            value={editedCaption()}
            onInput={(e) => setEditedCaption(e.target.value)}
            class="caption-input"
          />
          <button class="edit-button" onClick={handleEditPost}>Save</button>
          <button class="edit-button" onClick={() => setIsEditing(false)}>Cancel</button>
        </div>
      ) : 
        (currentUser === post.author.username) ? (
    
    <>
          <p>{post.caption}</p>
          <button onClick={() => setIsEditing(true)}>Edit</button>
        </>
      
    ): (

      <>
          <p>{post.caption}</p>
        </>
    )}
      

  
      <p>Posted on {new Date(post.created_at + "Z").toLocaleString(undefined, {hour12: true})}</p>
      
      {post.image_path && (
        <img 
          src={`${IMAGE_URL}/${post.image_path}`}
          alt={`Post by ${post.author.username}`} 
          style={{ maxWidth: '100%', height: 'auto' }} 
        />
      )}
      
      {currentUser === post.author.username && (
        <div>
        <button onClick={() => handleDeletePost()}>Delete Post</button>
        </div>
      )}
      
      <div class="comments">
        <p>Comments:</p>
        {post.comments.map(comment => (
          <Comment 
            key={comment.id} 
            comment={comment} 
            postId={post.id} 
            fetchPosts={fetchPosts}
            currentUser={currentUser}
          />
        ))}
  
        {loggedIn() && (
          <div>
            <input 
              type="text" 
              placeholder="Add a comment" 
              value={commentContent()} 
              onInput={(e) => setCommentContent(e.target.value)} 
            />
            <button onClick={() => handleAddComment(post.id)}>Add Comment</button>
          </div>
        )}
      </div>
    </div>
  );
  
}

export default Post;
