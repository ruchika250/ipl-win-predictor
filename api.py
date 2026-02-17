from fastapi import FastAPI
import os
import joblib
import pandas as pd
from pydantic import BaseModel, field_validator

app = FastAPI(
    title="IPL Win Predictor API",
    description="API for predicting the probability of winning for IPL teams based on match conditions.",
)

@app.get("/")
def greet():
    return {"message": "Welcome to the IPL Win Predictor API!"}

# Load Model
MODEL_PATH = "pipe.pkl"

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("Model file 'pipe.pkl' not found!")

pipe = joblib.load(MODEL_PATH)

class MatchData(BaseModel):
    batting_team: str 
    bowling_team: str 
    city: str
    target: int 
    score: int
    wickets: int
    overs: float   # changed to float

    @field_validator('batting_team')
    def validate_batting_team(cls, value):
        teams = [
            "Chennai Super Kings",
            "Mumbai Indians",
            "Kolkata Knight Riders",
            "Royal Challengers Bengaluru",
            "Delhi Capitals",
            "Sunrisers Hyderabad",
            "Rajasthan Royals",
            "Punjab Kings",
            "Gujarat Titans",
            "Lucknow Super Giants"
        ]
        if value not in teams:
            raise ValueError(f"Invalid batting team. Must be one of: {teams}")
        return value

    @field_validator('bowling_team')
    def validate_bowling_team(cls, value):
        teams = [
            "Chennai Super Kings",
            "Mumbai Indians",
            "Kolkata Knight Riders",
            "Royal Challengers Bengaluru",
            "Delhi Capitals",
            "Sunrisers Hyderabad",
            "Rajasthan Royals",
            "Punjab Kings",
            "Gujarat Titans",
            "Lucknow Super Giants"
        ]
        if value not in teams:
            raise ValueError(f"Invalid bowling team. Must be one of: {teams}")
        return value

    @field_validator('city')
    def validate_city(cls, value):
        cities = [
            'Hyderabad', 'Bangalore', 'Mumbai', 'Indore', 'Kolkata', 'Delhi',
            'Chandigarh', 'Jaipur', 'Chennai', 'Cape Town', 'Port Elizabeth',
            'Durban', 'Centurion', 'East London', 'Johannesburg', 'Kimberley',
            'Bloemfontein', 'Ahmedabad', 'Cuttack', 'Nagpur', 'Dharamsala',
            'Visakhapatnam', 'Pune', 'Raipur', 'Ranchi', 'Abu Dhabi',
            'Sharjah', 'Mohali', 'Bengaluru'
        ]
        if value not in cities:
            raise ValueError(f"Invalid city. Must be one of: {cities}")
        return value

    @field_validator('target')
    def validate_target(cls, value):
        if value <= 0:
            raise ValueError("Target must be a positive integer.")
        return value

    @field_validator('score')
    def validate_score(cls, value):
        if value < 0:
            raise ValueError("Score cannot be negative.")
        return value

    @field_validator('wickets')    
    def validate_wickets(cls, value):
        if value < 0 or value > 10:
            raise ValueError("Wickets must be between 0 and 10.")
        return value

    @field_validator('overs')
    def validate_overs(cls, value): 
        if value < 0 or value > 20:
            raise ValueError("Overs must be between 0 and 20.")
        return value    

@app.post("/predict")
def predict_win_probability(match_data: MatchData):
    runs_left = match_data.target - match_data.score
    balls_bowled = int(match_data.overs * 6)
    balls_left = max(120 - balls_bowled, 0)
    wickets_left = 10 - match_data.wickets

    crr = match_data.score / match_data.overs if match_data.overs > 0 else 0
    rrr = (runs_left * 6) / balls_left if balls_left > 0 else 0

    input_df = pd.DataFrame({
        'batting_team': [match_data.batting_team],
        'bowling_team': [match_data.bowling_team],
        'city': [match_data.city],
        'runs_left': [runs_left],
        'balls_left': [balls_left],
        'wickets': [wickets_left],
        'total_runs_x': [match_data.target],
        'crr': [crr],
        'rrr': [rrr]
    })

    result = pipe.predict_proba(input_df)
    loss = float(result[0][0])
    win = float(result[0][1])

    return {
        "batting_team": match_data.batting_team,
        "bowling_team": match_data.bowling_team,
        "win_probability": round(win * 100, 2),
        "loss_probability": round(loss * 100, 2)
    }
