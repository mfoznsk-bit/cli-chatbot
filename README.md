# CLI Chatbot with Python and Groq API

## What it does
This is a simple command-line interface (CLI) chatbot built using Python and the Groq API. The chatbot allows you to type messages, sends them to the AI, and displays responses. It supports keeping track of conversation history so the AI can respond based on previous messages. You can exit the chatbot by typing `quit`.

## How to Install
1. Make sure you have Python installed (version 3.10+ recommended).  
2. Install the Groq Python package by running:

```bash
pip install groq
Set your Groq API key as an environment variable:

Windows PowerShell:

setx GROQ_API_KEY "your_api_key_here"

Mac/Linux:

export GROQ_API_KEY="your_api_key_here"
# How to Run
Open a terminal and navigate to the project folder.
Run the chatbot:
python chatbot.py
Start chatting with the AI! Type quit to exit the chatbot.
#What I Learned
How to use the Groq API in Python.
How to create a CLI application that handles user input and displays AI responses.
How to maintain conversation history for context-aware replies.
How to safely store and use API keys using environment variables.
Basic Git and GitHub workflow: commit, push, and manage your repository.