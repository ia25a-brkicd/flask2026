import os
import requests
def send_simple_message():
  	return requests.post(
  		"https://api.mailgun.net/v3/sandboxaac2dec4f1b445bf9c922b43c85e6d22.mailgun.org/messages",
  		auth=("api", os.getenv('API_KEY', 'API_KEY')),
  		data={"from": "Mailgun Sandbox <postmaster@sandboxaac2dec4f1b445bf9c922b43c85e6d22.mailgun.org>",
			"to": "Dario Brkic <brkicd@bzz.ch>",
  			"subject": "Hello Dario Brkic",
  			"text": "Congratulations Dario Brkic, you just sent an email with Mailgun! You are truly awesome!"})