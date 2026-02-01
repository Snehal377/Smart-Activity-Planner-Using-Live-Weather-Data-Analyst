from flask import Flask, render_template, jsonify,request
import requests
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

app=Flask(__name__)

API_KEY = '1fb3adef2be18083bf8ab4be69ba4875'
BASE_URL = 'https://api.openweathermap.org/data/2.5/'

# weather 

def get_current_weather(city):
    url = f"{BASE_URL}weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()
    
    #handle invalid city 
    
    if data.get("cod") != 200:
        return None
    
    
    return {
        'description': data['weather'][0]['description'],
        'country': data['sys']['country'],
        'wind_gust_dir': data['wind'].get('deg', 0),
        'pressure': data['main']['pressure'],
        'Wind_Gust_Speed': data['wind'].get('speed', 0),
        'humidity': data['main']['humidity'],
        'current_temp': data['main']['temp'],
        'temp_min': data['main']['temp_min'],
        'temp_max': data['main']['temp_max'],
        'feels_like': data['main']['feels_like']
    }
    
    # data
    
def read_data():
    df = pd.read_csv("weather.csv")
    df = df.dropna().drop_duplicates()
    return df

def prepare_data(df):
    le = LabelEncoder()
    df['WindGustDir'] = le.fit_transform(df['WindGustDir'].astype(str))
    df['RainTomorrow'] = le.fit_transform(df['RainTomorrow'].astype(str))
    X = df.drop('RainTomorrow', axis=1)
    y = df['RainTomorrow']
    return X, y

def train_rain_model(X, y):
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model

def recommend_activity(temp, rain, humidity):
    if rain == 1:
        return "Indoor activities (Movies, Reading, Home Workout)"
    elif temp < 15:
        return "Warm indoor plans"
    elif 15 <= temp <= 25:
        return "Outdoor activities" if humidity < 70 else "Light outdoor walk"
    else:
        return "Light outdoor activity (Stay hydrated)"
    
    
    #router 
    
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/predict',methods=['POST'])
def predict():
    city= request.json['city']
    
    current_weather=get_current_weather(city)
    
    # check for invalid city 
    
    if current_weather is None:
        return jsonify({"error":"City not found. please enter a valid city name."}),400
    
    wind_deg = current_weather['wind_gust_dir'] % 360

   
    compass_points = [
    ("N", 0, 11.25), ("NNE", 11.25, 33.75), ("NE", 33.75, 56.25),
    ("ENE", 56.25, 78.75), ("E", 78.75, 101.25), ("ESE", 101.25, 123.75),
    ("SE", 123.75, 146.25), ("SSE", 146.25, 168.75), ("S", 168.75, 191.25),
    ("SSW", 191.25, 213.75), ("SW", 213.75, 236.25), ("WSW", 236.25, 258.75),
    ("W", 258.75, 281.25), ("WNW", 281.25, 303.75), ("NW", 303.75, 326.25),
    ("NNW", 326.25, 348.75)
    ]

    compass_direction = next(
    point for point, start, end in compass_points
    if start <= wind_deg < end
    )

    df=read_data()
    X,y=prepare_data(df)
    rain_model =train_rain_model(X,y)
    
    input_df=pd.DataFrame([{
        'MinTemp': current_weather['temp_min'],
        'MaxTemp': current_weather['temp_max'],
        'WindGustDir': 0,
        'WindGustSpeed': current_weather['Wind_Gust_Speed'],
        'Humidity': current_weather['humidity'],
        'Pressure': current_weather['pressure']
        
    }])
    for col in rain_model.feature_names_in_:
        if col not in input_df.columns:
            input_df[col] = 0  # default value for missing columns
    input_df = input_df[rain_model.feature_names_in_]
    
    rain_pred=int(rain_model.predict(input_df)[0])
    activity = recommend_activity(current_weather['current_temp'], rain_pred, current_weather['humidity'])

    
    return jsonify({
        'current_temp':current_weather['current_temp'],
        'humidity':current_weather['humidity'],
        'condition':current_weather['description'],
        'feels_like': current_weather['feels_like'],
        'wind_speed':current_weather['Wind_Gust_Speed'],
        'wind_direction':compass_direction,
        'rain':"Yes"if rain_pred else "No",
        'activity':activity
    })
    
    print(current_weather)
if __name__=="__main__":
        app.run(debug=True)

