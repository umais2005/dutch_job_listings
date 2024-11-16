import concurrent.futures
import requests
from bs4 import BeautifulSoup
import logging
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import concurrent
import logging

# Suppress logging from Selenium
logging.getLogger('WDM').setLevel(logging.NOTSET) 


def get_centrumtandzorg():

    url = "https://centrumtandzorg.nl/werken-bij/vacatures/"

    # Send a request to fetch the HTML content
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the section with class 'ct-jobs'
    ct_jobs_section = soup.find('section', class_='ct-jobs')

    # Extract all 'a' tags within this section
    links = ct_jobs_section.find_all('a')

    # Print each link's URL
    job_listings = []
    for link in links:
        job_url = link.get('href')
        
        # Send a request to fetch each job page's HTML content
        job_response = requests.get(job_url)
        job_soup = BeautifulSoup(job_response.text, 'html.parser')
        
        # Extract the header title
        job_listing_texts = []
        header_title = job_soup.find('div', class_='header-title-content')
        if header_title:
            title_text ="Functietitel: "+ header_title.h1.get_text(strip=True) if header_title.h1 else 'No title'
            location_and_type ="Locatie en soort:" + header_title.find('div', class_='brabo-content').get_text(strip=True) if header_title.find('div', class_='brabo-content') else 'No location/type info'
            
            job_listing_texts.extend([title_text, location_and_type])
        
        # Extract all text from 'detail-section ct-detail-text' divs
        detail_sections = job_soup.find_all('div', class_='detail-section ct-detail-text')
        for i, section in enumerate(detail_sections, start=1):
            section_text = section.get_text("\n",strip=True)
            # print(f"Detail Section {i}: {section_text}")
            job_listing_texts.append(section_text)
        job_listings.append({"job_url":link['href'], "job_listing":"\n".join(job_listing_texts)})
    

    print(f"Extracted {len(job_listings)} number of jobs from {url}")
    return job_listings
        
def get_mondzorggilde():
    url = "https://www.mondzorggilde.nl/werken-bij"

    # Send a request to fetch the HTML content
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # List to store all job details
    all_job_details = []
    job_listings = []

    # Find the main section with class "text"
    main_section = soup.find('section', class_='text')

    if main_section:
        # Find all primary job listing links within the main section
        primary_links = [a['href'] for a in main_section.select('.text__link a')]

        for primary_link in primary_links:
            # Visit each primary job listing URL to extract links in the vacancies section
            response = requests.get(primary_link)
            job_page_content = response.text
            job_soup = BeautifulSoup(job_page_content, 'html.parser')
            
            # Find the vacancies section and get all secondary links
            vacancies_section = job_soup.find('section', class_='text', id='vacancies')
            secondary_links = []
            if vacancies_section:
                secondary_links = [a['href'] for a in vacancies_section.find_all('a', href=True)]

            for secondary_link in secondary_links:
                # Visit each secondary job listing link to extract banner and description details
                response = requests.get(secondary_link)
                secondary_page_content = response.text
                secondary_soup = BeautifulSoup(secondary_page_content, 'html.parser')
                
                # Dictionary to store job details
                job_details = {
                    "job_location_and_type": "",
                    "job_description": ""
                }

                # Extract text from the banner section
                banner_section = secondary_soup.find('div', class_='banner__text h-100')
                if banner_section:
                    header = banner_section.find('h2')
                    body = banner_section.find('div', class_='banner__body')
                    if header:
                        job_details["job_location_and_type"] += header.get_text(strip=True) + "\n"
                    if body:
                        job_details["job_location_and_type"] += body.get_text(separator="\n", strip=True)

                # Extract text from the job description section
                description_section = secondary_soup.find('section', class_='text')
                if description_section:
                    text_body = description_section.find('div', class_='text__body')
                    if text_body:
                        job_details["job_description"] = text_body.get_text(separator="\n", strip=True)

                # Append job details to the list
                all_job_details.append(job_details)
                job_listing = job_details['job_location_and_type'] + job_details['job_description']
                job_listings.append({"job_url":secondary_link, "job_listing":job_listing})
    print(f"Extracted {len(job_listings)} number of jobs from {url}")
    
    return job_listings

def get_detandartsengroep():
    url = "https://detandartsengroep.recruitee.com/vacature-overzicht"

    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    job_listings = []
    # Define the container holding the vacancy listings
    vacancies = []
    job_urls = []
    for location_block in soup.find_all('div', class_='sc-ejdqvv-1 dwleVY'):
        # Iterate over each vacancy card within the location block
        for vacancy_card in location_block.find_all('div', class_='sc-6exb5d-3 gnPPfQ'):
            # Extract job title and link
            location_list = vacancy_card.find("li", attrs={"data-testid":"styled-location-list-item"})
            location_name = location_list.get_text(strip=True)
            job_link = vacancy_card.find('a', class_='sc-6exb5d-1 jnhAxL')
            job_title = job_link.get_text(strip=True)
            job_url = job_link['href'] if job_link else None
            # Add to vacancies list if the URL and location are found
            if job_url and location_name:
                vacancies.append({'title': job_title, 'location': location_name})
                job_urls.append("https://detandartsengroep.recruitee.com/" +job_url)
    # Print or process the list of vacancies
    # for vacancy in vacancies:
    #     print(f"Job Title: {vacancy['title']}, Location: {vacancy['location']}, URL: {vacancy['url']}")
    for link, vacancy in zip(job_urls, vacancies):
        response = requests.get(link)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the job description section
        description_div = soup.select_one("div.sc-1v95195-0.jscoSJ div div")
        
        # Check if the description_div exists and extract text
        if description_div:
            job_description = description_div.get_text(separator=" ", strip=True)
            vacancy['job_description'] = job_description
        else:
            vacancy['job_description'] = "Description not found"
        job_listing = f"""
    title: {vacancy['title']}
    location: {vacancy['location']}
    job_description: {vacancy['job_description']}
    """
        job_listings.append({"job_url":link,"job_listing":job_listing})
    print(f"Extracted {len(job_listings)} number of jobs from {url}")

    return job_listings
    # Print the dictionary of job descriptions
    # print(vacancies[-1])

def get_lassus():
    main_url = "https://lassustandartsen.easycruit.com/"


    # Initialize a list to store job listings
    job_listings = []

    # Send a GET request to fetch the HTML content
    response = requests.get(main_url)

    # Check if the request was successful
    if response.status_code == 200:
        html_content = response.text
        
        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all div elements with the class 'joblist' to extract links
        joblist_div = soup.find('div', class_='joblist')
        links = joblist_div.find_all('a', href=True)
        links = [main_url + link['href'] for link in links]
        # Extract links from 'joblist' divs
            # Find all 'a' tags within the 'joblist' div and get the href attribute
        for link in links:
            link_url = link
            print(link)
            # Access the link to fetch details (optional)
            detail_response = requests.get(link_url)
            if detail_response.status_code == 200:
                detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
                
                jd_appetizer_div = detail_soup.find('div', class_='jd-appetizer')
                job_title = jd_appetizer_div.find('h1').get_text(strip=True) if jd_appetizer_div and jd_appetizer_div.find('h1') else "N/A"
                
                # Extract text from 'twelve columns jd-details' div
                jd_details_div = detail_soup.find('div', class_='jd-description')
                jd_details_text = jd_details_div.get_text() if jd_details_div else "N/A"
                
                # Extract text from 'four columns jd-codelist' div
                jd_codelist_div = detail_soup.find('div', class_='four columns jd-codelist')
                jd_codelist_text = jd_codelist_div.get_text() if jd_codelist_div else "N/A"
                
                job_listing = f"""
                    {job_title}

                    {jd_codelist_text}

                    {jd_details_text}
                                    """
                # Append the data to job_listings
                job_listings.append({"job_url": link,"job_listing":job_listing} )
            else:
                print(f"Failed to retrieve details from {link_url}")
    else:
        print(f"Failed to retrieve content. Status code: {response.status_code}")
    print(f"Extracted {len(job_listings)} number of jobs from {main_url}")

    return job_listings

def get_puur():
    main_url = "https://puurmondzorg.nl/werken-bij/vacatures/"

    # Send a GET request to fetch the HTML content of the main page
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")

    # Initialize Chrome WebDriver
    driver = webdriver.Chrome(options=options)
    
    # List to store each job listing as a single string
    job_listings = []

    try:
        # Open the main URL
        driver.get(main_url)

        # Wait for job links to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'job-link'))
        )

        # Find all job links on the main page
        job_links = driver.find_elements(By.CLASS_NAME, 'job-link')
        
        for link in job_links:
            job_url = link.get_attribute('href')
            
            # Fetch the job page content using requests and BeautifulSoup
            job_response = requests.get(job_url)
            job_response.raise_for_status()
            
            job_soup = BeautifulSoup(job_response.text, 'html.parser')
            
            # Extract text from the specified div classes
            heading_div = job_soup.find('div', class_='single-job-heading-container')
            content_div = job_soup.find('div', class_='job-content-container relative-container')
            
            # Get the text content from these divs if they exist
            heading_text = heading_div.get_text(strip=True) if heading_div else ''
            content_text = content_div.get_text(strip=True) if content_div else ''
            
            # Combine all extracted text into one string
            job_listing = f"Titel en locatie: {heading_text}\ntaakomschrijving: {content_text}"
            
            # Append the combined text to the job_listings list
            job_listings.append({"job_url": job_url,"job_listing":job_listing})
    
    finally:
        # Close the Selenium driver
        driver.quit()
    print(f"Extracted {len(job_listings)} number of jobs from {main_url}")
    
    
    return job_listings

def get_freshtandartsen():
    try:
        main_url = "https://www.freshtandartsen.nl/vacatures/?functie&afstand&soort&longlat"
        response = requests.get(main_url)
        response.raise_for_status()
        # print(response.text)
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # List to store extracted links
        job_links = []
        
        # Find all divs with class "col-12 last"
        divs = soup.find_all('div', class_='col-12 last')
        
        # Loop through each div to find job_links
        for div in divs:
            # Find all anchor tags within the div
            anchor_tags = div.find_all('a')
            for tag in anchor_tags:
                link = tag.get('href')
                if link:  # Check if the link is not None
                    job_links.append(link)
        
        job_listings = []
        for job_link in job_links:
            # print(job_link)
            # job_link = "https://www.freshtandartsen.nl"+job_link
            # print(job_link)
            response = requests.get(job_link)
            response.raise_for_status()
            
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract text from div with class "functie"
            functie_div = soup.find('div', class_='functie')
            functie_text = functie_div.get_text(strip=True) if functie_div else 'N/A'
            
            # Extract text from div with class "locatie_uren"
            locatie_uren_div = soup.find('div', class_='locatie_uren')
            locatie_uren_text = locatie_uren_div.get_text(strip=True) if locatie_uren_div else 'N/A'
            
            # Extract text from all specified sections, ensuring section-single-vacatures is first
            sections_order = [
                'section-single-vacatures',  # Ensure this section comes first
                'section-wat-ga-je-doen', 
                'section-wie-ben-jij', 
                'section-wat-bieden-wij', 
            ]
            
            # Extract text from each section and store in an ordered format
            sections_text = []
            for section_class in sections_order:
                section = soup.find('section', class_=f'section {section_class}')
                section_text = section.get_text(strip=True) if section else 'N/A'
                sections_text.append(f"{section_text}")

            # Combine all extracted details into a single formatted string
            job_listing = (
                f"Functie: {functie_text}\n"
                f"Locatie/Uren: {locatie_uren_text}\n\n"
                "Job Details:\n" + "\n".join(sections_text)
            )
            job_listings.append({"job_url": job_link,"job_listing":job_listing})
    except Exception as e:
        print(e)
    print(f"Extracted {len(job_listings)} number of jobs from {main_url}")
    return job_listings

def get_dentalvacancies_eu():
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--no-sandbox")
    # Initialize Chrome WebDriver
    driver = webdriver.Chrome(options=options)  

    url = "https://careers.dentalvacancies.eu/colosseum-dental/search/?createNewAlert=false&q=&locationsearch=&optionsFacetsDD_shifttype=&optionsFacetsDD_customfield1=&optionsFacetsDD_city=&optionsFacetsDD_state="
    # Open the website
    driver.get(url)  

    job_links = []

    try:
        page_n = 2
        while True:
            # Wait until job elements are loaded
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr.data-row .jobTitle a"))
            )

            # Get all job links on the current page
            jobs_on_page = driver.find_elements(By.CSS_SELECTOR, "span.jobTitle.hidden-phone a")
            for job in jobs_on_page:
                job_links.append(job.get_attribute("href"))
            print(f"Collected job links: {len(job_links)}")

            # Check if there is a "Next" button to move to the next page
            next_button = driver.find_elements(By.CSS_SELECTOR, f"ul.pagination li a[title='Pagina {page_n}']")
            if next_button:
                next_button[0].click()
                print(f"Navigating to page {page_n}")
                time.sleep(2)  # Wait for the next page to load
                page_n += 1
            else:
                break  # No more pages

    finally:
        driver.quit()

    # Using requests and BeautifulSoup to extract job descriptions
    job_listings = []
    for link in job_links:
        try:
            response = requests.get(link)
            response.raise_for_status()  # Check if the request was successful
            
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract job description from div with class 'job'
            job_div = soup.find('div', class_='job')
            job_listing = ""
            if job_div:
                for element in job_div.find_all(['p', 'div'], recursive=False):  # Adjust tags as needed
                    text = element.get_text(strip=True)
                    if text:  # Avoid empty lines
                        job_listing += text + "\n\n"  # Double newline for better paragraph separation
                # job_listing = job_div.get_text(strip=True)
            else:
                job_listing = "No description available"
            
            # Store the job URL and description
            job_listings.append({"job_url": link,"job_listing":job_listing})
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch {link}: {e}")
        # break

    print(f"Total job descriptions collected: {len(job_listings)} from {url[:20]}")

    
    return job_listings

def get_werkenbijpda():
    main_url = "https://www.werkenbijpda.nl/vacatures/"
    options = Options()
    options.add_argument("--headless")  # Run headlessly
    driver = webdriver.Chrome(options=options)
    
    # Open the target URL
    driver.get(main_url)  # Replace with the actual URL

    job_links = []

    try:
        # Click "Load More Jobs" until all jobs are loaded
        while True:
            try:
                # Wait for the "Load More Jobs" button to be clickable
                load_more_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "load_more_jobs"))
                )
                # Click the "Load More Jobs" button
                driver.execute_script("arguments[0].click();", load_more_button)
                time.sleep(2)  # Wait for jobs to load
            except:
                # Exit the loop if the button is not found or clickable
                break

        # Parse the fully loaded page with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        job_links = []

        # Find all job links in the fully loaded page
        job_listings = soup.find("ul", class_="job_listings")
        if job_listings:
            for li in job_listings.find_all("li", class_="job_listing"):
                job_link = li.find("a", href=True)
                if job_link:
                    job_links.append(job_link['href'])
    finally:
        driver.quit()
                    
    job_listings = []
    for link in job_links:
        response = requests.get(link)
        response.raise_for_status()  # Check if the request was successful
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
    
    # Locate the only article tag and get all text within it
        job_listing = soup.article.get_text(separator=' ', strip=True)
        job_listings.append({"job_url": link,"job_listing":job_listing})
    
    print(f"Extracted {len(job_listings)} number of jobs from {main_url}")
    return job_listings

def get_omnios():
    url = "https://www.omnios.nl/vacatures"  # Replace with the actual URL

    # Send a request to the website
    response = requests.get(url)
    response.raise_for_status()  # Check if the request was successful

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the div with class 'entries'
    job_links = []
    entries_div = soup.find('div', class_='entries')
    if entries_div:
        # Loop through each article in the entries div
        for article in entries_div.find_all('article', class_='entry-card'):
            # Find the h2 tag within each article
            h2_tag = article.find('h2', class_='entry-title')
            if h2_tag:
                # Find the a tag within the h2 and get the href attribute
                link_tag = h2_tag.find('a', href=True)
                if link_tag:
                    job_link = link_tag['href']
                    job_links.append(job_link)
    job_listings = []
    for link in job_links:
        try:
            # Send a request to each job link
            response = requests.get(link)
            response.raise_for_status()  # Check if the request was successful

            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the first three divs where the class name contains both 'gb-container' and 'alignfull'
            gb_divs = soup.find_all(lambda tag: tag.name == "div" and "gb-container" in tag.get("class", []) and "alignfull" in tag.get("class", []))[:3]
            print(len(gb_divs))
            # Combine text from each of the found divs into a single string
            job_listing = "\n\n".join(gb_div.get_text(strip=True) for gb_div in gb_divs)

            # Append the combined string to job_listings
            job_listings.append({"job_url": link,"job_listing":job_listing})

        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch {link}: {e}")
    print(f"Extracted {len(job_listings)} number of jobs from {url}")
    
    return job_listings


def job_content_for_werkenbijdentalclinics(link):
    response = requests.get(link)
    response.raise_for_status()  # Check if request was successful
            
    soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the article content by its class
    article = soup.find("article")
    job_content = ""
            
    if article:
                # Extract headings and paragraphs
        for element in article.find_all(['h1', 'h2', 'h3', 'h4', 'p']):
            text = element.get_text(strip=True)
            if text:
                job_content += text + "\n\n"  # Newline after each heading or paragraph
                        
    # print("Job from {} scraped".format(link))
    # print(job_content)
    return job_content

def get_toportho():
    base_url = "https://www.toportho.nl/vacatures/page/"
    page_number = 1
    job_links = []
    job_listings = []
    while True:
        # Construct the URL for the current page
        url = f"{base_url}{page_number}/"
        print(f"Scraping page: {url}")

        # Make a request to the page
        response = requests.get(url)
        
        # Break if the page returns a 404 error
        if response.status_code == 404:
            print("No more pages found. Exiting.")
            break

        # Parse the page content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all header tags with class 'entry-header' and extract links
        headers = soup.find_all('header', class_='entry-header')
        for header in headers:
            link = header.find('a')
            if link and link.has_attr('href'):
                job_links.append(link['href'])
                print(f"Found job link: {link['href']}")
                try:
                    response = requests.get(link['href'])
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Find the article tag and initialize job content
                    article = soup.find('article')
                    job_listing = ""

                    if article:
                        # Find all headings and paragraphs in the article
                        for tag in article.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']):
                            text = tag.get_text(strip=True)
                            if text:
                                job_listing += text + "\n"  # Add newline after each tag's content
                    else:
                        job_listing = "No article content found."
                    # Append the job content to job listings
                    job_listings.append({"job_url": link['href'],"job_listing":job_listing})

                except requests.exceptions.RequestException as e:
                    print(f"Failed to fetch {link['href']}: {e}")
        # Increment the page number to go to the next page
        page_number += 1
    print(len(job_listings), f"Jobs listings scraped from {url}")

    return job_listings

def get_orthocenter():
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Path to your Chrome WebDriver

    # Initialize the WebDriver
    driver = webdriver.Chrome(options=options)

    # Step 1: Open the main page and collect all job links from `listing-item` divs
    url = "https://www.orthocenter.nl/vacatures/?_gl=1*nyuzxd*_up*MQ..&gclid=EAIaIQobChMI7cG2tP_iiAMVoLGDBx1uTy9fEAAYASAAEgL64PD_BwE"  # Replace with the actual URL
    driver.get(url)
    time.sleep(2)  # Allow some time for the page to load

    # Collect all job links from listing-item divs
    job_links = []
    listings = driver.find_elements(By.CSS_SELECTOR, "div.listing-item a")
    for listing in listings:
        link = listing.get_attribute("href")
        if link:
            job_links.append(link)
            print(f"Found job link: {link}")

    # Step 2: Visit each job link and scrape job details
    job_listings = []

    for job_url in job_links:
        try:
            driver.get(job_url)
            time.sleep(2)  # Allow some time for the job page to load

            # Find and store the job title from the h1 tag
            # Locate the entry-content-section div
            content_section = driver.find_element(By.CLASS_NAME, 'entry-content-section')

            widget_vacatures_info = driver.find_element(By.CLASS_NAME, 'widget-vacatures-info.sidebar-section-box')
    
            # Find the ul within this div and get all li elements inside it
            list_items = widget_vacatures_info.find_elements(By.TAG_NAME, 'li')
            
            # Extract and concatenate the text from each list item
            vacatures_info_text = "\n".join([item.text.strip() for item in list_items if item.text.strip()])
            # Get text from the two specific divs inside entry-content-section
            vacatures_info = content_section.find_element(By.CLASS_NAME, 'vacatures-information')
            vacatures_text = vacatures_info.text.strip() if vacatures_info else "No vacatures info found"
            
            wp_content_wrapper = content_section.find_element(By.CLASS_NAME, 'wpb-content-wrapper')
            wp_content_text = wp_content_wrapper.text.strip() if wp_content_wrapper else "No wp content found"

            # Concatenate job details into a single listing
            job_listing = f"Vacature details:\n{vacatures_info_text}\n\n{wp_content_text}\n"
            job_listings.append({"job_url": job_url,"job_listing":job_listing})
            print(f"Scraped content from {job_url}")
    
        except Exception as e:
            print(f"Failed to fetch content from {job_url}: {e}")

    # Close the WebDriver
    driver.quit()
    print(f"Extracted {len(job_listings)} number of jobs from {url}")

    return job_listings

def get_werkenbijdentalclinics(check_duplicates=True):
    
    if check_duplicates:
        from rewrite import JobListingProcessor
        job_processor = JobListingProcessor(use_for_existience_check=True)
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=options)
    url = "https://www.werkenbijdentalclinics.nl/?tax_query%5B1%5D%5Btaxonomy%5D=category&tax_query%5B1%5D%5Bterms%5D=&tax_query%5B2%5D%5Btaxonomy%5D=worklocation&tax_query%5B2%5D%5Bterms%5D=&tax_query%5B3%5D%5Btaxonomy%5D=region&tax_query%5B3%5D%5Bterms%5D=&s=&allowedMeta=YTowOnt9&allowedTaxonomies=YTozOntpOjA7czo4OiJjYXRlZ29yeSI7aToxO3M6MTI6Indvcmtsb2NhdGlvbiI7aToyO3M6NjoicmVnaW9uIjt9&allowedPostType=czo0OiJwb3N0Ijs%3D&posttype=post"
    driver.get(url)
    job_links = []
    job_listings = []
    page_number = 1

    try:
        try:
            cookie_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyButtonAccept"))
            )
            cookie_button.click()
        except:
            print("No cookie dialog found or it could not be closed.")

        while True:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div#content article h2.entry-title a"))
            )
            articles = driver.find_elements(By.CSS_SELECTOR, "div#content article h2.entry-title a")
            for article in articles:
                link = article.get_attribute("href")
                if check_duplicates:
                    is_processed_in_wp, is_processed_in_manatal = job_processor.is_job_processed(link)
                    if is_processed_in_wp and is_processed_in_manatal:
                        print(f"Skipping already processed link: {link}")
                        continue
                job_links.append(link)

            print(f"Page {page_number} has {len(articles)} jobs.")
            page_number += 1
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.LINK_TEXT, str(page_number)))
                )
                next_button.click()
            except:
                break

        # Concurrently process job links
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(job_content_for_werkenbijdentalclinics, job_links))

        job_listings = [{"job_url": link, "job_listing": result} for link, result in zip(job_links, results) if result]
    except Exception as e:
        print("Error in scraping:", type(e))
    finally:
        driver.quit()

    return job_listings


if __name__ == "__main__":
    start_time = time.time()  # Record the start time

    # listings = get_lassus()
    # listings = get_puur()
    # listings = get_dentalvacancies_eu()
    # listings = get_werkenbijpda()
    # listings = get_omnios()
    listings = get_werkenbijdentalclinics(check_duplicates=False)
    # listings = get_werkenbijdentalclinics()
    # listings = get_toportho()
    # listings = get_orthocenter()

    end_time = time.time()  # Record the end time

    # Calculate and print the elapsed time
    elapsed_time = end_time - start_time
    print(f"Execution Time: {elapsed_time:.2f} seconds")

    # Output results
    print(len(listings))
    if listings:
        print(listings[0])
