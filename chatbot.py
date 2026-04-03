import os
from groq import Groq


client = Groq(api_key=os.getenv("GROQ_API_KEY"))
 

 
 
# 📝 Conversation history
history = [{"role": "system", "content": "You are a friendly customer service agent for a store in Oran. Answer politely, provide store info, product info, and be helpful to customers.and if the request is anything not related to the store say i cant assist you with that !"}] 

print("Welcome to your Groq CLI chatbot! Type 'quit' to exit.")

while True:
    user_input = input("You: ")

    if user_input.lower() == "quit":
        print("Exiting... Goodbye!")
        break

    # Add user message to conversation history
    history.append({"role": "user", "content": user_input})

    print("Sending request...")

    # Send full conversation history to the API
    response = client.chat.completions.create(
        messages=history,
        model="llama-3.1-8b-instant"
    )

    print("Done!")

    # Get AI response
    ai_message = response.choices[0].message.content
    print("AI:", ai_message)

    # Add AI response to conversation history
    history.append({"role": "assistant", "content": ai_message})