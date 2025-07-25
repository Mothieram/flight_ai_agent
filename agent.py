import pandas as pd
from typing import List, Dict, Optional
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize Gemini with API key from .env
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("No API key found. Please set GEMINI_API_KEY in your .env file")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash')

# Load flight data
df = pd.read_csv('exported_data/flight_data.csv')

class FlightDataAgent:
    """Base class for flight data analysis agents"""
    
    def __init__(self, name: str, specialty: str):
        self.name = name
        self.specialty = specialty
        self.context = f"""
        You are {name}, a specialized AI agent for {specialty}.
        You have access to flight data with columns: {', '.join(df.columns)}.
        Current dataset has {len(df)} flights scheduled for 2025-07-21.
        """
    
    def analyze(self, query: str) -> str:
        """Analyze the query using the agent's specialty"""
        prompt = f"""
        {self.context}
        User question: {query}
        
        Please provide a concise, accurate response based on your specialty.
        If you need specific data, here's a relevant sample:
        {df.sample(3).to_dict('records')}
        """
        
        response = model.generate_content(prompt)
        return response.text

class RoutingAgent:
    """Coordinates between specialized agents"""
    
    def __init__(self, agents: List[FlightDataAgent]):
        self.agents = {agent.specialty: agent for agent in agents}
        
    def route_query(self, query: str) -> str:
        """Determine which agent should handle the query"""
        routing_prompt = f"""
        Classify this flight data question into one of these categories:
        - airlines: Questions about specific airlines or airline operations
        - routes: Questions about flight routes or airports
        - stats: Statistical questions about flight data
        - general: Other questions about the flight dataset
        
        Question: {query}
        
        Respond ONLY with the category name.
        """
        
        category = model.generate_content(routing_prompt).text.lower()
        return self.agents.get(category, self.agents['general']).analyze(query)

def generate_readme(questions: List[str], filename: str = "query.md"):
    """Generate a query.md file with questions and answers"""
    # Create specialized agents
    agents = [
        FlightDataAgent("Airline Analyst", "airlines"),
        FlightDataAgent("Route Expert", "routes"),
        FlightDataAgent("Data Statistician", "stats"),
        FlightDataAgent("General Flight Assistant", "general")
    ]
    
    # Create the router
    router = RoutingAgent(agents)
    
    def query_flight_data(question: str) -> str:
        """Main interface for querying flight data"""
        try:
            return router.route_query(question)
        except Exception as e:
            return f"Error processing your query: {str(e)}"
    
    with open(filename, 'w') as f:
        f.write("# Flight Data Analysis Report\n\n")
        f.write("## Agentic AI Analysis of Flight Data\n\n")
        f.write("This report contains answers to common questions about the flight dataset.\n\n")
        
        for i, q in enumerate(questions, 1):
            answer = query_flight_data(q)
            f.write(f"### Question {i}: {q}\n\n")
            f.write(f"**Answer**: {answer}\n\n")
            f.write("---\n\n")
        
        f.write("### Dataset Overview\n")
        f.write(f"- Total flights: {len(df)}\n")
        f.write(f"- Airlines: {len(df['airline_name'].unique())}\n")
        f.write(f"- Airports: {len(df['departure_airport'].unique())} departure, {len(df['arrival_airport'].unique())} arrival\n\n")
        f.write("Generated by Flight Data Agentic AI System")

# Example usage
if __name__ == "__main__":
    # Create a .env file with GEMINI_API_KEY=your_api_key
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write('GEMINI_API_KEY=your_api_key_here\n')
        print("Created .env template file. Please add your Gemini API key.")
    else:
        questions = [
            "Which airlines fly from Christchurch to Auckland?",
            "What's the most common departure airport in Asia?",
            "How many flights are operated by Air New Zealand?",
            "Tell me something interesting about this flight data"
        ]
        
        generate_readme(questions)
        print("README.md file generated successfully!")