import os
from groq import Groq


client = Groq(api_key=os.getenv("GROQ_API_KEY"))
print("Sending request...")
response = client.chat.completions.create(
    messages=[
        {"role": "user", "content": "what is the most expensive shoes in world"}
    ],
    model="llama-3.1-8b-instant"
)
print("Done!") 
print(response.choices[0].message.content)