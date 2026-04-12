import os
import json
from groq import Groq
from datetime import datetime, timezone, timedelta

 
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = "llama-3.1-8b-instant"

tools = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": """Perform basic arithmetic operations on two numbers.
            Use this tool whenever the user asks for any calculation, math problem,
            price total, discount, or anything involving numbers and operations.
            Do NOT try to calculate mentally — always use this tool for math.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide"],
                        "description": "The operation: add, subtract, multiply, or divide"
                    },
                    "num1": {
                        "type": "number",
                        "description": "The first number in the operation"
                    },
                    "num2": {
                        "type": "number",
                        "description": "The second number in the operation"
                    }
                },
                "required": ["operation", "num1", "num2"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_datetime",
            "description": """Get the current date and time in Algeria (Algiers timezone, UTC+1).
            Use this tool whenever the user asks: what time is it, what day is today,
            what is today's date, what day of the week is it, or anything related
            to the current date or time. Always use this tool for time questions —
            never guess the date from training data.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "format": {
                        "type": "string",
                        "enum": ["full", "date_only", "time_only", "day_only"],
                        "description": """What to return:
                        'full' = full date + time (e.g. Wednesday 15 January 2025, 14:30),
                        'date_only' = just the date (e.g. 15 January 2025),
                        'time_only' = just the time (e.g. 14:30:22),
                        'day_only' = just the day name (e.g. Wednesday)"""
                    }
                },
                "required": ["format"]
            }
        }
    }
]
# Why is the description so detailed?
# Because Claude reads the description to decide WHEN to call the tool.
# The line "never guess the date from training data" is important —
# without it, the model might try to answer from memory instead of calling the tool.
# The more specific your description, the more reliably the tool gets called.

# =========================================================
# 2. PYTHON FUNCTIONS THAT ACTUALLY RUN THE TOOLS
# =========================================================

def calculator(operation: str, num1: float, num2: float):
    """
    The actual calculation happens here in Python.
    Claude never runs this — Claude just asks for it.
    Your code runs it and sends the result back.
    """
    if operation == "add":
        return num1 + num2
    elif operation == "subtract":
        return num1 - num2
    elif operation == "multiply":
        return num1 * num2
    elif operation == "divide":
        if num2 == 0:
            return "Error: Cannot divide by zero"
        return num1 / num2
    else:
        return f"Error: Unknown operation '{operation}'"


def get_datetime(format: str):
    """
    Returns the current date/time in Algeria timezone (UTC+1).
    
    Why UTC+1? Algeria uses Central European Time year-round.
    Oran and Algiers are both UTC+1.
    
    datetime.now(timezone.utc) gets the current UTC time.
    timedelta(hours=1) adds 1 hour to convert to Algerian time.
    """
    algeria_time = datetime.now(timezone.utc) + timedelta(hours=1)
    # datetime.now() gets current time.
    # timezone.utc makes it timezone-aware (not naive).
    # + timedelta(hours=1) shifts it forward 1 hour to Algeria time.

    if format == "full":
        return algeria_time.strftime("%A %d %B %Y, %H:%M:%S")
        # strftime() formats a datetime object into a readable string.
        # %A = full day name (Wednesday)
        # %d = day number (15)
        # %B = full month name (January)
        # %Y = 4-digit year (2025)
        # %H = hour in 24h format (14)
        # %M = minutes (30)
        # %S = seconds (22)

    elif format == "date_only":
        return algeria_time.strftime("%d %B %Y")
        # Returns: 15 January 2025

    elif format == "time_only":
        return algeria_time.strftime("%H:%M:%S")
        # Returns: 14:30:22

    elif format == "day_only":
        return algeria_time.strftime("%A")
        # Returns: Wednesday

    else:
        return algeria_time.strftime("%A %d %B %Y, %H:%M:%S")
        # Default fallback: return full format if unknown format given

# =========================================================
# 3. TOOL ROUTER FUNCTION
# =========================================================

def run_tool(function_name: str, arguments: dict):
    """
    This function receives the tool name and arguments from Claude
    and routes to the correct Python function.
    
    Why a separate router function?
    Because as you add more tools (weather, search, database)
    you just add more elif branches here. The main loop stays clean.
    
    function_name: the name Claude chose (e.g. "calculator")
    arguments: a dict of the inputs Claude decided to pass
    """
    if function_name == "calculator":
        return calculator(
            operation=arguments["operation"],
            num1=arguments["num1"],
            num2=arguments["num2"]
        )
    
    elif function_name == "get_datetime":
        return get_datetime(
            format=arguments.get("format", "full")
        )
        # arguments.get("format", "full") means:
        # try to get "format" from arguments.
        # If it doesn't exist, use "full" as default.
        # Safer than arguments["format"] which crashes if key missing.
    
    else:
        return f"Error: Tool '{function_name}' is not defined"
        # Safety net — if Claude hallucinates a tool name
        # that doesn't exist, we return an error instead of crashing.

# =========================================================
# 4. MAIN INTERACTIVE LOOP
# =========================================================

print("Groq Agent — Calculator + Date/Time Tools")
print("Ask me anything: math, date, time, or both.")
print("Type 'quit' to exit.\n")

while True:
    user_question = input("You: ").strip()
    # .strip() removes any accidental spaces before/after the text.

    if user_question.lower() in ["quit", "exit", "q"]:
        print("Goodbye!")
        break

    if not user_question:
        # if not user_question = if the string is empty.
        # An empty string is "falsy" in Python — so this catches
        # the case where user just pressed enter with no text.
        continue
        # continue = skip the rest of this loop iteration
        # and go back to the top of the while loop.

    # =========================================================
    # 5. BUILD THE MESSAGES LIST
    # =========================================================
    messages = [
        {
            "role": "system",
            "content": """You are a helpful assistant for a store in Oran, Algeria.
            You have access to a calculator tool and a date/time tool.
            Always use the calculator tool for any math — never calculate mentally.
            Always use the date/time tool for any time or date question — never guess.
            Reply in the same language the user uses."""
        },
        {
            "role": "user",
            "content": user_question
        }
    ]

    # =========================================================
    # 6. FIRST API CALL — Claude decides if it needs a tool
    # =========================================================
    try:
        # try: attempt this block of code.
        # If anything inside crashes, jump to except instead of crashing the whole program.

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto"
            # "auto" = Claude decides whether to call a tool or answer directly.
        )

    except Exception as e:
        # Exception = any error that can happen.
        # as e = store the error details in variable e.
        print(f"API Error on first call: {e}")
        # Print the error so you can see what went wrong.
        continue
        # Skip to next loop iteration instead of crashing.

    message = response.choices[0].message
    # .choices[0] = first (and usually only) response option.
    # .message = the full message object Claude returned.

    messages.append(message)
    # Add Claude's response to history so the next API call
    # has full context of what happened so far.

    # =========================================================
    # 7. TOOL USE LOOP — handle one or multiple tool calls
    # =========================================================
    while message.tool_calls:
        # while message.tool_calls = keep looping as long as
        # Claude is asking for tools. Claude can ask for
        # multiple tools in sequence — this handles all of them.

        print(f"Claude is using tools...")

        for tool_call in message.tool_calls:
            # Loop through each tool call Claude requested.
            # Usually just 1, but Claude can request multiple at once.

            function_name = tool_call.function.name
            # The name of the tool Claude wants to call.
            # e.g. "calculator" or "get_datetime"

            try:
                arguments = json.loads(tool_call.function.arguments)
                # tool_call.function.arguments comes back as a JSON string.
                # json.loads() converts it from string to Python dict.
                # e.g. '{"operation": "multiply", "num1": 50, "num2": 1800}'
                # becomes {"operation": "multiply", "num1": 50, "num2": 1800}

            except json.JSONDecodeError as e:
                # json.JSONDecodeError = specific error when JSON is malformed.
                # This catches the case where Claude sends broken JSON arguments.
                print(f"Failed to parse tool arguments: {e}")
                arguments = {}
                # Set empty dict so the program doesn't crash.
                # run_tool will return an error message gracefully.

            print(f"  Tool: {function_name}")
            print(f"  Input: {arguments}")

            try:
                result = run_tool(function_name, arguments)
                # Call our router function which calls the right Python function.
                # result is whatever the tool returns — a number, a date string, etc.

            except Exception as e:
                result = f"Tool execution failed: {e}"
                # If the tool itself crashes for any reason,
                # send the error as the result instead of crashing the program.
                # Claude will read this error and tell the user something went wrong.

            print(f"  Result: {result}")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
                # str(result) converts the result to string.
                # This is required — the API only accepts strings in content.
                # tool_call_id links this result to the specific tool call
                # Claude made. Important when Claude makes multiple tool calls.
            })

        # =========================================================
        # 8. NEXT API CALL — Claude reads the tool result
        # =========================================================
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages
                # No tools parameter here — we just want Claude
                # to read the tool result and give a final answer.
                # Though Claude can decide to call another tool if needed.
            )

        except Exception as e:
            print(f"API Error on follow-up call: {e}")
            break
            # break exits the while message.tool_calls loop.

        message = response.choices[0].message
        messages.append(message)
        # Update message so the while condition checks again.
        # If Claude needs another tool — loop continues.
        # If Claude is done — message.tool_calls will be empty/None
        # and the while loop exits.

    # =========================================================
    # 9. PRINT FINAL ANSWER
    # =========================================================
    if message.content:
        # Check that content is not None or empty before printing.
        print(f"\nAgent: {message.content}\n")
    else:
        print("\nAgent: (no response)\n")

