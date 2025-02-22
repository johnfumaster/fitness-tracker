from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup
    conn = get_db_connection()
    conn.execute("CREATE TABLE IF NOT EXISTS workouts (id INTEGER PRIMARY KEY, name TEXT, duration INTEGER)")
    conn.close()
    yield

app = FastAPI(lifespan=lifespan)

# Database Setup
def get_db_connection():
    conn = sqlite3.connect('workouts.db')
    conn.row_factory = sqlite3.Row
    return conn

# Models
class Workout(BaseModel):
    name: str
    duration: int # in minutes

@app.post('/workouts')
def create_workout(workout: Workout):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO workouts (name, duration) VALUES (?,?)", (workout.name, workout.duration))
    conn.commit()
    conn.close()
    return {"message": "Workout added successfully"}

@app.get("/workouts")
def get_workouts():
    conn = get_db_connection()
    workouts = conn.execute("SELECT * FROM workouts").fetchall()
    conn.close()
    return {"workouts": [dict(workout) for workout in workouts]}

@app.get("/")
def read_root():
    return {"message": "Welcome to the fitness tracker API"}

