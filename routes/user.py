from fastapi import APIRouter, Response, HTTPException, Depends
from config.db import conn
from models.user import users, chats, messages
from schemas.user import User, Chat, Message
from cryptography.fernet import Fernet
from starlette.status import HTTP_204_NO_CONTENT
from .auth_jwt import generate_token, verify_token
from cryptography.fernet import Fernet
from datetime import datetime
import os

# Si el archivo de la clave no existe, se genera una nueva y se guarda en el archivo
if not os.path.exists('key.key'):
    key = Fernet.generate_key()
    with open('key.key', 'wb') as key_file:
        key_file.write(key)
else:
    # Si el archivo de la clave existe, se lee la clave desde el archivo
    with open('key.key', 'rb') as key_file:
        key = key_file.read()

f_key = Fernet(key)

user = APIRouter()  



@user.get('/users')
def getUsers():
    return conn.execute(users.select()).fetchall()



@user.post('/register')
def createUser(user: User):
    existing_user = conn.execute(users.select().where(users.c.email == user.email)).fetchone()
    if existing_user:
        raise HTTPException(status_code=409, detail="User already registered")

    new_user = {"email": user.email}
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



@user.post('/users/{user_id}/chats')
def createChat(user_id: str, chat: Chat, user_id_token = Depends(verify_token)):
    # comparamos el user_id del token con el user_id del endpoint
    
    if user_id_token != int(user_id):
       raise HTTPException(status_code=401, detail="Unauthorized user")

    # Primero, verificamos que el usuario exista
    if not conn.execute(users.select().where(users.c.id == user_id)).first():
        raise HTTPException(status_code=404, detail="User not found")

    # Luego, insertamos el nuevo registro en la tabla chats
    new_chat = {
        "user_id": user_id,
        "chat_name": chat.chat_name,
        "chat_description": chat.chat_description,
        "language": chat.language
    }

    result = conn.execute(chats.insert(new_chat))
    return conn.execute(chats.select().where(chats.c.id == result.lastrowid)).first()



@user.post('/users/{user_id}/chats/{chat_id}/messages')
def createMessage(user_id: str, chat_id: str, message: Message, user_id_token = Depends(verify_token)):
    # comparamos el user_id del token con el user_id del endpoint
    if user_id_token != int(user_id):
        raise HTTPException(status_code=401, detail="Unauthorized user")

    # Verificamos que el chat exista y pertenezca al usuario
    chat = conn.execute(chats.select().where(chats.c.id == chat_id, chats.c.user_id == user_id)).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Insertamos el nuevo registro en la tabla messages
    new_message = {
        "chat_id": chat_id,
        "user_id": user_id,
        "message_content": message.message_content,
        "timestamp": datetime.now()
    }

    result = conn.execute(messages.insert(new_message))
    return conn.execute(messages.select().where(messages.c.id == result.lastrowid)).first()



@user.get('/users/{user_id}/chats/{chat_id}/messages')
def getMessagesByChatId(user_id: str, chat_id: str):
    # Primero, verificamos que el usuario exista
    if not conn.execute(users.select().where(users.c.id == user_id)).first():
        raise HTTPException(status_code=404, detail="User not found")

    # Luego, verificamos que el chat pertenece al usuario
    if not conn.execute(chats.select().where((chats.c.id == chat_id) & (chats.c.user_id == user_id))).first():
        raise HTTPException(status_code=404, detail="Chat not found")

    # Obtenemos todos los mensajes pertenecientes a ese chat
    messages_query = messages.select().where(messages.c.chat_id == chat_id)
    messages_result = conn.execute(messages_query).fetchall()
    return messages_result



@user.delete('/users/{user_id}/chats/{id}')
def deleteChat(user_id: str, id: int, user_id_token=Depends(verify_token)):
    # Comparamos el user_id del token con el user_id del endpoint
    if user_id_token != int(user_id):
        raise HTTPException(status_code=401, detail="Unauthorized user")

    # Verificamos que el usuario exista
    if not conn.execute(users.select().where(users.c.id == user_id)).first():
        raise HTTPException(status_code=404, detail="User not found")

    # Verificamos que el chat exista y pertenezca al usuario
    chat = conn.execute(chats.select().where(chats.c.id == id)).first()
    if not chat or chat['user_id'] != int(user_id):
        raise HTTPException(status_code=404, detail="Chat not found")

    # Borramos el chat de la base de datos
    conn.execute(chats.delete().where((chats.c.id == id) & (chats.c.user_id == user_id)))
    return {"message": f"Chat {id} has been deleted"}



@user.get('/users/{user_id}/chats')
def getChatsByUserId(user_id: str):
    # Primero, verificamos que el usuario exista
    if not conn.execute(users.select().where(users.c.id == user_id)).first():
        raise HTTPException(status_code=404, detail="User not found")

    # Luego, obtenemos los chats asociados a ese usuario
    chats_query = chats.select().where(chats.c.user_id == user_id)
    chats_result = conn.execute(chats_query).fetchall()
    return chats_result



@user.post('/login')
def login(user: User):
    # Busca al usuario por correo electrónico
    user_query = users.select().where(users.c.email == user.email)
    result = conn.execute(user_query)
    row = result.fetchone()
    if row is None:
        # El usuario no existe
        raise HTTPException(status_code=401, detail="Correo electrónico o contraseña incorrectos")
    
    # Verifica la contraseña
    stored_password = f_key.decrypt(row['password'].encode()).decode('utf-8')
    if user.password != stored_password:
        # Contraseña incorrecta
        raise HTTPException(status_code=401, detail="Correo electrónico o contraseña incorrectos")

    # Genera el token JWT
    token = generate_token(row['id'])
    #print(token)

    # Devuelve el token
    return {"token": token}



@user.get('/auth_id')
def get_user(user_id: int = Depends(verify_token)):
    print(f"User ID: {user_id}")
    return {"user_id": user_id}



@user.get('/protected')
def protected(token: str = Depends(verify_token)):
    if token is None:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    else:
        return {"message": "Recurso protegido"}