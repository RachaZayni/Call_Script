from faker import Faker
from simple_salesforce import Salesforce
from accessDatabase import init
from consumer_details import PASSWORD,USERNAME,CONSUMER_KEY,CONSUMER_SECRET
# Initialize Faker and Salesforce connection
fake = Faker()
u,auth,a=init()
sf = Salesforce(instance_url=u, session_id=a)



for _ in range(20):
    lead = {
        'FirstName': fake.first_name(),
        'LastName': fake.last_name(),
        'Company': fake.company(),
        'Email': fake.email(),
        'Phone': fake.phone_number(),
        'MobilePhone': fake.phone_number(),
        'Title': fake.job(),
        'LeadSource': fake.random_element(elements=['Web', 'Phone Inquiry', 'Trade Show', 'Referral', 'Partner', 'Other']),
        'Status': fake.random_element(elements=['New', 'Working', 'Nurturing', 'Qualified', 'Unqualified']),
        'Description': fake.catch_phrase(),
        'Street': fake.street_address(),
        'City': fake.city(),
        'State': fake.state(),
        'PostalCode': fake.zipcode(),
        'Country': 'United States',
        'Industry': fake.random_element(elements=['Technology', 'Healthcare', 'Finance', 'Education', 'Manufacturing', 'Retail']),
        'AnnualRevenue': fake.random_int(min=100000, max=10000000),
        'NumberOfEmployees': fake.random_int(min=1, max=1000),
        'Website': fake.url()
    }

    # Create a new Lead in Salesforce
    sf.Lead.create(lead)

print("20 fake lead records have been added to Salesforce.")
