from .. import models, schemas, oauth2
from typing import List, Optional
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from sqlalchemy import func

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

@router.get("/", response_model=List[schemas.PostOut])
async def get_post(db : Session = Depends(get_db), current_user : int = Depends(oauth2.get_current_user), limit : int = 10, skip : int = 0, search : Optional[str] = ""):

    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()

    posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    results = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id)

    # If you want to get the user specific id when you logged 
    # posts = db.query(models.Post).filter(models.Post.owner_id == current_user.id).all()

    return results

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
async def create_posts(post : schemas.PostCreate, db : Session = Depends(get_db), current_user : int = Depends(oauth2.get_current_user)):


    # cursor.execute(""" INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()

    # new_post = models.Post(title=post.title, content=post.content, published=post.published)

    new_post = models.Post(owner_id = current_user.id, **post.dict())
    db.add(new_post)
    db.commit() 
    db.refresh(new_post)

    return new_post

# @app.post("/posts", status_code=status.HTTP_201_CREATED)
# async def create_posts(post : Post):
#     print(post)
#     post_dict = post.dict()
#     post_dict["id"] = randrange(0,1000000)
#     my_posts.append(post_dict)
#     return {"data" : post_dict}

# @app.post("/createposts")
# async def create_posts(payload: dict = Body(...)):
#     print(payload)
#     return {"new_post" : f"title {payload["title"]}, Content : {payload["content"]}"}

@router.get("/{id}", response_model=schemas.PostOut)
async def get_post(id : int, res : Response, db : Session = Depends(get_db),current_user : int = Depends(oauth2.get_current_user)):

    # cursor.execute(""" SELECT * FROM posts WHERE id = %s """, (str(id)))
    # post = cursor.fetchone()

    # post = db.query(models.Post).filter(models.Post.id == id).first()

    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()


    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This id does not exist.")
        # res.status_code = status.HTTP_404_NOT_FOUND
    return post

# @app.get("/posts/{id}")
# async def get_post(id : int, res : Response):
#     post = find_post(id)
#     if not post:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This id does not exist.")
#         # res.status_code = status.HTTP_404_NOT_FOUND
#     return {"post_detail" : post}


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id:int, db : Session = Depends(get_db),current_user : int = Depends(oauth2.get_current_user)):

    # cursor.execute(""" DELETE FROM posts WHERE id = %s RETURNING * """, (str(id)))
    # deleted_post = cursor.fetchone
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This id does not exist.")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action.")
    
    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

# @app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_post(id:int):
#     index = find_index_post(id)

#     if index == None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This id does not exist.")

#     my_posts.pop(index)
#     # return {"message" : "Post was deleted"}
#     return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.Post)
async def update_post(id:int, post : schemas.PostCreate, db : Session = Depends(get_db),current_user : int = Depends(oauth2.get_current_user)):

    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """ , (post.title, post.content, post.published, str(id)))
    # updated_post = cursor.fetchone()
    # conn.commit()

    updated_post = db.query(models.Post).filter(models.Post.id == id)

    if updated_post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This id does not exist.")

    if updated_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action.")

    updated_post.update(post.dict(), synchronize_session=False)
    db.commit()

    return updated_post.first()

# @app.put("/posts/{id}")
# async def update_post(id:int, post : Post):
#     index = find_index_post(id)

#     if index == None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This id does not exist.")

#     post_dict = post.dict()
#     post_dict["id"] = id
#     my_posts[index] = post_dict
#     return {"data" : post_dict}



