import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException, Response, status, Depends
from pydantic import BaseModel
import time

from . import models #SQLALCHEMY
from sqlalchemy.orm import Session
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)#SQLALCHEMY, it will create table within postgres


# Initialize the FastAPI application
app = FastAPI() 
# Define a Pydantic model for input validation and data handling
class Post(BaseModel):
    title: str  # Title of the post (string)
    content: str  # Content of the post (string)
    published: bool = True  # Optional field with default value as True

# sqlalchemy end points
@app.get('/sqlalchemy/posts')
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    print(posts)
    return {"data": posts}

@app.post("/sqlalchemy/posts", status_code=status.HTTP_201_CREATED) 
def create_posts(post:Post, db: Session = Depends(get_db)):
    # new_post= models.Post(
    #     title=post.title,
    #     content=post.content,
    #     published=post.published
    #     )
    new_post = models.Post(
        **post.dict() # ** for unpacking and it is replacing above commited code
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post) # retrive that new post that we just created and store back into variable
    return {"data":new_post}

@app.get("/sqlalchemy/posts/{id}")  # GET request to get a specific post by ID
def get_post_by_id(id: int,db: Session = Depends(get_db)):
   post = db.query(models.Post).filter(models.Post.id == id).first() # filter works as WHERE in query
   if not post:  # Check if post doesn't exist
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail={"message": f"Post with id: {id} was not found"}
        ) 
   return {"post_detail": post}

@app.delete("/sqlalchemy/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)  # DELETE request to remove a post
def delete_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() == None:  # Check if no post was deleted
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail={"message": f"Post with id: {id} was not found"}
        ) 
    post.delete(synchronize_session=False)
    db.commit()
    return {"message": "Post has been removed"}


@app.put("/sqlalchemy/posts/{id}")  # PUT request to update a post
def update_post(id: int, uodated_post: Post, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post == None:  # Check if the post wasn't found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail={"message": f"Post with id: {id} was not found"}
        ) 
    post_query.update(
        uodated_post.dict(),
        synchronize_session=False
    )
    db.commit()
    print(post_query.first())
    return {"data": post_query.first()}


# Attempt to connect to the PostgreSQL database with retries
while True:
    try:
        # Establishing the database connection
        connection = psycopg2.connect(
            host='localhost',  # Database host
            database='fastapi',  # Database name
            user='postgres',  # Database user
            password='200123',  # Database password
            cursor_factory=RealDictCursor  # Returns query results as dictionaries
        )
        cursor = connection.cursor()
        print("Database connection was successful!")
        break  # Exit the loop on successful connection
    except Exception as error:
        print("Connecting to database failed")
        print("Error:", error)
        time.sleep(2)  # Retry after 2 seconds if connection fails

# Root endpoint to test API status
@app.get("/")  # Path operation decorator for root URL
def root():
    return {"message": "Hello API!!!!!!!!"}

# Endpoint to retrieve all posts from the database
@app.get("/posts")  # GET request to fetch all posts
def get_post():
    cursor.execute("""SELECT * FROM posts2""")  # Execute SQL query
    posts = cursor.fetchall()  # Fetch all results from query
    if not posts:  # Check if no posts exist
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail={"message": "No posts found"}
        ) 
    print(posts)  # Print posts for debugging
    return {"posts": posts}

# Endpoint to create a new post in the database
@app.post("/posts", status_code=status.HTTP_201_CREATED)  # POST request to add a new post
def create_posts(post: Post):
    cursor.execute(
        """INSERT INTO posts2 (title, content, published) VALUES (%s, %s, %s) RETURNING *""", 
        (post.title, post.content, post.published)
    )
    new_post = cursor.fetchone()  # Get the newly created post
    connection.commit()  # Commit the transaction to the database
    if not new_post:  # Check if insertion failed
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT, 
            detail={"message": "Data not added"}
        ) 
    print(new_post)  # Print new post for debugging
    return {"new_post_detail": new_post}

# Endpoint to fetch the latest post based on the created_at timestamp
@app.get("/posts/latest")  # GET request to get the latest post
def get_lastest_post():
    cursor.execute("SELECT * FROM posts2 ORDER BY created_at DESC LIMIT 1")
    last_row = cursor.fetchone()  # Fetch the latest row
    if last_row is None:  # Check if no record exists
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="No records found in the 'posts' table.")
    return last_row

# Endpoint to fetch a post by its ID
@app.get("/posts/{id}")  # GET request to get a specific post by ID
def get_post_by_id(id: int, response: Response):
    cursor.execute("""SELECT * FROM posts2 WHERE id = %s """, (str(id),))
    post = cursor.fetchone()  # Fetch the requested post
    if not post:  # Check if post doesn't exist
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail={"message": f"Post with id: {id} was not found"}
        ) 
    return {"post_detail": post}

# Endpoint to delete a post by its ID
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)  # DELETE request to remove a post
def delete_post(id: int):
    cursor.execute("""DELETE FROM posts2 WHERE id = %s RETURNING *""", (str(id),))
    deleted_post = cursor.fetchone()  # Fetch the deleted post
    connection.commit()  # Commit the deletion to the database
    if deleted_post is None:  # Check if no post was deleted
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail={"message": f"Post with id: {id} was not found"}
        ) 
    return {"message": "Post has been removed"}

# Endpoint to update an existing post by its ID
@app.put("/posts/{id}")  # PUT request to update a post
def update_post(id: int, post: Post):
    cursor.execute(
        """UPDATE posts2 SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
        (post.title, post.content, post.published, str(id))
    )
    updated_post = cursor.fetchone()  # Fetch the updated post
    connection.commit()  # Commit the update to the database
    if updated_post is None:  # Check if the post wasn't found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail={"message": f"Post with id: {id} was not found"}
        ) 
    return {"data": updated_post}
