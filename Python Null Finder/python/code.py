#                          Python Null finder
import re

# --- Step 1: Input and Output Files ---
input_file = "input_text.txt"      # The file to read from
output_file = "extracted_emails.txt"  # The file to save results

# --- Step 2: Read content from the input file ---
try:
    with open(input_file, "r", encoding="utf-8") as file:
        content = file.read()
except FileNotFoundError:
    print(f"❌ Error: The file '{input_file}' was not found.")
    exit()

# --- Step 3: Use Regular Expression to find emails ---
# Basic regex for email pattern
email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

emails = re.findall(email_pattern, content)

# --- Step 4: Remove duplicates (optional but useful) ---
unique_emails = sorted(set(emails))

# --- Step 5: Save emails to the output file ---
with open(output_file, "w", encoding="utf-8") as file:
    for email in unique_emails:
        file.write(email + "\n")

# --- Step 6: Display results ---
print(f"✅ Found {len(unique_emails)} unique email addresses.")
print(f"📄 Saved them to '{output_file}'.")







#                         Python rule based chatbot
--- Simple Rule-Based Chatbot ---

def chatbot_response(user_input):
    """Return a predefined response based on user input."""
    user_input = user_input.lower().strip()  # normalize input

    if user_input in ["hi", "hello", "hey"]:
        return "Hi there! 👋"
    elif user_input in ["how are you", "how are you doing"]:
        return "I'm just a bunch of code, but I'm doing great! 😄"
    elif user_input in ["what is your name", "who are you"]:
        return "I'm your friendly Python chatbot!"
    elif user_input in ["bye", "goodbye", "exit"]:
        return "Goodbye! 👋 Have a nice day!"
    else:
        return "Sorry, I didn't understand that. Try saying 'hello' or 'bye'."

# --- Main Chat Loop ---
print("🤖 Chatbot: Hello! Type something to chat (type 'bye' to exit).")

while True:
    user_message = input("You: ")
    response = chatbot_response(user_message)
    print("🤖 Chatbot:", response)
    
    # Exit loop if user says bye
    if user_message.lower() in ["bye", "goodbye", "exit"]:
        break

