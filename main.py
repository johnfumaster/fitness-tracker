from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Connect to Supabase PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    print("✅ Database connection successful!")
except Exception as e:
    print(f"❌ Failed to connect: {e}")

app = FastAPI()

# Models
class Workout(BaseModel):
    name: str
    duration: int # in minutes

@app.post("/workouts")
def create_workout(workout: Workout):
    try:
        cursor.execute("INSERT INTO workouts (name, duration) VALUES (%s, %s) RETURNING id", (workout.name, workout.duration))
        workout_id = cursor.fetchone()[0]
        conn.commit()
        return {"message": "Workout added successfully", "id": workout_id}
    except Exception as e:
        return {"error": str(e)}

@app.get("/workouts")
def get_workouts():
    cursor.execute("SELECT * FROM workouts")
    workouts = cursor.fetchall()
    return {"workouts": [{"id": w[0], "name": w[1], "duration": w[2]} for w in workouts]}

@app.get("/")
def read_root():
    return {"message": "Welcome to the fitness tracker API"}

