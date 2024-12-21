from fastapi import FastAPI, Depends, Response, HTTPException, status
from fastapi import HTTPException, Depends, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import List, Optional
import os
import shutil

import database
from database import engine, get_db
from models import Base, User, Post, Comment
from pydantic_models import (
    UserBase,
    UserCreate,
    UserLogin,
    TokenResponse,
    UserResponse,
    PostUpdate,
    PostResponse,
    CommentCreate,
    CommentUpdate,
    CommentResponse,
    UserDeleteRequest
)


# JWT Secret and Algorithm Config
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
UPLOAD_DIR = "static/uploads"
UPLOAD_DIR_ROOT = os.environ.get("UPLOAD_DIR_ROOT", "./")

PUBLIC_IP = os.environ.get("PUBLIC_IP", "http://35.184.43.116/")
Base.metadata.create_all(bind=engine)
app = FastAPI()
api_router = APIRouter()
if UPLOAD_DIR_ROOT == "./":
    app.mount("/static", StaticFiles(directory="static"), name="static")



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")
origins = ["http://localhost:8000", "http://localhost:5173", "http://localhost:8080", PUBLIC_IP]
# origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow only the frontend to communicate with backend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Helper Functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user


# 1. User Signup
@api_router.post("/signup/", response_model=UserResponse)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter((User.username == user.username) | (User.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or Email already exists")

    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# 2. User Login
@api_router.post("/login/", response_model=TokenResponse)
async def login(user_login: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_login.username).first()
    if not user or not verify_password(user_login.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@api_router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(response: Response):
    response.delete_cookie("access_token")  # Optional if using cookies for storing JWT
    return {"msg": "Logged out successfully"}


@api_router.get("/check-auth")
def check_auth(token: str = Depends(oauth2_scheme)):
    """
    This route is protected, and checks if the token provided is valid.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"username": username}  # If valid, return the authenticated username


@api_router.delete("/users/delete/", response_model=dict)
async def delete_user(
    user_delete_request: UserDeleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify password
    if not verify_password(user_delete_request.password, current_user.password):
        raise HTTPException(status_code=400, detail="Incorrect password")

    # Delete the user
    db.delete(current_user)
    db.commit()
    return {"message": "User deleted successfully"}


# 4. Create a Post
@api_router.post("/post/", response_model=PostResponse)
async def create_post(
    caption: str = Form(...),  # Use Form to handle form data
    file: Optional[UploadFile] = File(None),  # Handle file uploads
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    image_path = None
    if file:
        image_path = os.path.join(UPLOAD_DIR, file.filename)
        file_location = os.path.join(UPLOAD_DIR_ROOT, image_path)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)


    db_post = Post(caption=caption, image_path=image_path, user_id=current_user.id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    # return db_post
    return PostResponse(
        id=db_post.id,
        image_path=db_post.image_path,
        caption=db_post.caption,
        user_id=db_post.user_id,
        created_at=db_post.created_at,
        updated_at=db_post.updated_at,
        author=UserBase(id=current_user.id, username=current_user.username),  # Include author info
        comments=[],
    )


# 5. Update a Post


@api_router.put("/post/{post_id}/", response_model=PostResponse)
async def update_post(
    post_id: int, post_data: PostUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    post = db.query(Post).filter(Post.id == post_id, Post.user_id == current_user.id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Update the post's caption
    post.caption = post_data.caption
    # SQLAlchemy will automatically update the 'updated_at' field
    db.commit()
    db.refresh(post)
    return post


# 6. Delete a Post
@api_router.delete("/post/{post_id}/", response_model=dict)
async def delete_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_post = db.query(Post).filter(Post.id == post_id, Post.user_id == current_user.id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(db_post)
    db.commit()
    return {"message": "Post deleted successfully"}


# 7. Create a Comment on a Post
@api_router.post("/comment/", response_model=CommentResponse)
async def create_comment(
    comment: CommentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    db_comment = Comment(content=comment.content, post_id=comment.post_id, user_id=current_user.id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


# 8. Update a Comment
@api_router.put("/comment/{comment_id}/", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = db.query(Comment).filter(Comment.id == comment_id, Comment.user_id == current_user.id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    # Update the comment's content
    comment.content = comment_data.content
    # SQLAlchemy will automatically update the 'updated_at' field
    db.commit()
    db.refresh(comment)
    return comment


# 9. Delete a Comment
@api_router.delete("/comment/{comment_id}/", response_model=dict)
async def delete_comment(
    comment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    db_comment = db.query(Comment).filter(Comment.id == comment_id, Comment.user_id == current_user.id).first()
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    db.delete(db_comment)
    db.commit()
    return {"message": "Comment deleted successfully"}


# 10. Read All Posts (with Comments)
@api_router.get("/post/", response_model=List[PostResponse])
async def read_all_posts(db: Session = Depends(get_db)):
    posts = db.query(Post).all()
    # return posts
    db_posts = []
    for db_post in posts:
        db_post_comments = []
        for comment in db_post.comments:
            comment_user = db.query(User).filter(User.id == comment.user_id).first()
            db_post_comments += [
                CommentResponse(
                    id=comment.id,
                    content=comment.content,
                    user_id=comment.user_id,
                    created_at=comment.created_at,
                    updated_at=comment.updated_at,
                    author=UserBase(id=comment_user.id, username=comment_user.username),  # Include author info
                )
            ]
        current_user = db.query(User).filter(User.id == db_post.user_id).first()
        db_posts += [
            PostResponse(
                id=db_post.id,
                caption=db_post.caption,
                image_path=db_post.image_path,
                user_id=db_post.user_id,
                created_at=db_post.created_at,
                updated_at=db_post.updated_at,
                author=UserBase(id=current_user.id, username=current_user.username),  # Include author info
                comments=db_post_comments,
            )
        ]
    return db_posts


# 11. Read All Comments for a Post
@api_router.get("/post/{post_id}/comments/", response_model=List[CommentResponse])
async def read_all_comments(post_id: int, db: Session = Depends(get_db)):
    comments = db.query(Comment).filter(Comment.post_id == post_id).all()
    # return comments
    db_comments = []
    for comment in comments:
        comment_user = db.query(User).filter(User.id == comment.user_id).first()
        db_comments += [
            CommentResponse(
                id=comment.id,
                content=comment.content,
                user_id=comment.user_id,
                created_at=comment.created_at,
                updated_at=comment.updated_at,
                author=UserBase(id=comment_user.id, username=comment_user.username),  # Include author info
            )
        ]
    return db_comments


app.include_router(api_router, prefix="/api")
