import pandas as pd
import requests
from consumer_details import CONSUMER_SECRET,CONSUMER_KEY,USERNAME,PASSWORD
from pydantic import BaseModel, Field
from pydantic import BaseModel
from pydantic_ai import Agent
from datetime import datetime,timedelta
from dateutil import parser

import os
os.environ["OPENAI_API_KEY"] = "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"

global auth_url
auth_url='https://login.salesforce.com/services/oauth2/token'

global data
data = {
    'client_id':CONSUMER_KEY,
    'client_secret':CONSUMER_SECRET,
    'grant_type':'password',
    'username':USERNAME,
    'password':PASSWORD
                    }
class Contact(BaseModel):
    name: str
    description: str
    email: str

def init():
    redirect_uri = 'http://localhost/'

    response = requests.post(auth_url, data)
    json_res = response.json() ##Converts the response to a Python dictionary.
    access_token = json_res['access_token']
    auth = {'Authorization':'Bearer ' + access_token} #Prepares the authorization header for future API requests.
    instance_url = json_res['instance_url']
    url = instance_url + '/services/data/v57.0/query'
    return url, auth,access_token



agent = Agent(
    model='openai:gpt-4',
    system_prompt='Be concise, reply with one sentence.',
)

def AccessDB(phoneNb):
    url,auth,a=init()
    query = f"SELECT Id, Name, Company,Title,Industry,LeadSource,Status,Description,AnnualRevenue,NumberOfEmployees,Country,State FROM Lead WHERE Phone = '{phoneNb}'"
    response = requests.get(url, headers=auth, params={"q": query})
    r2=response.json()

    lead_record = r2["records"][0]

    lead_data = {
        "Id": lead_record.get("Id", "Unknown"),
        "Name": lead_record.get("Name", "Unknown"),
        "Company": lead_record.get("Company", "Unknown"),
        "Title": lead_record.get("Title", "Unknown"),
        "Industry": lead_record.get("Industry", "Unknown"),
        "LeadSource": lead_record.get("LeadSource", "Unknown"),
        "Status": lead_record.get("Status", "Unknown"),
        "Description": lead_record.get("Description", "Unknown"),
        "AnnualRevenue": lead_record.get("AnnualRevenue", "Unknown"),
        "NumberOfEmployees": lead_record.get("NumberOfEmployees", "Unknown"),
        "Country": lead_record.get("Country", "Unknown"),
        "State": lead_record.get("State", "Unknown"),
    }

    return  lead_data

def create_event(nbH,nbD):
    _, _, access_token = init()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    event_data = {
        "Subject": "AI Agent Meeting",
        "Location": "Virtual",
        "StartDateTime": (datetime.utcnow() + timedelta(days=nbD, hours=nbH)).isoformat() + "Z",

        "EndDateTime": (datetime.utcnow() + timedelta(days=nbD, hours=nbH+1)).isoformat() + "Z",
        "Description": "Discussing AI agent integration with Salesforce."
    }

    response = requests.post(auth_url, data)
    json_res = response.json()  ##Converts the response to a Python dictionary.
    instance_url = json_res['instance_url']

    response.raise_for_status()
    url = f"{instance_url}/services/data/v59.0/sobjects/Event"
    response = requests.post(url, headers=headers, json=event_data)
    #response.raise_for_status()
    return response.json()





def is_datetime_occupied(day, hour):
        url, auth, _ = init()

        # Format the target datetime for comparison
        now = datetime.now()
        target_datetime = datetime(now.year, now.month, day, hour, 0, 0)

        # Salesforce datetime format: MM/DD/YYYY, HH:MM AM/PM
        query = """
        SELECT Id, Subject, FORMAT(StartDateTime), FORMAT(EndDateTime)
        FROM Event
        LIMIT 20
        """

        response = requests.get(url, headers=auth, params={"q": query})
        if response.status_code != 200:
            raise Exception(f"Salesforce API error: {response.status_code} - {response.text}")

        records = response.json().get("records", [])

        # Check if the target day and hour are occupied
        for record in records:
            start_datetime_str = record["StartDateTime"]
            end_datetime_str=record["EndDateTime"]
            start_datetime = datetime.strptime(start_datetime_str, '%m/%d/%Y, %I:%M %p')
            end_datetime = datetime.strptime(end_datetime_str, '%m/%d/%Y, %I:%M %p')
            print(start_datetime.hour)
            print(end_datetime.hour)
            # Ignore the year, just match day and hour
            if start_datetime.day==day and hour>=start_datetime.hour  and hour<= end_datetime.hour:
                return True

        return False


#AccessDB('984-606-3334')

#url, auth, a = init()
#print(create_event())




# Generate fake customer data

#fake = Faker()
#for _ in range(20):
#    customer = {
#        'FirstName': fake.first_name(),
#        'LastName': fake.last_name(),
#        'Email': fake.email(),
#        'Phone': fake.phone_number(),
 #       'Description': fake.catch_phrase()
 #   }
 #   # Create a new Contact in Salesforce
 #   sf.Contact.create(customer)

#print("Fake customer data has been added to Salesforce.")



