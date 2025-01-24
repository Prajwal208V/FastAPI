from ..utils import hash
from fastapi import HTTPException, status, Depends, APIRouter
from sqlalchemy.orm import Session
from ..pydantic import Post, UserCreate, userOut
from ..import models #SQLALCHEMY
from ..database import get_db

router = APIRouter(
    prefix= '/users',
    tags=['Users']
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=userOut) 
def create_user(user:UserCreate, db: Session = Depends(get_db)):
    hasged_password = hash(user.password)
    user.password = hasged_password
    new_user = models.User(
        **user.dict()
        )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/{id}",response_model=userOut)
def get_user(id:int,db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail={ f"User with id: {id} dose not exist"}
        ) 
    return user