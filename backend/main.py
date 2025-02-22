from fastapi import FastAPI, Depends,HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import psycopg2
import os
import requests
from dotenv import load_dotenv
import logging

# Configure logging with more details and proper format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

# Load environment variables from .env
load_dotenv()

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

# Connect to Supabase PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    logger.info("✅ Database connection successful!")
except Exception as e:
    logger.error(f"❌ Failed to connect: {e}")
    # Add this line to see detailed error
    raise e

app = FastAPI()
auth_scheme = HTTPBearer()  # Middleware to handle authentication tokens

# Models
class Workout(BaseModel):
    name: str
    duration: int # in minutes

# Function to verify JWT token from Supabase
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    token = credentials.credentials
    headers = {"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
    response = requests.get(f"{SUPABASE_URL}/auth/v1/user", headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return response.json() # Returns user info

@app.post("/workouts")
def create_workout(workout: Workout):
    try:
        cursor.execute("INSERT INTO workouts (name, duration) VALUES (%s, %s) RETURNING id", (workout.name, workout.duration))
        workout_id = cursor.fetchone()[0]
        conn.commit()
        logger.info(f"Created workout with ID: {workout_id}")
        return {"message": "Workout added successfully", "id": workout_id}
    except Exception as e:
        logger.error(f"Error creating workout: {e}")
        return {"error": str(e)}

@app.get("/workouts")
def get_workouts():
    cursor.execute("SELECT * FROM workouts")
    workouts = cursor.fetchall()
    return {"workouts": [{"id": w[0], "name": w[1], "duration": w[2]} for w in workouts]}

@app.get("/")
def read_root():
    return {"message": "Welcome to the fitness tracker API"}

