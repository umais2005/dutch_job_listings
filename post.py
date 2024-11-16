from requests.auth import HTTPBasicAuth
import requests
from typing import Literal

def get_manatal_jobs(n_jobs=-1, return_ids=True):

    url = "https://api.manatal.com/open/v3/jobs/"

    headers = {
        "accept": "application/json",
        "Authorization": "Token eb1947c4c16cda453aa48c434bcbcd463b610f62"
    }

    response = requests.get(url, headers=headers)
    if return_ids:
        return [res['id'] for res in response.json()['results']]
    else:
        return response.json()['results'][n_jobs]

def post_manatal_jobs(job_dict=None, test=False):

    url = "https://api.manatal.com/open/v3/jobs/"

    if test:
        job_dict = {'Job title': 'Tandarts (TESTING)', 'Job description': '<b>Functieomschrijving</b><br>Als tandarts-endodontoloog bij ons team, ben vaardigheden op het gebied van endodontologie en bent nauwkeurig, gestructureerd en communicatief vaardig. Je kunt goed functioneren in een team en hebt een passende opleiding met diploma.<br><br><b>Wie wij zoeken</b><br>Wij zoeken een enthousiaste endodontoloog om ons team te versterken in onze algemene praktijk. Je bent een teamplayer met een sterke focus op kwaliteit en patiëntenzorg. De werkdagen worden in overleg vastgesteld.<br><br><b>Wat wij bieden</b><br>Wij bieden goede arbeidsvoorwaarden, inclusief een salaris boven het KNMT-advies en PFZW-pensioenopbouw. Werken op zzp-basis is ook mogelijk. Je komt in een uitdagende en afwisselende functie in een aantrekkelijke en goed georganiseerde omgeving. Samen met een enthousiast team werk je mee aan goede tandzorg voor iedereen. Betrokkenheid en bevlogenheid scoren hoog in onze organisatie.', 'Location': 'Nederland', 'Contract Details': 'Deeltijd', 'Job Industry': 
        'Medisch / Farmaceutisch', 'Client': 'Fleming'}

    payload = {
        "external_id": job_dict.get("id"),
        "organization": 2537874,
        "position_name": job_dict.get("Job title", "Untitled"),
        "description": job_dict.get("Job description", "No content provided"),
        "headcount": 1,
        "address": job_dict.get("Location", "Unknown Location"),
        "contract_details": 'part_time',
        "is_published": True,
        'industry': {'id': 5039075, 'name': 'Medical / Pharmaceutical'}
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": "Token eb1947c4c16cda453aa48c434bcbcd463b610f62"
    }

    response = requests.post(url, json=payload, headers=headers)

    return response.json()



def post_job_to_wordpress(job_dict=None,
                          status:Literal["publish", "draft"] = "draft",
                          test=False):
    """
    Post the job listing to WordPress.Bt default, it will make a draft.
    """
    WORDPRESS_URL = "https://mondzorgvacatures.com"  # Replace with your site URL
    API_ENDPOINT = f"{WORDPRESS_URL}/wp-json/wp/v2/job-listings"
    
    USERNAME = "Scrape"  # Replace with your WordPress username
    APPLICATION_PASSWORD = "6UDwTHJ6HmGhnelGmjy1NLn0"  # Replace with your Application Password
    if test:
        job_dict = {'Job title': 'TEST', 'Job description': '<b>Functieomschrijving</b><br>Als tandarts-endodontoloog bij ons team, ben vaardigheden op het gebied van endodontologie en bent nauwkeurig, gestructureerd en communicatief vaardig. Je kunt goed functioneren in een team en hebt een passende opleiding met diploma.<br><br><b>Wie wij zoeken</b><br>Wij zoeken een enthousiaste endodontoloog om ons team te versterken in onze algemene praktijk. Je bent een teamplayer met een sterke focus op kwaliteit en patiëntenzorg. De werkdagen worden in overleg vastgesteld.<br><br><b>Wat wij bieden</b><br>Wij bieden goede arbeidsvoorwaarden, inclusief een salaris boven het KNMT-advies en PFZW-pensioenopbouw. Werken op zzp-basis is ook mogelijk. Je komt in een uitdagende en afwisselende functie in een aantrekkelijke en goed georganiseerde omgeving. Samen met een enthousiast team werk je mee aan goede tandzorg voor iedereen. Betrokkenheid en bevlogenheid scoren hoog in onze organisatie.', 'Location': 'Nederland', 'Contract Details': 'Deeltijd', 'Job Industry': 
        'Medisch / Farmaceutisch', 'Client': 'Fleming'}
    # Prepare the data for the job listing
    post = {
        "title": { "raw": job_dict.get("Job title", "Untitled") },
        "content": { "raw": job_dict.get("Job description", "No content provided")},
        "status": status,
        "meta": {
            "_job_location": job_dict.get("Location", "Unknown Location"),
            "_id": job_dict.get("id", "1234") , # Use the hashed ID if available
            "_application": "info@mondzorgrecruiters.nl",
            "_company_manager_id": "6061"

        }
    }

    try:
        response = requests.post(
            API_ENDPOINT,
            auth=HTTPBasicAuth(USERNAME, APPLICATION_PASSWORD),
            json=post
        )
    
        if response.status_code == 201:
            post_id = response.json()['id']
            print(f"Job created successfully with ID: {post_id}")
            return response.json()
        else:
            print(f"Failed to create post. Status Code: {response.status_code}")
            print("Response:", response.text)
            return None
    except Exception as e:
        print("An error occurred:", str(e))
        return None
    
if __name__ == "__main__":
    resp = get_manatal_jobs()
    # post_manatal_jobs(test=True)
    # resp = post_job_to_wordpress(test=True)
    print(resp)
