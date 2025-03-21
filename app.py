# import streamlit as st
# import requests
# import re
# import pandas as pd
# import openai
# import time
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin, urlparse
# from serpapi import GoogleSearch
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart

# # Set up API Keys
# SERPAPI_KEY = st.secrets["SERPAPI_KEY"]
# OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
# openai.api_key = OPENAI_API_KEY

# st.title("📧 Automated Email Scraper & Sender for Manufacturers")

# # User Inputs
# supplier_name = st.text_input("Enter Your Name")
# supplier_company = st.text_input("Enter Your Company Name")
# supplier_website = st.text_input("Enter Your Website URL")
# supplier_contact = st.text_input("Enter Your Contact Number")
# supplied_materials = st.text_input("Enter the Type of Raw Materials You Supply")
# query = st.text_input("Enter the type of manufacturers to target (e.g., 'electronics manufacturers USA')")

# # Utility Functions
# def is_valid_url(url):
#     parsed = urlparse(url)
#     return bool(parsed.netloc) and bool(parsed.scheme)

# def normalize_url(base_url, link):
#     if not link or link.startswith(("#", "mailto:", "tel:", "javascript:")):
#         return None
#     full_url = urljoin(base_url, link)
#     return full_url if is_valid_url(full_url) else None

# def search_manufacturers(query, num_results=10):
#     manufacturer_list = []
#     start = 0
#     while len(manufacturer_list) < num_results:
#         params = {"engine": "google", "q": query, "api_key": SERPAPI_KEY, "num": min(10, num_results - len(manufacturer_list)), "start": start}
#         response = GoogleSearch(params).get_dict()
#         for result in response.get("organic_results", []):
#             manufacturer_list.append((result.get("title", "N/A"), result.get("link", "")))
#         if not response.get("organic_results"):
#             break
#         start += 10
#     return manufacturer_list

# def extract_emails(url):
#     try:
#         response = requests.get(url, timeout=10)
#         return list(set(re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", response.text)))
#     except:
#         return []

# def find_contact_pages(url):
#     contact_pages = []
#     try:
#         response = requests.get(url, timeout=10)
#         soup = BeautifulSoup(response.text, "html.parser")
#         for link in soup.find_all("a", href=True):
#             href = link.get("href")
#             if any(keyword in (link.text.lower() + href.lower()) for keyword in ["contact", "reach us", "get in touch", "email us"]):
#                 full_url = normalize_url(url, href)
#                 if full_url:
#                     contact_pages.append(full_url)
#     except:
#         pass
#     return contact_pages

# def crawl_website(base_url, max_pages=20):
#     visited, to_visit, found_emails = set(), {base_url}, set()
#     pages_checked = 0
#     while to_visit and pages_checked < max_pages:
#         try:
#             current_url = to_visit.pop()
#             if current_url in visited:
#                 continue
#             visited.add(current_url)
#             pages_checked += 1
#             found_emails.update(extract_emails(current_url))
#             if len(found_emails) > 5:
#                 break
#             response = requests.get(current_url, timeout=10)
#             soup = BeautifulSoup(response.text, "html.parser")
#             for link in soup.find_all("a", href=True):
#                 href = link["href"]
#                 normalized_url = normalize_url(base_url, href)
#                 if normalized_url and normalized_url not in visited:
#                     to_visit.add(normalized_url)
#             time.sleep(1)
#         except:
#             continue
#     return list(found_emails)

# def scrape_manufacturer_emails(query):
#     manufacturers = search_manufacturers(query, num_results=10)
#     results = []
#     for name, website in manufacturers:
#         contact_pages = find_contact_pages(website)
#         company_email = next((extract_emails(page)[0] for page in contact_pages if extract_emails(page)), None)
#         if not company_email:
#             site_emails = crawl_website(website, max_pages=15)
#             company_email = site_emails[0] if site_emails else None
#         results.append({"Company": name, "Website": website, "Email": company_email if company_email else "No email found"})
#     return results

# def generate_email(client_company):
#     prompt = f"""
# #     Generate a professional email for a manufacturer inquiry:
# #     - Address it to the team at {client_company}.
# #     - Introduce myself as {supplier_name}, representing {supplier_company}.
# #     - Explain that our company specializes in supplying {supplied_materials}.
# #     - Emphasize how our materials can benefit their manufacturing process.
# #     - Maintain a formal and polite tone.
# #     - Include my contact details: {supplier_website}, {supplier_contact}.

# #     Subject: High-Quality {supplied_materials} for {client_company}

# #     Dear {client_company} Team,

# #     I hope this email finds you well. My name is {supplier_name}, and I represent {supplier_company}, a trusted supplier of {supplied_materials}. We understand the importance of high-quality raw materials in manufacturing and would love the opportunity to support your production needs.

# #     I would appreciate the chance to discuss how our products can benefit your company. Please let me know a convenient time for a quick call.

# #     Looking forward to your response.

# #     Best regards,  
# #     {supplier_name}  
# #     {supplier_company}  
# #     {supplier_website}  
# #     {supplier_contact}
# #     """
#     response = openai.ChatCompletion.create(model="gpt-4", messages=[{"role": "system", "content": "You are a professional email writer."}, {"role": "user", "content": prompt}])
#     return response["choices"][0]["message"]["content"]

# def send_email(sender_email, app_password, recipient_email, subject, body):
#     try:
#         msg = MIMEMultipart()
#         msg["From"], msg["To"], msg["Subject"] = sender_email, recipient_email, subject
#         msg.attach(MIMEText(body, "plain"))
#         with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
#             server.login(sender_email, app_password)
#             server.sendmail(sender_email, recipient_email, msg.as_string())
#         return f"✅ Email sent to {recipient_email}"
#     except Exception as e:
#         return f"❌ Failed to send email to {recipient_email}: {str(e)}"

# if st.button("Find Manufacturers & Extract Emails"):
#     manufacturer_emails = scrape_manufacturer_emails(query)
#     df = pd.DataFrame(manufacturer_emails)
#     st.dataframe(df)
#     df.to_csv("manufacturers_with_emails.csv", index=False)
#     st.success("Scraped Data Saved!")

# sender_email = st.text_input("Enter Your Gmail Address")
# app_password = st.text_input("Enter Your Gmail App Password", type="password")
# if st.button("Send Emails"):
#     df = pd.read_csv("manufacturers_with_emails.csv")
#     for _, row in df.iterrows():
#         recipient_email, company = row["Email"], row["Company"]
#         if recipient_email != "No email found":
#             email_body = generate_email(company)
#             subject = f"High-Quality {supplied_materials} for {company}"
#             st.write(send_email(sender_email, app_password, recipient_email, subject, email_body))
#             st.success("✅ All emails have been processed.")

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

# Page configuration
st.set_page_config(
    page_title="Manufacturer Email Scraper",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS to make the UI more modern
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 10px 24px;
        font-size: 16px;
        transition-duration: 0.4s;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    h1, h2, h3 {
        color: #1E3A8A;
    }
    .highlight {
        background-color: #f0f8ff;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin-bottom: 20px;
    }
    .success-message {
        background-color: #DFF0D8;
        color: #3C763D;
        padding: 10px;
        border-radius: 4px;
        margin-bottom: 10px;
    }
    .error-message {
        background-color: #F2DEDE;
        color: #A94442;
        padding: 10px;
        border-radius: 4px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Set up API Keys
SERPAPI_KEY = st.secrets["SERPAPI_KEY"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
openai.api_key = OPENAI_API_KEY

# App header with logo and title
col1, col2 = st.columns([1, 5])
with col1:
    st.markdown("# 📧")
with col2:
    st.markdown("# Automated Email Scraper & Sender")
    st.markdown("#### Connect with manufacturers efficiently")

# Create tabs for different sections
tab1, tab2, tab3 = st.tabs(["Your Information", "Find Manufacturers", "Send Emails"])

# Utility Functions (unchanged)
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
    with st.spinner("Searching for manufacturers..."):
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
    progress_bar = st.progress(0)
    
    for i, (name, website) in enumerate(manufacturers):
        st.markdown(f"Processing: **{name}**")
        contact_pages = find_contact_pages(website)
        company_email = next((extract_emails(page)[0] for page in contact_pages if extract_emails(page)), None)
        if not company_email:
            site_emails = crawl_website(website, max_pages=15)
            company_email = site_emails[0] if site_emails else None
        results.append({"Company": name, "Website": website, "Email": company_email if company_email else "No email found"})
        progress_bar.progress((i + 1) / len(manufacturers))
    
    progress_bar.empty()
    return results

def generate_email(client_company):
    prompt = f"""
    Generate a professional email for a manufacturer inquiry:
    - Address it to the team at {client_company}.
    - Introduce myself as {supplier_name}, representing {supplier_company}.
    - Explain that our company specializes in supplying {supplied_materials}.
    - Emphasize how our materials can benefit their manufacturing process.
    - Maintain a formal and polite tone.
    - Include my contact details: {supplier_website}, {supplier_contact}.

    Subject: High-Quality {supplied_materials} for {client_company}

    Dear {client_company} Team,

    I hope this email finds you well. My name is {supplier_name}, and I represent {supplier_company}, a trusted supplier of {supplied_materials}. We understand the importance of high-quality raw materials in manufacturing and would love the opportunity to support your production needs.

    I would appreciate the chance to discuss how our products can benefit your company. Please let me know a convenient time for a quick call.

    Looking forward to your response.

    Best regards,  
    {supplier_name}  
    {supplier_company}  
    {supplier_website}  
    {supplier_contact}
    """
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

# Tab 1: User Information
with tab1:
    st.markdown("""
    <div class="highlight">
        <h3>Your Information</h3>
        <p>Enter your details below to personalize outreach emails to manufacturers.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        supplier_name = st.text_input("Your Name", placeholder="John Doe")
        supplier_company = st.text_input("Your Company Name", placeholder="Materials Inc.")
    with col2:
        supplier_website = st.text_input("Your Website URL", placeholder="https://example.com")
        supplier_contact = st.text_input("Your Contact Number", placeholder="+1 (123) 456-7890")
    
    supplied_materials = st.text_input("Type of Raw Materials You Supply", placeholder="Metal alloys, plastics, electronic components...")
    
    if all([supplier_name, supplier_company, supplier_website, supplier_contact, supplied_materials]):
        st.success("Information complete! You can now proceed to the 'Find Manufacturers' tab.")
    
# Tab 2: Find Manufacturers
with tab2:
    st.markdown("""
    <div class="highlight">
        <h3>Find Manufacturers</h3>
        <p>Search for manufacturers and extract their contact information.</p>
    </div>
    """, unsafe_allow_html=True)
    
    query = st.text_input("Type of manufacturers to target", placeholder="electronics manufacturers USA")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        find_button = st.button("Find Manufacturers", use_container_width=True)
    
    if find_button:
        if not query:
            st.error("Please enter a search query.")
        else:
            with st.spinner("Looking for manufacturers and extracting emails..."):
                manufacturer_emails = scrape_manufacturer_emails(query)
                df = pd.DataFrame(manufacturer_emails)
                
                # Style the dataframe
                st.markdown("### Results")
                st.dataframe(
                    df.style.apply(
                        lambda x: ['background-color: #f0f8ff' if x.name % 2 == 0 else 'background-color: white' for i in range(len(x))], 
                        axis=1
                    ),
                    use_container_width=True,
                    height=400
                )
                
                # Save data
                df.to_csv("manufacturers_with_emails.csv", index=False)
                
                # Count results
                total_emails = len(df[df["Email"] != "No email found"])
                
                # Success message
                st.markdown(f"""
                <div class="success-message">
                    <h4>✅ Data scraped and saved successfully!</h4>
                    <p>Found {len(df)} manufacturers, {total_emails} with valid emails.</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Download button
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="manufacturers_with_emails.csv",
                    mime="text/csv",
                )

# Tab 3: Send Emails
with tab3:
    st.markdown("""
    <div class="highlight">
        <h3>Send Emails</h3>
        <p>Send personalized outreach emails to the manufacturers you found.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        sender_email = st.text_input("Your Gmail Address", placeholder="your.email@gmail.com")
    with col2:
        app_password = st.text_input("Your Gmail App Password", type="password", 
                                    help="This is an app-specific password. Create one at myaccount.google.com/security")
    
    # Display preview if data exists
    try:
        df = pd.read_csv("manufacturers_with_emails.csv")
        st.markdown("### Manufacturer Data")
        st.dataframe(
            df.style.apply(
                lambda x: ['background-color: #f0f8ff' if x.name % 2 == 0 else 'background-color: white' for i in range(len(x))], 
                axis=1
            ),
            use_container_width=True,
            height=200
        )
        
        # Show preview
        if st.checkbox("Show email preview"):
            preview_company = st.selectbox("Select a company for email preview", df["Company"].tolist())
            if preview_company:
                with st.spinner("Generating preview..."):
                    preview_email = generate_email(preview_company)
                    st.code(preview_email, language="")
        
        # Send emails
        if st.button("Send Emails", use_container_width=True):
            if not sender_email or not app_password:
                st.error("Please enter your Gmail credentials.")
            else:
                emails_sent = 0
                emails_failed = 0
                progress_bar = st.progress(0)
                
                for i, row in df.iterrows():
                    recipient_email, company = row["Email"], row["Company"]
                    if recipient_email != "No email found":
                        with st.spinner(f"Sending email to {company}..."):
                            email_body = generate_email(company)
                            subject = f"High-Quality {supplied_materials} for {company}"
                            result = send_email(sender_email, app_password, recipient_email, subject, email_body)
                            
                            if "✅" in result:
                                emails_sent += 1
                            else:
                                emails_failed += 1
                            
                            st.write(result)
                    progress_bar.progress((i + 1) / len(df))
                
                progress_bar.empty()
                st.markdown(f"""
                <div class="success-message">
                    <h4>✅ Email campaign completed!</h4>
                    <p>Successfully sent: {emails_sent} emails<br>
                    Failed: {emails_failed} emails</p>
                </div>
                """, unsafe_allow_html=True)
                
    except FileNotFoundError:
        st.info("No manufacturer data available. Please go to the 'Find Manufacturers' tab first.")

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 30px; padding: 10px; border-top: 1px solid #ddd;">
    <p style="color: #666;">Automated Email Scraper & Sender for Manufacturers | © 2025</p>
</div>
""", unsafe_allow_html=True)
