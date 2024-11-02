from flask import Flask, request, jsonify
import random
import re
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from flask_cors import CORS

# Load environment variables
load_dotenv()
secret_key = os.getenv("APP_PASS")
email_s = os.getenv("USER_ID")

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Required for session management
CORS(app)

# State tracking dictionary for simplicity
conversation_state = {}

class RuleBot:
    negative_res = ("no", "nope", "nah", "naw", "not a chance", "sorry")
    exit_commands = ("quit", "pause", "exit", "goodbye", "bye", "later")

    def check_exit(self, response):
        if response in self.exit_commands or response in self.negative_res:
            return {"message": "Have a nice day!", "end_conversation": True}
        return None

    def validate_email(self, email):
        regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
        return re.match(regex, email)

    def send_otp(self, email):
        otp_number = random.randint(1111, 9999)
        subject = "Train Ticket"
        body = "Your OTP is " + str(otp_number)

        message = MIMEText(body)
        message['Subject'] = subject
        message['From'] = email_s
        message['To'] = email

        # try:
        #     with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        #         server.login(email_s, secret_key)
        #         server.sendmail(email_s, email, message.as_string())
        # except smtplib.SMTPAuthenticationError as e:
        #     print("Authentication failed:", e)
        #     return {"error": "Failed to send OTP. Check email credentials."}
        test = str(email_s) + str(secret_key) + str(email)
        return test

# Initialize RuleBot instance
bot = RuleBot()

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_id = data.get('user_id')
    user_input = data.get('message').strip().lower()

    # Initialize or reset conversation state if user_id is new or if user is starting over
    if user_id not in conversation_state or user_input == "restart":
        conversation_state[user_id] = {"step": "start"}

    # Retrieve the current state for this user
    state = conversation_state[user_id]
    response = None

    # Handle exit phrases
    exit_check = bot.check_exit(user_input)
    if exit_check:
        conversation_state.pop(user_id, None)  # Clear the state on exit
        return jsonify(exit_check), 200

    if state["step"] == "start":
        response = {"message": "Hi! What is your name?", "next_step": "ask_name"}
        state["step"] = "ask_name"
    elif state["step"] == "ask_name":
        state["name"] = user_input
        response = {"message": f"Hi {state['name']}, do you wish to book a train ticket?", "next_step": "confirm_booking"}
        state["step"] = "confirm_booking"
    elif state["step"] == "confirm_booking":
        if user_input in ["yes", "y"]:
            response = {"message": "Please enter your age:", "next_step": "ask_age"}
            state["step"] = "ask_age"
        else:
            response = {"message": "Alright! Have a nice day!", "end_conversation": True}
            conversation_state.pop(user_id, None)  # Clear the state
    elif state["step"] == "ask_age":
        if user_input.isdigit() and int(user_input) >= 18:
            response = {"message": "Please enter your boarding station:", "next_step": "ask_source"}
            state["step"] = "ask_source"
        else:
            response = {"message": "You are too young to book. Have a nice day!", "end_conversation": True}
            conversation_state.pop(user_id, None)
    elif state["step"] == "ask_source":
        state["source"] = user_input
        response = {"message": "Please enter your destination station:", "next_step": "ask_destination"}
        state["step"] = "ask_destination"
    elif state["step"] == "ask_destination":
        if user_input != state["source"]:
            state["destination"] = user_input
            response = {"message": "Please enter your email for confirmation:", "next_step": "ask_email"}
            state["step"] = "ask_email"
        else:
            response = {"message": "Destination and boarding stations cannot be the same. Please enter a different destination station."}
    elif state["step"] == "ask_email":
        if bot.validate_email(user_input):
            otp = bot.send_otp(user_input)
            state["otp"] = otp
            response = {"message": otp, "next_step": "verify_otp"}
            state["step"] = "verify_otp"
        else:
            response = {"message": "Invalid email format. Please enter a valid email address."}
            # Stay in the "ask_email" step to allow for re-entry.
    elif state["step"] == "verify_otp":
        if user_input == str(state.get("otp")):
            response = {"message": "Verified! Your ticket will be sent to you soon.", "end_conversation": True}
            conversation_state.pop(user_id, None)  # Clear the state after completion
        else:
            response = {"message": "Invalid OTP. Please try again."}
            # Stay in the "verify_otp" step to allow for re-entry.

    return jsonify(response), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
