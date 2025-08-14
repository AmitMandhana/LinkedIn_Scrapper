import requests
import re
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

# =====================================
# CONFIG
# =====================================
HUNTER_API_KEY = "9c2692425ad60022a20915635b38095f8d7436c3"  # <-- Put your Hunter.io API key here
SHEET_NAME = "Job Listings"  # Name of your Google Sheet
GOOGLE_CREDS_JSON = "C:\\Users\\BISHNU KANTA\\Desktop\\job\\google_drive.json"
  # Path to your Google API credentials JSON
JOB_KEYWORD = "Software Engineer"
JOB_LOCATION = "India"
MAX_JOBS = 5  # Limit jobs per site to avoid hitting free API limits
# =====================================

# Google Sheets setup
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDS_JSON, SCOPE)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

# Function to find emails using Hunter.io
def find_emails(domain):
    url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={HUNTER_API_KEY}"
    try:
        resp = requests.get(url).json()
        emails = resp.get("data", {}).get("emails", [])
        
        # Get HR/Recruiter email (first priority)
        hr_email = ""
        worker_email = ""
        
        for email in emails:
            position = email.get("position", "").lower()
            email_value = email.get("value", "")
            
            # Look for HR/recruiting related positions for HR email
            if any(role in position for role in ["hr", "recruit", "talent", "people", "human"]):
                hr_email = email_value
                if worker_email:  # If we already found a worker email, we can stop
                    break
            # Look for worker/employee emails
            elif any(role in position for role in ["engineer", "developer", "programmer", "staff", "employee", "worker"]):
                worker_email = email_value
                if hr_email:  # If we already found an HR email, we can stop
                    break
        
        # If no specific HR email found, use the first email as HR email
        if not hr_email and emails:
            hr_email = emails[0]["value"]
            
        # If no specific worker email found, use the second email as worker email if available
        if not worker_email and len(emails) > 1:
            worker_email = emails[1]["value"]
        
        return hr_email, worker_email
    except Exception as e:
        print(f"[!] Hunter API error: {e}")
    return "", ""

# Function to scrape LinkedIn
def scrape_indeed(keyword, location):
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException
    
    driver = webdriver.Chrome()
    # Using LinkedIn instead of Indeed
    search_url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}&location={location}"
    driver.get(search_url)
    
    jobs_data = []
    
    try:
        # Wait for job cards to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".job-search-card"))
        )
        
        # Get all job elements directly using Selenium
        job_elements = driver.find_elements(By.CSS_SELECTOR, ".job-search-card")[:MAX_JOBS]
        print(f"[DEBUG] Found {len(job_elements)} jobs on LinkedIn using Selenium")
        
        for job in job_elements:
            try:
                title_elem = job.find_element(By.CSS_SELECTOR, ".base-search-card__title")
                title = title_elem.text.strip()
                
                try:
                    company_elem = job.find_element(By.CSS_SELECTOR, ".base-search-card__subtitle")
                    company = company_elem.text.strip()
                except:
                    company = "Company not found"
                
                try:
                    loc_elem = job.find_element(By.CSS_SELECTOR, ".job-search-card__location")
                    loc = loc_elem.text.strip()
                except:
                    loc = "Location not found"
                
                try:
                    link_elem = job.find_element(By.CSS_SELECTOR, ".base-card__full-link")
                    link = link_elem.get_attribute("href")
                except:
                    link = "Link not found"
                
                # Try regex first
                email_match = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}", job.text)
                
                if email_match:
                    hr_email = email_match[0]
                    worker_email = email_match[1] if len(email_match) > 1 else ""
                else:
                    # Use Hunter.io to find both HR and worker emails
                    hr_email, worker_email = find_emails(company.replace(" ", "").lower() + ".com")
                
                jobs_data.append([title, company, loc, hr_email, worker_email, link])
                print(f"[DEBUG] Added job: {title} at {company}")
            except Exception as e:
                print(f"[DEBUG] Error parsing job: {e}")
                continue
    except TimeoutException:
        print("[DEBUG] Timeout waiting for LinkedIn job results to load")
    except Exception as e:
        print(f"[DEBUG] Error scraping LinkedIn: {e}")
    finally:
        driver.quit()
    
    return jobs_data

# Function to scrape Naukri
def scrape_naukri(keyword, location):
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException
    
    driver = webdriver.Chrome()
    url = f"https://www.naukri.com/{keyword.replace(' ', '-')}-jobs-in-{location.lower()}"
    driver.get(url)
    jobs_data = []
    
    try:
        # Wait for job cards to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "article.jobTuple, div.list"))
        )
        
        # Get all job elements directly using Selenium
        job_elements = driver.find_elements(By.CSS_SELECTOR, "article.jobTuple, div.list")[:MAX_JOBS]
        print(f"[DEBUG] Found {len(job_elements)} jobs on Naukri using Selenium")
        
        for job in job_elements:
            try:
                title_elem = job.find_element(By.CSS_SELECTOR, "a.title, a.jobTitle")
                title = title_elem.text.strip()
                
                try:
                    company_elem = job.find_element(By.CSS_SELECTOR, "a.subTitle, a.companyInfo")
                    company = company_elem.text.strip()
                except:
                    company = "Company not found"
                
                try:
                    loc_elem = job.find_element(By.CSS_SELECTOR, "li.location, span.location")
                    loc = loc_elem.text.strip()
                except:
                    loc = "Location not found"
                
                try:
                    link = title_elem.get_attribute("href")
                except:
                    link = "Link not found"
                
                # No direct email on Naukri → use Hunter.io to find both HR and worker emails
                hr_email, worker_email = find_emails(company.replace(" ", "").lower() + ".com")
                
                jobs_data.append([title, company, loc, hr_email, worker_email, link])
                print(f"[DEBUG] Added job: {title} at {company}")
            except Exception as e:
                print(f"[DEBUG] Error parsing job: {e}")
                continue
    except TimeoutException:
        print("[DEBUG] Timeout waiting for Naukri job results to load")
    except Exception as e:
        print(f"[DEBUG] Error scraping Naukri: {e}")
    finally:
        driver.quit()
        
    return jobs_data

# Push to Google Sheet
def update_google_sheet(data):
    sheet.clear()
    sheet.append_row(["Job Title", "Company", "Location", "HR Email", "Worker Email", "Job Link"])
    for row in data:
        sheet.append_row(row)

if __name__ == "__main__":
    print("[*] Scraping LinkedIn...")
    linkedin_jobs = scrape_indeed(JOB_KEYWORD, JOB_LOCATION)

    print("[*] Scraping Naukri...")
    naukri_jobs = scrape_naukri(JOB_KEYWORD, JOB_LOCATION)

    all_jobs = linkedin_jobs + naukri_jobs
    print(f"[+] Total jobs found: {len(all_jobs)}")

    update_google_sheet(all_jobs)
    print("✅ Google Sheet updated successfully!")
