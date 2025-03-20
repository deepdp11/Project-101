# import requests
# import re
# from bs4 import BeautifulSoup
# from serpapi import GoogleSearch
# import pandas as pd
# import openai
# import time
# from urllib.parse import urljoin, urlparse

# # Ask user for their details
# supplier_name = input("Enter your name: ")
# supplier_company = input("Enter your company name: ")
# supplier_website = input("Enter your website URL: ")
# supplier_contact = input("Enter your contact number: ")
# supplied_materials = input("Enter the type of raw materials you supply: ")

# SERPAPI_KEY = "5b21fc83d7b1f6f315608d4d0c6d7e9cd6e28e54e642257c154724b86f6634bf"
# OPENAI_API_KEY = "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"

# openai.api_key = OPENAI_API_KEY

# def is_valid_url(url):
#     """Check if URL is valid and has proper scheme"""
#     parsed = urlparse(url)
#     return bool(parsed.netloc) and bool(parsed.scheme)

# def normalize_url(base_url, link):
#     """Normalize relative URLs to absolute URLs"""
#     if not link:
#         return None
        
#     # Handle links that are just anchors
#     if link.startswith('#'):
#         return None
        
#     # Handle mailto links
#     if link.startswith('mailto:'):
#         return None
        
#     # Handle phone links
#     if link.startswith('tel:'):
#         return None
        
#     # Handle JavaScript links
#     if link.startswith('javascript:'):
#         return None
        
#     # Join relative URLs with base URL
#     full_url = urljoin(base_url, link)
    
#     # Check if the URL is valid
#     if not is_valid_url(full_url):
#         return None
        
#     # Make sure we're staying on the same domain
#     base_domain = urlparse(base_url).netloc
#     link_domain = urlparse(full_url).netloc
    
#     if base_domain != link_domain:
#         return None
        
#     return full_url

# # Search manufacturers on Google with pagination
# def search_manufacturers(query, num_results=10):
#     manufacturer_list = []
#     start = 0
#     while len(manufacturer_list) < num_results:
#         params = {
#             "engine": "google",
#             "q": query,
#             "api_key": SERPAPI_KEY,
#             "num": min(10, num_results - len(manufacturer_list)),
#             "start": start
#         }
#         response = GoogleSearch(params).get_dict()
        
#         for result in response.get("organic_results", []):
#             title = result.get("title", "N/A")
#             link = result.get("link", "")
#             manufacturer_list.append((title, link))
        
#         if not response.get("organic_results"):
#             break  # Stop if there are no more results
        
#         start += 10
    
#     return manufacturer_list

# # Function to find emails on a page
# def extract_emails(url):
#     try:
#         response = requests.get(url, timeout=10)
#         emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", response.text)
#         return list(set(emails))  # Remove duplicates
#     except Exception:
#         return []

# # Function to crawl a website and collect pages to check for emails
# def crawl_website(base_url, max_pages=20):
#     visited = set()
#     to_visit = {base_url}
#     found_emails = set()
#     pages_checked = 0
    
#     while to_visit and pages_checked < max_pages:
#         try:
#             current_url = to_visit.pop()
            
#             if current_url in visited:
#                 continue
                
#             visited.add(current_url)
#             pages_checked += 1
            
#             response = requests.get(current_url, timeout=10)
#             soup = BeautifulSoup(response.text, "html.parser")
            
#             # Extract emails from current page
#             page_emails = extract_emails(current_url)
#             found_emails.update(page_emails)
            
#             # If we have enough pages or found emails, stop crawling
#             if pages_checked >= max_pages or len(found_emails) > 5:
#                 break
                
#             # Find more links to crawl
#             for link in soup.find_all("a", href=True):
#                 href = link["href"]
#                 normalized_url = normalize_url(base_url, href)
                
#                 if normalized_url and normalized_url not in visited:
#                     # Prioritize contact pages
#                     if "contact" in normalized_url.lower():
#                         to_visit = {normalized_url} | to_visit  # Add to beginning
#                     else:
#                         to_visit.add(normalized_url)
                        
#             # Be nice to the server
#             time.sleep(1)
            
#         except Exception:
#             continue
    
#     return list(found_emails)

# # Function to find and prioritize the contact page
# def find_contact_pages(url):
#     contact_pages = []
#     try:
#         response = requests.get(url, timeout=10)
#         soup = BeautifulSoup(response.text, "html.parser")
        
#         for link in soup.find_all("a", href=True):
#             href = link.get("href")
#             link_text = link.text.lower()
            
#             # Check if the link is related to contact
#             contact_keywords = ["contact", "reach us", "get in touch", "email us", "about us"]
#             if any(keyword in link_text or keyword in href.lower() for keyword in contact_keywords):
#                 full_url = normalize_url(url, href)
#                 if full_url:
#                     contact_pages.append(full_url)
        
#         return contact_pages
#     except Exception:
#         return []

# # Scrape manufacturers and extract emails
# # Scrape manufacturers and extract one email per company
# def scrape_manufacturer_emails(search_query):
#     manufacturers = search_manufacturers(search_query, num_results=10)
#     results = []
    
#     for name, website in manufacturers:
#         company_email = None  # Store only one email

#         # First check contact pages
#         contact_pages = find_contact_pages(website)
#         for contact_page in contact_pages:
#             emails = extract_emails(contact_page)
#             if emails:
#                 company_email = emails[0]  # Take the first email found
#                 break  # Stop searching once an email is found

#         # If no emails found on contact pages, crawl the site
#         if not company_email:
#             site_emails = crawl_website(website, max_pages=15)
#             if site_emails:
#                 company_email = site_emails[0]  # Take the first email found
        
#         results.append({
#             "Company": name, 
#             "Website": website, 
#             "Email": company_email if company_email else "No email found"
#         })
    
#     return results


# # Generate outreach email
# def generate_email(client_company):
#     prompt = f"""
#     Generate a professional email for a manufacturer inquiry:
#     - Address it to the team at {client_company}.
#     - Introduce myself as {supplier_name}, representing {supplier_company}.
#     - Explain that our company specializes in supplying {supplied_materials}.
#     - Emphasize how our materials can benefit their manufacturing process.
#     - Maintain a formal and polite tone.
#     - Include my contact details: {supplier_website}, {supplier_contact}.

#     Subject: High-Quality {supplied_materials} for {client_company}

#     Dear {client_company} Team,

#     I hope this email finds you well. My name is {supplier_name}, and I represent {supplier_company}, a trusted supplier of {supplied_materials}. We understand the importance of high-quality raw materials in manufacturing and would love the opportunity to support your production needs.

#     I would appreciate the chance to discuss how our products can benefit your company. Please let me know a convenient time for a quick call.

#     Looking forward to your response.

#     Best regards,  
#     {supplier_name}  
#     {supplier_company}  
#     {supplier_website}  
#     {supplier_contact}
#     """
    
#     response = openai.ChatCompletion.create(
#         model="gpt-4",
#         messages=[
#             {"role": "system", "content": "You are a professional email writer."},
#             {"role": "user", "content": prompt}
#         ]
#     )
    
#     return response["choices"][0]["message"]["content"]

# # Run the tool
# query = input("Enter the type of manufacturers you want to target (e.g., 'electronics manufacturers USA'): ")
# manufacturer_emails = scrape_manufacturer_emails(query)

# emails = []
# for row in manufacturer_emails:
#     client_company = row["Company"]
#     email = row["Email"] if row["Email"] else "No email found"
    
#     if email != "No email found":
#         email_text = generate_email(client_company)
#     else:
#         email_text = "No valid email found"
    
#     emails.append({
#         "Company": client_company,
#         "Website": row["Website"],
#         "Email": email,
#         "Generated Email": email_text
#     })

# # Save results
# df = pd.DataFrame(emails)
# output_file = "manufacturers_with_emails.csv"
# df.to_csv(output_file, index=False)
# print(f"Personalized emails generated and saved to {output_file}")


# import smtplib
# import pandas as pd
# import re
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from getpass import getpass

# # Ask user for their email credentials
# sender_email = input("Enter your Gmail address: ")
# app_password = getpass("Enter your Gmail App Password: ")

# # Function to extract subject and body from the 'Generated Email' column
# def extract_subject_body(email_text):
#     subject_match = re.search(r"Subject:\s*(.+)", email_text)
#     subject = subject_match.group(1).strip() if subject_match else "Business Inquiry"

#     body = re.sub(r"Subject:\s*.+\n", "", email_text).strip()
#     return subject, body

# # Function to send email via SMTP
# def send_email(recipient_email, subject, body):
#     try:
#         msg = MIMEMultipart()
#         msg["From"] = sender_email
#         msg["To"] = recipient_email
#         msg["Subject"] = subject
#         msg.attach(MIMEText(body, "plain"))

#         # Connect to Gmail SMTP server
#         with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
#             server.login(sender_email, app_password)
#             server.sendmail(sender_email, recipient_email, msg.as_string())

#         print(f"✅ Email sent to {recipient_email}")

#     except Exception as e:
#         print(f"❌ Failed to send email to {recipient_email}: {str(e)}")

# # Load emails from CSV
# csv_file = "manufacturers_with_emails.csv"  # Ensure correct file path
# df = pd.read_csv(csv_file)

# # Loop through each row and send emails
# for _, row in df.iterrows():
#     recipient_email = row["Email"]
#     email_text = row["Generated Email"]

#     if pd.notna(recipient_email) and recipient_email != "No email found":
#         subject, body = extract_subject_body(email_text)
#         send_email(recipient_email, subject, body)
#     else:
#         print(f"⚠️ Skipping {row['Company']} (No valid email found)")

# print("✅ All emails have been processed.")


import streamlit as st
import requests
import re
import pandas as pd
import openai
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from serpapi import GoogleSearch
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Set up API Keys
SERPAPI_KEY = ""
OPENAI_API_KEY = ""
openai.api_key = OPENAI_API_KEY

st.title("📧 Automated Email Scraper & Sender for Manufacturers")

# User Inputs
supplier_name = st.text_input("Enter Your Name")
supplier_company = st.text_input("Enter Your Company Name")
supplier_website = st.text_input("Enter Your Website URL")
supplier_contact = st.text_input("Enter Your Contact Number")
supplied_materials = st.text_input("Enter the Type of Raw Materials You Supply")
query = st.text_input("Enter the type of manufacturers to target (e.g., 'electronics manufacturers USA')")

# Utility Functions
def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def normalize_url(base_url, link):
    if not link or link.startswith(("#", "mailto:", "tel:", "javascript:")):
        return None
    full_url = urljoin(base_url, link)
    return full_url if is_valid_url(full_url) else None

def search_manufacturers(query, num_results=10):
    manufacturer_list = []
    start = 0
    while len(manufacturer_list) < num_results:
        params = {"engine": "google", "q": query, "api_key": SERPAPI_KEY, "num": min(10, num_results - len(manufacturer_list)), "start": start}
        response = GoogleSearch(params).get_dict()
        for result in response.get("organic_results", []):
            manufacturer_list.append((result.get("title", "N/A"), result.get("link", "")))
        if not response.get("organic_results"):
            break
        start += 10
    return manufacturer_list

def extract_emails(url):
    try:
        response = requests.get(url, timeout=10)
        return list(set(re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", response.text)))
    except:
        return []

def find_contact_pages(url):
    contact_pages = []
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        for link in soup.find_all("a", href=True):
            href = link.get("href")
            if any(keyword in (link.text.lower() + href.lower()) for keyword in ["contact", "reach us", "get in touch", "email us"]):
                full_url = normalize_url(url, href)
                if full_url:
                    contact_pages.append(full_url)
    except:
        pass
    return contact_pages

def crawl_website(base_url, max_pages=20):
    visited, to_visit, found_emails = set(), {base_url}, set()
    pages_checked = 0
    while to_visit and pages_checked < max_pages:
        try:
            current_url = to_visit.pop()
            if current_url in visited:
                continue
            visited.add(current_url)
            pages_checked += 1
            found_emails.update(extract_emails(current_url))
            if len(found_emails) > 5:
                break
            response = requests.get(current_url, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            for link in soup.find_all("a", href=True):
                href = link["href"]
                normalized_url = normalize_url(base_url, href)
                if normalized_url and normalized_url not in visited:
                    to_visit.add(normalized_url)
            time.sleep(1)
        except:
            continue
    return list(found_emails)

def scrape_manufacturer_emails(query):
    manufacturers = search_manufacturers(query, num_results=10)
    results = []
    for name, website in manufacturers:
        contact_pages = find_contact_pages(website)
        company_email = next((extract_emails(page)[0] for page in contact_pages if extract_emails(page)), None)
        if not company_email:
            site_emails = crawl_website(website, max_pages=15)
            company_email = site_emails[0] if site_emails else None
        results.append({"Company": name, "Website": website, "Email": company_email if company_email else "No email found"})
    return results

def generate_email(client_company):
    prompt = f"""
#     Generate a professional email for a manufacturer inquiry:
#     - Address it to the team at {client_company}.
#     - Introduce myself as {supplier_name}, representing {supplier_company}.
#     - Explain that our company specializes in supplying {supplied_materials}.
#     - Emphasize how our materials can benefit their manufacturing process.
#     - Maintain a formal and polite tone.
#     - Include my contact details: {supplier_website}, {supplier_contact}.

#     Subject: High-Quality {supplied_materials} for {client_company}

#     Dear {client_company} Team,

#     I hope this email finds you well. My name is {supplier_name}, and I represent {supplier_company}, a trusted supplier of {supplied_materials}. We understand the importance of high-quality raw materials in manufacturing and would love the opportunity to support your production needs.

#     I would appreciate the chance to discuss how our products can benefit your company. Please let me know a convenient time for a quick call.

#     Looking forward to your response.

#     Best regards,  
#     {supplier_name}  
#     {supplier_company}  
#     {supplier_website}  
#     {supplier_contact}
#     """
    response = openai.ChatCompletion.create(model="gpt-4", messages=[{"role": "system", "content": "You are a professional email writer."}, {"role": "user", "content": prompt}])
    return response["choices"][0]["message"]["content"]

def send_email(sender_email, app_password, recipient_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg["From"], msg["To"], msg["Subject"] = sender_email, recipient_email, subject
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        return f"✅ Email sent to {recipient_email}"
    except Exception as e:
        return f"❌ Failed to send email to {recipient_email}: {str(e)}"

if st.button("Find Manufacturers & Extract Emails"):
    manufacturer_emails = scrape_manufacturer_emails(query)
    df = pd.DataFrame(manufacturer_emails)
    st.dataframe(df)
    df.to_csv("manufacturers_with_emails.csv", index=False)
    st.success("Scraped Data Saved!")

sender_email = st.text_input("Enter Your Gmail Address")
app_password = st.text_input("Enter Your Gmail App Password", type="password")
if st.button("Send Emails"):
    df = pd.read_csv("manufacturers_with_emails.csv")
    for _, row in df.iterrows():
        recipient_email, company = row["Email"], row["Company"]
        if recipient_email != "No email found":
            email_body = generate_email(company)
            subject = f"High-Quality {supplied_materials} for {company}"
            st.write(send_email(sender_email, app_password, recipient_email, subject, email_body))
st.success("✅ All emails have been processed.")


