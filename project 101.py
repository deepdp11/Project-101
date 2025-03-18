import requests
import re
from bs4 import BeautifulSoup
from serpapi import GoogleSearch
import pandas as pd

SERPAPI_KEY = "5b21fc83d7b1f6f315608d4d0c6d7e9cd6e28e54e642257c154724b86f6634bf"  

# Search manufacturers on Google
def search_manufacturers(query, num_results=10):
    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": num_results
    }
    response = GoogleSearch(params).get_dict()
    manufacturer_list = []
    
    for result in response.get("organic_results", []):
        title = result.get("title", "N/A")
        link = result.get("link", "")
        manufacturer_list.append((title, link))
    
    return manufacturer_list

# Function to find emails on a page
def extract_emails(url):
    try:
        response = requests.get(url, timeout=10)
        emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", response.text)
        return list(set(emails))  # Remove duplicates
    except:
        return []

# Function to find the contact page
def find_contact_page(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Look for links with "contact"
        for link in soup.find_all("a", href=True):
            href = link.get("href")
            if "contact us" in href.lower():
                if href.startswith("http"):
                    return href
                elif href.startswith("/"):
                    return url + href  # Handle relative URL
        
        return None  # No contact page found
    except:
        return None

# Run the full scraping process
def scrape_manufacturer_emails(search_query):
    manufacturers = search_manufacturers(search_query, num_results=5)  # Get first 5 results
    results = []
    
    for name, website in manufacturers:
        print(f"Scraping {name} ({website})")
        
        emails = extract_emails(website)  # Try homepage
        if not emails:
            contact_page = find_contact_page(website)
            if contact_page:
                print(f"Checking contact page: {contact_page}")
                emails = extract_emails(contact_page)

        results.append({"Company": name, "Website": website, "Emails": emails})
    
    return results

# Example search
query = "wooden furniture manufacturers in alberta "
manufacturer_emails = scrape_manufacturer_emails(query)

for company in manufacturer_emails:
    print(company)

emaildata = pd.DataFrame(manufacturer_emails)
emaildata.to_csv("manufacturers_with_emails.csv", index=False)

import google.generativeai as genai
import pandas as pd

# Gemini API key
genai.configure(api_key="AIzaSyDxH4ZqX0rlbhCj7LWHz0S1PKeD2xQinnY")

# Load the Gemini model
model = genai.GenerativeModel("gemini-2.0-flash")

# Load the manufacturers data from a CSV file
df = pd.read_csv("manufacturers_with_emails.csv")  

# function to generate an email
def generate_email(company):
    prompt = f"""
    Generate a professional email for a furniture manufacturer inquiry:
    - Address it to the team at {company}.
    - Mention that you are interested in supplying raw materials.
    - Maintain a formal and polite tone.
    -only mention my name Dp, Company name DP wood supplier and my website,contact no https://dpwoodsupplier.com
    +17779998899

    Example:

    Subject: Potential Business Partnership with {company}

    Dear {company} Team,

    I hope this email finds you well. I am reaching out to explore a potential collaboration with {company}. 
    We are very interested in learning more about your products and discussing how we could work together. 

    Please let me know a convenient time for a quick call to discuss this further.

    Looking forward to your response.

    Best regards,  
    DP wood supplier
    https://dpwoodsupplier.com
    +17779998899
    """

    # Generate email using Google Gemini API
    response = model.generate_content(prompt)
    
    return response.text  # Get the response text from the API

emails = []

for index, row in df.iterrows():
    company_name = row["Company"]
    email_list = row["Emails"] if pd.notna(row["Emails"]) else "No email found"

    email_text = "No valid email found"
    
    if email_list:  # If an email exists, generate email content
        email_text = generate_email(company_name)

    # Store the results
    email_entry = {
        "Company": company_name,
        "Website": row["Website"],
        "Emails": email_list,
        "Generated Email": email_text
    }
    
    emails.append(email_entry)

# Save results to a CSV file
final_df = pd.DataFrame(emails)
final_df.to_csv("manufacturers_with_emails.csv", index=False)

print("Personalized emails generated and saved.")
