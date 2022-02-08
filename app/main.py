from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlalchemy as db
import bcrypt, jwt, os
from dotenv import load_dotenv


class Credential(BaseModel):
    username: str
    password: str


# Connect to db
load_dotenv()
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
SECRET_KEY = "secret" # would need to generate a better one


# Create DB
engine = db.create_engine(f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@db:{POSTGRES_PORT}/{POSTGRES_DB}")
connection = engine.connect()
metadata = db.MetaData()
users = db.Table(
   "users", metadata, 
   db.Column("user", db.String, primary_key = True), 
   db.Column("hash", db.LargeBinary(60)),
   db.Column("salt", db.LargeBinary(60)))
metadata.create_all(engine)


app = FastAPI()


@app.get("/")
def status():
    return {"message": "OK"}


@app.post("/register")
def register(credentials: Credential):
    try:
        temp_salt = bcrypt.gensalt()
        temp_hash = bcrypt.hashpw(credentials.password.encode("utf8"), temp_salt)
        engine.execute(users.insert(), 
                       user = credentials.username, 
                       hash = temp_hash,
                       salt = temp_salt)
        raise HTTPException(200, "User created!")
    except db.exc.IntegrityError:
        raise HTTPException(409, "Username already exists!")
    

@app.get("/login")
def login(credentials: Credential):
    try:
        # Retrieve hashed password from db and compare to request body
        sql_stmt = db.select(users.c.hash).select_from(users).where(users.c.user == credentials.username)
        hashed = engine.execute(sql_stmt).first()[0]
        if bcrypt.checkpw(credentials.password.encode("utf8"), hashed):
            # Generate JWT token
            token = jwt.encode({"user": credentials.username, "exp": None}, SECRET_KEY, algorithm="HS256")
            return {
                "message": "Login successful",
                "token": token
            }
        else:
            raise HTTPException(401, "Incorrect username/password!")
    except TypeError:
        # Do not want to give indication which of the username or password is incorrect
        # Incorrect username
        raise HTTPException(401, "Incorrect username/password!")