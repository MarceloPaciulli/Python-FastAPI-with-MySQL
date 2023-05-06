from sqlalchemy import Table, Column, Integer, String, Sequence, ForeignKey, DateTime
from datetime import datetime
from config.db import meta, engine

users = Table("users", meta,
    Column('id', Integer, Sequence('user_id_seq'), primary_key=True),
    Column('email', String(255)),
    Column('password', String(255))
)

chats = Table("chats", meta,
    Column('id', Integer, Sequence('chat_id_seq'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('chat_name', String(255)),
    Column('chat_description', String(255)),
    Column('language', String(255), default="en")
)

messages = Table("messages", meta,
    Column('id', Integer, Sequence('message_id_seq'), primary_key=True),
    Column('chat_id', Integer, ForeignKey('chats.id')),
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('message_content', String(255)),
    Column('timestamp', DateTime, default=datetime.now())
)


meta.create_all(engine)
