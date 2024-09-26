import streamlit as st
import requests
import openai
import asyncio
import httpx

# Set up Streamlit secrets for API keys
OPENWEATHER_API_KEY = st.secrets["open-weather"]
OPENAI_API_KEY = st.secrets["openai_key"]
CLAUDE_API_KEY = st.secrets["claude-key"]

# Set up Streamlit UI
st.title("Weather Chatbot")

# Sidebar for LLM selection
st.sidebar.header("Settings")
llm_vendor = st.sidebar.selectbox("Select LLM Vendor", ("OpenAI", "Claude"))

# Input for city
location = st.text_input("Enter a city to get the weather:", "Syracuse, NY")

# Function to retrieve weather data
def get_current_weather(location, API_key):
    if "," in location:
        location = location.split(",")[0].strip()
    url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={API_key}"
    response = requests.get(url)
    data = response.json()

    # Extract temperatures and convert Kelvin to Celsius
    temp = data['main']['temp'] - 273.15
    feels_like = data['main']['feels_like'] - 273.15
    temp_min = data['main']['temp_min'] - 273.15
    temp_max = data['main']['temp_max'] - 273.15
    humidity = data['main']['humidity']
    description = data['weather'][0]['description']

    return {
        "location": location,
        "temperature": round(temp, 2),
        "feels_like": round(feels_like, 2),
        "temp_min": round(temp_min, 2),
        "temp_max": round(temp_max, 2),
        "humidity": humidity,
        "description": description
    }

# Function to generate clothing suggestions and picnic advice using LLM
async def generate_clothing_and_picnic_advice(weather_info, llm_vendor):
    prompt = (f"The current weather in {weather_info['location']} is {weather_info['description']} with a temperature of "
              f"{weather_info['temperature']}°C, feels like {weather_info['feels_like']}°C, humidity is {weather_info['humidity']}%. "
              "What should someone wear today and is it a good day for a picnic?")

    if llm_vendor == "OpenAI":
        openai.api_key = OPENAI_API_KEY
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Specify the model
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100
        )
        return response['choices'][0]['message']['content'].strip()

    elif llm_vendor == "Claude":
        async with httpx.AsyncClient() as client:
            anthropic_client = anthropic.Anthropic(api_key=CLAUDE_API_KEY, http_client=client)
            response = await anthropic_client.completions.create(
                prompt=f"\n\n{anthropic.HUMAN_PROMPT}{prompt}\n\n{anthropic.AI_PROMPT}",
                model="claude-3",
                max_tokens=100
            )
            return response.completion.strip()

# Main function for processing the weather data
async def process_weather_request(location, llm_vendor):
    weather_info = get_current_weather(location, OPENWEATHER_API_KEY)
    clothing_suggestions = await generate_clothing_and_picnic_advice(weather_info, llm_vendor)
    return weather_info, clothing_suggestions

# Button for retrieving weather and suggestions
if st.button("Get Weather and Advice"):
    weather_info, advice = asyncio.run(process_weather_request(location, llm_vendor))

    # Display the weather information and suggestions
    st.write(f"**Weather in {weather_info['location']}:**")
    st.write(f"Temperature: {weather_info['temperature']}°C (Feels like {weather_info['feels_like']}°C)")
    st.write(f"Min Temp: {weather_info['temp_min']}°C, Max Temp: {weather_info['temp_max']}°C")
    st.write(f"Humidity: {weather_info['humidity']}%")
    st.write(f"Description: {weather_info['description']}")
    st.write("**Clothing Suggestions and Picnic Advice:**")
    st.write(advice)
