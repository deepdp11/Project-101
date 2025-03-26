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

# Set page configuration
st.set_page_config(
    page_title="Manufacturer Outreach",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    /* Accessible Color Palette */
    :root {
        --primary-color: #2C3E50;      /* Deep Navy Blue */
        --secondary-color: #3498DB;    /* Bright Blue */
        --accent-color: #27AE60;       /* Vibrant Green */
        --background-light: #F5F7FA;   /* Soft Light Gray */
        --text-primary: #2C3E50;       /* Dark Navy for Text */
        --text-secondary: #34495E;     /* Slightly Lighter Navy */
        --white: #FFFFFF;
        --soft-shadow: rgba(0, 0, 0, 0.1);
    }

    /* Global Redesign for Readability */
    body {
        font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
        background-color: var(--background-light);
        color: var(--text-primary);
    }

    .main .block-container {
        background: var(--white);
        border-radius: 16px;
        box-shadow: 
            0 10px 30px var(--soft-shadow), 
            0 5px 15px rgba(0, 0, 0, 0.05);
        padding: 2rem;
    }

    /* Button Design */
    .stButton button {
        background-color: var(--primary-color);
        color: var(--white);
        border: none;
        border-radius: 12px;
        height: 3.5rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 10px rgba(44, 62, 80, 0.2);
    }

    .stButton button:hover {
        background-color: var(--secondary-color);
        transform: translateY(-3px);
        box-shadow: 0 6px 15px rgba(52, 152, 219, 0.3);
    }

    /* Input Fields */
    .stTextInput input, 
    .stTextArea textarea {
        border-radius: 10px;
        border: 1.5px solid #E0E4E8;
        background: var(--white);
        color: var(--text-primary);
        transition: all 0.3s ease;
    }

    .stTextInput input:focus, 
    .stTextArea textarea:focus {
        border-color: var(--secondary-color);
        box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
        outline: none;
    }

    /* Headings */
    h1 {
        color: var(--primary-color);
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 1.5rem;
    }

    h2 {
        color: var(--text-secondary);
        font-size: 1.8rem !important;
        font-weight: 600 !important;
        margin-bottom: 1rem;
        border-bottom: 3px solid var(--secondary-color);
        padding-bottom: 10px;
    }

    /* Information Boxes */
    .info-box {
        background-color: #EBF5FB;
        color: var(--text-secondary);
        border-radius: 12px;
        border-left: 5px solid var(--secondary-color);
        padding: 15px;
        margin-bottom: 20px;
    }

    .success-message {
        background-color: #D5F5E3;
        color: #2E8B57;
        border-radius: 12px;
        border-left: 5px solid var(--accent-color);
        padding: 15px;
    }

    .error-message {
        background-color: #FDEDEC;
        color: #C0392B;
        border-radius: 12px;
        border-left: 5px solid #E74C3C;
        padding: 15px;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: var(--background-light);
        border-radius: 12px;
        padding: 5px;
    }

    .stTabs [data-baseweb="tab"] {
        color: var(--text-secondary);
        transition: all 0.3s ease;
    }

    .stTabs [data-baseweb="tab-selected"] {
        background-color: var(--primary-color);
        color: var(--white) !important;
        border-radius: 10px;
    }

    /* Dataframe */
    .stDataFrame {
        border-radius: 12px;
        border: 1px solid #E0E4E8;
        box-shadow: 0 4px 10px var(--soft-shadow);
    }

    /* Section Divider */
    .section-divider {
        border-top: 2px solid #E0E4E8;
        margin: 2rem 0;
    }

    /* Ensure Text Visibility */
    * {
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
</style>
""", unsafe_allow_html=True)

# Set up API Keys
SERPAPI_KEY = st.secrets["SERPAPI_KEY"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
openai.api_key = OPENAI_API_KEY

# App Header
st.title("📧 Manufacturer Outreach Automation")
st.markdown("""
<div class="info-box">
This tool helps you find manufacturers, extract their contact emails, and send personalized outreach messages - all in one streamlined workflow.
</div>
""", unsafe_allow_html=True)

# Create tabs for better organization
tab1, tab2, tab3 = st.tabs(["📝 Your Information", "🔍 Find Manufacturers", "📨 Send Emails"])

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
    with st.spinner("🔍 Searching for manufacturers and extracting emails... This may take a few minutes."):
        progress_bar = st.progress(0)
        manufacturers = search_manufacturers(query, num_results=10)
        results = []
        
        for i, (name, website) in enumerate(manufacturers):
            progress_text = st.empty()
            progress_text.markdown(f"Processing: **{name}** ({i+1}/{len(manufacturers)})")
            
            contact_pages = find_contact_pages(website)
            company_email = next((extract_emails(page)[0] for page in contact_pages if extract_emails(page)), None)
            if not company_email:
                site_emails = crawl_website(website, max_pages=15)
                company_email = site_emails[0] if site_emails else None
            
            results.append({
                "Company": name, 
                "Website": website, 
                "Email": company_email if company_email else "No email found"
            })
            
            progress_bar.progress((i + 1) / len(manufacturers))
        
        progress_text.empty()
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

# Initialize session state for storing data between tabs
if 'supplier_info_complete' not in st.session_state:
    st.session_state.supplier_info_complete = False
if 'manufacturers_found' not in st.session_state:
    st.session_state.manufacturers_found = False
if 'df' not in st.session_state:
    st.session_state.df = None

# Tab 1: Your Information
with tab1:
    st.header("Your Business Information")
    
    col1, col2 = st.columns(2)
    with col1:
        supplier_name = st.text_input("Your Name", help="Enter your full name as it will appear in emails")
        supplier_company = st.text_input("Company Name", help="Enter your company's full name")
        supplier_contact = st.text_input("Contact Number", help="Enter your business phone number")
    
    with col2:
        supplier_website = st.text_input("Website URL", help="Enter your complete website URL including https://")
        supplied_materials = st.text_input("Materials You Supply", help="Specify the raw materials or products you offer")
    
    if st.button("Save Information"):
        if supplier_name and supplier_company and supplier_website and supplier_contact and supplied_materials:
            st.session_state.supplier_info_complete = True
            st.markdown('<div class="success-message">✅ Your information has been saved. You can now proceed to the next tab.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="error-message">❌ Please fill in all fields to continue.</div>', unsafe_allow_html=True)

# Tab 2: Find Manufacturers
with tab2:
    st.header("Find Potential Clients")
    
    if not st.session_state.supplier_info_complete:
        st.warning("⚠️ Please complete your business information in the previous tab first.")
    else:
        query = st.text_input("Target Manufacturers", placeholder="e.g., electronics manufacturers USA, automotive parts suppliers", help="Specify the type of manufacturers you want to target")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            search_button = st.button("🔍 Find Manufacturers & Extract Emails")
        
        if search_button and query:
            manufacturer_emails = scrape_manufacturer_emails(query)
            df = pd.DataFrame(manufacturer_emails)
            
            # Style the dataframe
            st.subheader(f"📋 Found {len(df)} Potential Clients")
            styled_df = df.style.apply(lambda x: ['background-color: #f0f8ff' if x.name % 2 == 0 else '' for i in x], axis=1)
            st.dataframe(styled_df, use_container_width=True)
            
            # Save to session state and file
            st.session_state.df = df
            df.to_csv("manufacturers_with_emails.csv", index=False)
            st.session_state.manufacturers_found = True
            st.markdown('<div class="success-message">✅ Manufacturer data has been saved. You can now proceed to sending emails.</div>', unsafe_allow_html=True)
            
            # Add download button
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name="manufacturers_with_emails.csv",
                mime="text/csv",
            )

# Tab 3: Send Emails
with tab3:
    st.header("Send Outreach Emails")
    
    if not st.session_state.manufacturers_found:
        st.warning("⚠️ Please find manufacturers in the previous tab first.")
    else:
        st.subheader("Email Configuration")
        
        col1, col2 = st.columns(2)
        with col1:
            sender_email = st.text_input("Your Gmail Address", help="Enter the Gmail address you'll use to send emails")
        with col2:
            app_password = st.text_input("Gmail App Password", type="password", help="Enter your Gmail app password (not your regular Gmail password)")
        
        st.markdown("""
        <div class="info-box">
        ℹ️ <strong>Note:</strong> You need to set up an <a href="https://support.google.com/accounts/answer/185833" target="_blank">App Password</a> in your Google Account for this application to send emails securely.
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.df is not None:
            st.subheader("Preview Recipients")
            st.dataframe(st.session_state.df[["Company", "Email"]], use_container_width=True)
            
            # Sample email preview
            st.subheader("Sample Email Preview")
            if st.session_state.df.iloc[0]["Email"] != "No email found":
                sample_company = st.session_state.df.iloc[0]["Company"]
                sample_email = generate_email(sample_company)
                st.text_area("Email Preview", sample_email, height=300, disabled=True)
            
            valid_emails = st.session_state.df[st.session_state.df["Email"] != "No email found"]
            
            col1, col2 = st.columns([3, 1])
            with col1:
                send_button = st.button("📨 Send Emails to All Valid Recipients")
            
            if send_button:
                if sender_email and app_password:
                    with st.spinner("📨 Sending emails..."):
                        results = []
                        progress_bar = st.progress(0)
                        
                        for i, (_, row) in enumerate(valid_emails.iterrows()):
                            recipient_email, company = row["Email"], row["Company"]
                            if recipient_email != "No email found":
                                email_body = generate_email(company)
                                subject = f"High-Quality {supplied_materials} for {company}"
                                result = send_email(sender_email, app_password, recipient_email, subject, email_body)
                                results.append(result)
                                progress_bar.progress((i + 1) / len(valid_emails))
                        
                        # Display results
                        st.markdown(f"<div class='success-message'>✅ Sent {sum('✅' in r for r in results)} of {len(results)} emails successfully</div>", unsafe_allow_html=True)
                        for result in results:
                            if "✅" in result:
                                st.success(result)
                            else:
                                st.error(result)
                else:
                    st.markdown("<div class='error-message'>❌ Please enter your Gmail address and app password.</div>", unsafe_allow_html=True)

# Footer
st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
st.markdown("### 🔒 Privacy Note")
st.markdown("""
<div class="info-box">
Your data and API keys are securely stored and are not shared with any third parties. Emails are sent directly from your Gmail account.
</div>
""", unsafe_allow_html=True)

