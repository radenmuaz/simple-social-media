import requests

API_URL = "http://127.0.0.1:8000/api"

# 1. User Signup
def signup(username, email, password):
    url = f"{API_URL}/signup/"
    data = {"username": username, "email": email, "password": password}
    response = requests.post(url, json=data)
    print(f"Signup: {response.status_code}, {response.json()}")
    return response


# 2. User Login (assuming JWT is returned on login)
def login(username, password):
    url = f"{API_URL}/login/"
    data = {"username": username, "password": password}
    response = requests.post(url, json=data)
    print(f"Login: {response.status_code}, {response.json()}")
    if response.status_code == 200:
        token = response.json().get("access_token")
        return token
    return None


# 3. User Logout (assuming a session-based logout endpoint)

def logout(token):
    url = f"{API_URL}/logout"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(url, headers=headers)
    print(f"Logout: {response.status_code}, {response.json()}")

# 4. Check current logged-in user
def check_current_user(token):
    url = f"{API_URL}/check-auth/"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    print(f"Check Current User: {response.status_code}, {response.json()}")


def create_post(token, caption):
    url = f"{API_URL}/post/"
    headers = {"Authorization": f"Bearer {token}", }
    data = {"caption": caption}
    files = {"file": None}
    # files = None
    response = requests.post(url, data=data, headers=headers, files=files)
    # data = {"caption": caption, "file":None}
    # response = requests.post(url, data=data, headers=headers)
    print(f"Create Post: {response.status_code}, {response.json()}")
    return response.json()["id"]


def read_all_posts(token):
    url = f"{API_URL}/post/"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    print(f"Read All Posts: {response.status_code}, {response.json()}")


def update_post(token, post_id, new_caption):
    url = f"{API_URL}/post/{post_id}/"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {"caption": new_caption}
    response = requests.put(url, json=data, headers=headers)
    print(f"Update Post: {response.status_code}, {response.json()}")

def delete_post(token, post_id):
    url = f"{API_URL}/post/{post_id}/"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(url, headers=headers)
    print(f"Delete Post: {response.status_code}, {response.json()}")


# 6. Create, Read, Update, Delete (CRUD) Comment
def create_comment(token, post_id, content):
    url = f"{API_URL}/comment/"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {"post_id": post_id, "content": content}
    response = requests.post(url, json=data, headers=headers)
    print(f"Create Comment: {response.status_code}, {response.json()}")
    return response.json()["id"]


def read_all_comments_for_post(token, post_id):
    url = f"{API_URL}/post/{post_id}/comments/"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    print(f"Read All Comments: {response.status_code}, {response.json()}")


def update_comment(token, comment_id, new_content):
    url = f"{API_URL}/comment/{comment_id}/"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {"content": new_content}
    response = requests.put(url, json=data, headers=headers)
    print(f"Update Comment: {response.status_code}, {response.json()}")


def delete_comment(token, comment_id):
    url = f"{API_URL}/comment/{comment_id}/"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(url, headers=headers)
    print(f"Delete Comment: {response.status_code}, {response.json()}")


def delete_user(token, password):
    url = f"{API_URL}/users/delete/"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {"password": password}
    response = requests.delete(url, json=data, headers=headers)
    print(f"Delete User: {response.status_code}, {response.json()}")


# Run all tests
if __name__ == "__main__":
    # Test variables
    username = "testuser"
    email = "testuser@example.com"
    password = "password123"

    # 1. Signup
    try:
        signup(username, email, password)
    except:
        pass

    # 2. Login
    token = login(username, password)
    if not token:
        print("Login failed. Exiting...")
        exit()

    # 3. Check current user
    check_current_user(token)

    # 4. CRUD Post
    post_id = create_post(token, "This is my first post.")
    read_all_posts(token)
    update_post(token, post_id, "This is my updated post caption.")
    delete_post(token, post_id)

    # 5. CRUD Comment
    post_id = create_post(token, "Another post for comment testing.")
    comment_id = create_comment(token, post_id, "This is a comment.")
    read_all_comments_for_post(token, post_id)
    update_comment(token, comment_id, "This is an updated comment.")
    delete_comment(token, comment_id)

    # 6. Logout
    logout(token)
    # 7. Delete User
    token = login(username, password)
    delete_user(token, password)
