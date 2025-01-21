from sqlalchemy.orm import Session
from fastapi import HTTPException, Response, status, Depends,APIRouter
from typing import List
from ..database import get_db
from .. import models #SQLALCHEMY
from ..pydantic import PostCreate, Post


router = APIRouter()

# sqlalchemy end points
@router.get('/sqlalchemy/posts',response_model=List[Post])
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts

@router.post("/sqlalchemy/posts", status_code=status.HTTP_201_CREATED,response_model=Post) 
def create_posts(post:PostCreate, db: Session = Depends(get_db)):
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
    return new_post

@router.get("/sqlalchemy/posts/{id}",response_model=Post)  # GET request to get a specific post by ID
def get_post_by_id(id: int,db: Session = Depends(get_db)):
   post = db.query(models.Post).filter(models.Post.id == id).first() # filter works as WHERE in query
   if not post:  # Check if post doesn't exist
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail={"message": f"Post with id: {id} was not found"}
        ) 
   return post

@router.delete("/sqlalchemy/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)  # DELETE request to remove a post
def delete_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() == None:  # Check if no post was deleted
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail={"message": f"Post with id: {id} was not found"}
        ) 
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/sqlalchemy/posts/{id}",response_model=Post)  # PUT request to update a post
def update_post(id: int, uodated_post: PostCreate, db: Session = Depends(get_db)):
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
    return post_query.first()
