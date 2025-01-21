from ..pydantic import PostCreate
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from fastapi import HTTPException, status, Response, APIRouter

router = APIRouter()

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
@router.get("/")  # Path operation decorator for root URL
def root():
    return {"message": "Hello API!!!!!!!!"}

# Endpoint to retrieve all posts from the database
@router.get("/posts")  # GET request to fetch all posts
def get_post():
    cursor.execute("""SELECT * FROM posts2""")  # Execute SQL query
    posts = cursor.fetchall()  # Fetch all results from query
    if not posts:  # Check if no posts exist
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail={"message": "No posts found"}
        ) 
    print(posts)  # Print posts for debugging
    return posts

# Endpoint to create a new post in the database
@router.post("/posts", status_code=status.HTTP_201_CREATED)  # POST request to add a new post
def create_posts(post: PostCreate):
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
    return new_post

# Endpoint to fetch the latest post based on the created_at timestamp
@router.get("/posts/latest")  # GET request to get the latest post
def get_lastest_post():
    cursor.execute("SELECT * FROM posts2 ORDER BY created_at DESC LIMIT 1")
    last_row = cursor.fetchone()  # Fetch the latest row
    if last_row is None:  # Check if no record exists
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="No records found in the 'posts' table.")
    return last_row

# Endpoint to fetch a post by its ID
@router.get("/posts/{id}")  # GET request to get a specific post by ID
def get_post_by_id(id: int, response: Response):
    cursor.execute("""SELECT * FROM posts2 WHERE id = %s """, (str(id),))
    post = cursor.fetchone()  # Fetch the requested post
    if not post:  # Check if post doesn't exist
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail={"message": f"Post with id: {id} was not found"}
        ) 
    return post

# Endpoint to delete a post by its ID
@router.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)  # DELETE request to remove a post
def delete_post(id: int):
    cursor.execute("""DELETE FROM posts2 WHERE id = %s RETURNING *""", (str(id),))
    deleted_post = cursor.fetchone()  # Fetch the deleted post
    connection.commit()  # Commit the deletion to the database
    if deleted_post is None:  # Check if no post was deleted
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail={"message": f"Post with id: {id} was not found"}
        ) 
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Endpoint to update an existing post by its ID
@router.put("/posts/{id}")  # PUT request to update a post
def update_post(id: int, post: PostCreate):
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
    return updated_post