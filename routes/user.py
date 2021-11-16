from fastapi import APIRouter, Response
from config.db import conn
from models.user import users
from schemas.user import User
from cryptography.fernet import Fernet
from starlette.status import HTTP_204_NO_CONTENT


key = Fernet.generate_key()
f_key = Fernet(key)
user = APIRouter()  


@user.get('/users')
def getUsers():
    return conn.execute(users.select()).fetchall()

@user.post('/users')
def createUser(user: User):
    new_user = {"name": user.name,"email": user.email}
    new_user["password"] = f_key.encrypt(user.password.encode('utf-8'))
    result = conn.execute(users.insert(new_user))
    return conn.execute(users.select().where(users.c.id == result.lastrowid)).first()


@user.get('/users/{id}')
def getUser(id: str):
    return conn.execute(users.select().where(users.c.id == id)).first()


@user.delete('/users/{id}')
def deleteUser(id: str):
    conn.execute(users.delete().where(users.c.id == id))
    return Response(status_code=HTTP_204_NO_CONTENT)


@user.put('/users/{id}')
def updateUser(id: str, user: User):
    conn.execute(users.update().values(name=user.name, 
    email=user.email, 
    password=f_key.encrypt(user.password.encode('utf-8'))).where(users.c.id==id))
    return conn.execute(users.select().where(users.c.id == id)).first()