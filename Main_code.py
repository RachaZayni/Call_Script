from datetime import datetime
import customtkinter as ctk
import speech_recognition as sr
import pyttsx3
import threading
from pydantic import BaseModel
from pydantic_ai import Agent
from typing import List
import os
from accessDatabase import AccessDB,init,is_datetime_occupied,create_event
import time
import re
from transformers import pipeline
import requests
from queue import Queue




product="tablet"
lead_id=2


sentiment_analyzer = pipeline("sentiment-analysis", model='distilbert/distilbert-base-uncased-finetuned-sst-2-english')
prefer_messages = False  # Global flag for message preference
message_queue = Queue()


duration_label=None
app=None
status_label=None
chat_display=None
running=True
timer_thread=None


os.environ["OPENAI_API_KEY"] = "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"
#os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
class UserContext(BaseModel):
    user_id: str
    messages: List[dict] = []

    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})


    def get_context(self):
        return self.messages




def end_call():
    global running
    running = False  # Stop the timer
    duration_label.configure(text="Call Ended")
    app.after(2000, app.quit)
    speaker.stop()



def count_time(now):
    while running:
        elapsed_time = datetime.now() - now
        minutes = elapsed_time.seconds // 60
        seconds = elapsed_time.seconds % 60
        txt = f"{minutes:02}:{seconds:02}"

        # Update the label in the main UI thread
        duration_label.configure(text=txt)
        time.sleep(1)


def send_message():
    # Get the message from the entry field
    message = message_entry.get().strip()
    if message:
        chat_display.insert(ctk.END, f"Me: {message}\n")
        message_entry.delete(0, ctk.END)  # Clear the entry field

        # Add the message to the queue
        message_queue.put(message)


def create_app():
   global prefer_messages_var
   global message_entry
# Create the main call window
   global app, status_label, duration_label, chat_display,timer_thread
   app = ctk.CTk()   #Creates the main application window.
   now=datetime.now()
   running = True
   app.title("AI Call Interface")
   app.geometry("400x600")

# Call status
   status_label = ctk.CTkLabel(app, text="Connecting...", font=("Arial", 18)) #A text label widget for displaying the call status.
   status_label.pack(pady=20) #Adds padding around the label for spacing.

# Call duration
   duration_label = ctk.CTkLabel(app, text="00:00", font=("Arial", 14))
   duration_label.pack(pady=5)

# Call display (like a chat bubble)
   chat_display = ctk.CTkTextbox(app, width=350, height=200)
   chat_display.pack(pady=20)


   prefer_messages_var = ctk.BooleanVar(value=False)
   message_toggle = ctk.CTkCheckBox(app, text="I prefer to send messages", variable=prefer_messages_var,
                                 command=toggle_message_preference)
   message_toggle.pack(pady=10)

   message_entry = ctk.CTkEntry(app, width=300, placeholder_text="Type your message...")
   message_entry.pack(pady=5)
   message_entry.configure(state="disabled")

   send_button = ctk.CTkButton(app, text="Send", command=send_message, width=200)
   send_button.pack(pady=10)

   #end button
   end_button = ctk.CTkButton(app, text="End Call", command=end_call, width=200)
   end_button.pack(pady=10)


   timer_thread = threading.Thread(target=count_time,args=(now,))
   timer_thread.start()


   return timer_thread



def toggle_message_preference():
    global prefer_messages
    prefer_messages = prefer_messages_var.get()
    if prefer_messages:
        status_label.configure(text="Message Mode")
        message_entry.configure(state="normal")
    else:
        status_label.configure(text="Voice Mode")
        message_entry.configure(state="disabled")


# Listen and respond function
def listen_and_respond():
    global speaker
    client_text = ""
    end=0;
    recognizer = sr.Recognizer()

    # Initialize the text-to-speech engine
    speaker = pyttsx3.init()

    with sr.Microphone() as source:
        try:


                initial_message = f"begin a call with an unexpected statment"
                ai_initial_response = agent.run_sync(initial_message,
                                                     context=user_context.get_context())

                user_context.add_message("assistant", ai_initial_response.output)
                chat_display.insert("end", f"Bot: {ai_initial_response.output}\n")

                status_label.configure(text="Talking...")
                speaker.say(ai_initial_response.output)
                speaker.runAndWait()
                while True:
                    prefer_messages = prefer_messages_var.get()
                    if prefer_messages:
                         if not message_queue.empty():
                              client_text = message_queue.get()
                    else:
                # Listen for client speech
                          with sr.Microphone() as source:
                               recognizer.adjust_for_ambient_noise(source)  # Reduce background noise
                               status_label.configure(text="Listening...")
                               audio = recognizer.listen(source)  # Capture the audio


                          try:
                    # Convert speech to text
                               client_text = recognizer.recognize_google(audio)
                               end=0

                          except Exception as e:
                           end += 1;
                           if end >= 5:
                            end_call()
                           chat_display.insert("end", f"Bot: I didn't catch that. Please try again.\n")
                           speaker.say("I didn't catch that. Please try again.")
                           speaker.runAndWait()

                    if len(client_text) > 0:

                       user_context.add_message("user", client_text)
                       sentiment = sentiment_analyzer(client_text)[0]
                       sentiment_label = sentiment['label']

                       if sentiment_label == "POSITIVE":
                                  ai_response = positive_agent.run_sync(client_text,context=user_context.get_context(),)
                       elif sentiment_label=="NEGATIVE":
                                  ai_response = negative_agent.run_sync(client_text,context=user_context.get_context(),)
                       else :
                                ai_response=neutral_agent.run_sync(client_text,context=user_context.get_context(),)



                       if ai_response.output.lower()== "end":
                          chat_display.insert("end", f"Bot: Thanks for the chat. If you need any more help, just let us know. Goodbye!\n")
                          speaker.say("Thanks for the chat. If you need any more help, just let us know. Goodbye!")
                          time.sleep(7)
                          end_call()
                       elif bool(re.match(r"^\d+(\.\d+)?,\d+(\.\d+)?$", ai_response.output)):
                                parts = ai_response.output.split(",")
                                nb_hours = int(parts[0])
                                nb_days = int(parts[1])
                                if not is_datetime_occupied(datetime.now().day+nb_days,datetime.now().hour+nb_hours):
                                    create_event(nb_hours,nb_days)
                                    chat_display.insert("end",f"Bot:your demo is scheduled!\n")
                                    speaker.say( "your demo is scheduled!")
                                    user_context.add_message("assistant", "your demo is scheduled!")
                                else :
                                    chat_display.insert("end", f"Bot: sorry.. this date is unavailable, choose another one")
                                    user_context.add_message("assistant", "sorry.. this date is unavailable, choose another one")
                                    # Speak the response
                                    speaker.say("sorry.. this date is unavailable, choose another one")
                                    speaker.runAndWait()

                       else:
                                chat_display.insert("end", f"Bot: {ai_response.output}\n")

                                user_context.add_message("assistant", ai_response.output)

                    # Speak the response
                                speaker.say(ai_response.output)
                                speaker.runAndWait()
                    client_text=''


        except KeyboardInterrupt:
            print("\nCall ended.")
            speaker.stop()



####Main Program


url,auth,a=init()
query = f"SELECT Phone FROM Lead"
response = requests.get(url, headers=auth, params={"q": query})
r2=response.json()





PhoneNb= r2["records"][lead_id]["Phone"]
lead_data = AccessDB(PhoneNb)
user_context = UserContext(user_id=lead_data["Id"])

lead_info_text = "\n".join([f"{k}: {v}" for k, v in lead_data.items()])
user_context.add_message("user", f"Lead information:\n{lead_info_text}\n.")


positive_prompt = f"""
        - Be encouraging and positive in your responses.
        - Attempt to schedule a demo if the client expresses interest.
        - If the client agrees, ask for a preferred date and time for the demo.
        - If the client provides a demo date and time, respond **only** with the time difference from the current date 
          in the format: **<nbDays>,<nbHours>**, where **nbDays** and **nbHours** represent the number of full days 
          and hours from now until the provided date and time.
        - Once the client specifies a date, do not ask for it again.
        - If the client tries to end the conversation, respond with the single word: **"end"**.
        - The current date is **{datetime.today()}** and the current time is **{datetime.now()}**.
        - Keep responses under 25 words.
    """


negative_prompt ="""
        - Address the client's concerns patiently and provide supportive responses.
        - Emphasize the benefits of the demo to overcome hesitation.
        - If the client tries to end the conversation, respond with the single word: **"end"**.
        - Keep responses under 25 words.
     """

neutral_prompt=f"""
        - Provide clear, factual information without pushing too hard.
        - Respond to demo requests without being overly enthusiastic or forceful.
        - If the client asks for a demo date and time, respond **only** with the time difference 
          from the current date in the format: **<nbDays>,<nbHours>**.
        - Once the client specifies a date, do not ask for it again.
        - If the client tries to end the conversation, respond with the single word: **"end"**.
        - The current date is **{datetime.today()}** and the current time is **{datetime.now()}**.
        - Keep responses under 25 words.
    """
positive_agent = Agent(
    name="Engager Agent",
    model='openai:gpt-4',
    system_prompt=positive_prompt,
    max_tokens=40
)

negative_agent = Agent(
    name="Advisor Agent",
    model='openai:gpt-4',
    system_prompt=negative_prompt,
    max_tokens=40
)
neutral_agent = Agent(
    name="Reassurer Agent",
    model='openai:gpt-4',
    system_prompt=neutral_prompt,
    max_tokens=40
)


agent = Agent(
    name="Sales Buddy",
    model='openai:gpt-4o',
    system_prompt=f"""
    You are a persuasive salesperson for {product}.
    - Use the lead's information to customize your pitch.
    - Highlight benefits and different advantages.
    - Keep responses clear, friendly, and under 20 words.
    """,
    user_context=user_context.get_context(),
    deps_type=datetime,
)

thread2 = threading.Thread(target=listen_and_respond, daemon=True)
thread2.start()
create_app()
app.mainloop()


