import random
import re
from dotenv import load_dotenv
import os

load_dotenv()

secret_key = os.getenv("APP_PASS")
email_s = os.getenv("USER_ID")


class RuleBot:
    ##response
    negative_res = ("no", "nope", "nah", "naw", "not a chance", "sorry")
    exit_commands = ("quit", "pause", "exit", "goodbye", "bye", "later")

    # def __init__(self):
    #     self.alienbabble = {
    #         'describe_planet_intent': r'.*\s*your planet.*',
    #         'answer_why_intent': r'why\sare.*',
    #         'about_intellipaat': r'.*\s*intellipaat.*'
    #     }

    def book_or_not(self):
        name = input("what is your name ?\n")
        self.check_exit(name)
        to_book_or_not = input(
            f"Hi, {name}, I am here to help you book your train ticket. Do you wish to continue?\n")
        self.check_exit(to_book_or_not)
        self.yes_book()

    def yes_book(self):
        age = input("Enter your Age:")
        if age in (self.negative_res, self.exit_commands):
            print("Have nice day!")
            exit()
        if not age.isdigit():
            print("Your response is invalid, please try again!")
            self.yes_book()
        elif int(age)<18:
            print("You are too young too book!, Have a nice day")
        else:
            self.source()

    def source(self):
        source_place = input("Enter the name of the station you will be boarding from:").lower()
        self.check_exit(source_place)
        if not source_place.isalpha():
            print("Your response is invalid, please try again!")
            self.source()
        else:
            self.destination(source_place)

    def destination(self, source_place):
        destination_place = input("Enter the name of the destination station:").lower()
        self.check_exit(destination_place)
        if not destination_place.isalpha():
            self.destination()
        else:
            if destination_place == source_place:
                print("Destination and Boarding cannot be same.")
                self.destination()
            # print("booked succesfully")
            # return
            self.c_mail()

    def c_mail(self):
        email = input("Please enter your email for the confirmation:")
        self.check_exit(email)

        """Check if the email is a valid format."""
        # Regular expression for validating an Email
        regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
        # If the string matches the regex, it is a valid email
        if re.match(regex, email):
            self.send_otp(email)
        else:
            print(f"'{email}' is an invalid email address.")
            self.c_mail(email)

    def send_otp(self, email):
        # email send gmail
        import smtplib
        from email.mime.text import MIMEText

        # Define your email content and credentials
        subject = "Train Ticket"
        otp_number = random.randint(1111, 9999)
        body = "Your otp is " + str(otp_number)
        sender_email = email_s
        receiver_email = email
        password = secret_key  # Be cautious with passwords in code!

        # Create MIMEText object
        message = MIMEText(body)
        message['Subject'] = subject
        message['From'] = sender_email
        message['To'] = receiver_email

        # Connect to Gmail's SMTP server
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:  # Note the use of port 587 for STARTTLS
            # server.ehlo()  # Can be called optionally (It is called automatically after a connect)
            # server.starttls()  # Secure the connection
            # server.ehlo()  # Can be called optionally (It reidentifies us to the server post-STARTTLS)
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())  # Send the email

            print("Otp sent successfully!")
        # print(otp_number)
        opt = input("Enter the otp send to your email:")
        if int(opt) == otp_number:
            print("Verified, Your ticket will be send to you soon.")
        else:
            print("wrong otp \n")
            opt = input("Enter the otp send to your email:")
            if opt == otp_number:
                print("Verified, Your ticket will be send to you soon.")
            else:
                exit()

    def check_exit(self, response):
        if response in self.exit_commands or response in self.negative_res:
            print("Have nice day!")
            exit()


bot = RuleBot()
bot.book_or_not()