from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import re
import hashlib
import os
import json
from prompts import to_html
from datetime import date



class JobListingProcessor:
    def __init__(self, rewrite_prompt, job_listing_json_prompt, html_prompt, model="llama3-70b-8192", temperature=0.2, test=False):
        self.api_key = os.getenv("OPEN_API_KEY") if not test else os.getenv("GROQ_API_KEY")
        self.model = model
        self.rewrite_prompt = rewrite_prompt
        self.job_listing_json_prompt = job_listing_json_prompt
        self.html_prompt = html_prompt
        self.temperature = temperature
        if test:
            self.llm = ChatGroq(model=self.model, temperature=self.temperature, api_key=self.api_key)
        else:
            self.llm = ChatOpenAI(api_key=self.api_key, model="gpt-4o", temperature=self.temperature)
        self.job_mapping_file_wp = "job_url_to_id_mapping_wp.json"
        self.job_mapping_file_manatal = "job_url_to_id_mapping_manatal.json"
        self.job_url_to_id_mapping_wp = self.load_job_url_to_id_mapping_wp()
        self.job_url_to_id_mapping_manatal = self.load_job_url_to_id_mapping_manatal()
        self.jobs_mapping = self.load_jobs_json()
        rewrite_prompt = PromptTemplate(input_variables=["job_listing"], template=self.rewrite_prompt)
        self.rewrite_chain = rewrite_prompt | self.llm
        mapping_prompt = PromptTemplate(input_variables=["job_listing"], template=self.job_listing_json_prompt)
        self.mapping_chain = mapping_prompt | self.llm
        job_to_html = PromptTemplate(input_variables=["text"], template=self.html_prompt)
        self.html_conversion_chain = job_to_html | self.llm

    def load_job_url_to_id_mapping_wp(self):
        """Load the job_url to job_id mapping from a JSON file if it exists."""
        if os.path.exists(self.job_mapping_file_wp):
            with open(self.job_mapping_file_wp, "r") as file:
                return json.load(file)
        return {}

    def save_job_url_to_id_mapping_wp(self):
        """Save the job_url to job_id mapping to a JSON file."""
        with open(self.job_mapping_file_wp, "w") as file:
            json.dump(self.job_url_to_id_mapping_wp, file)

    def load_job_url_to_id_mapping_manatal(self):
        """Load the job_url to job_id mapping from a JSON file if it exists."""
        if os.path.exists(self.job_mapping_file_manatal):
            with open(self.job_mapping_file_manatal, "r") as file:
                return json.load(file)
        return {}
    

    def save_job_url_to_id_mapping_manatal(self):
        """Save the job_url to job_id mapping to a JSON file."""
        with open(self.job_mapping_file_manatal, "w") as file:
            json.dump(self.job_url_to_id_mapping_wp, file)
    
    def load_jobs_json(self):
        """Load the job_url to job_id mapping from a JSON file if it exists."""
        if os.path.exists('jobs.json'):
            with open("jobs.json", "r") as file:
                return json.load(file)
        return {}
        
    def save_jobs_json(self):
        """save the job_url to job_id mapping from a JSON file if it exists."""
        with open("jobs.json", "w") as file:
            json.dump(self.jobs_mapping, file)
        
        # Initialize the LLM model as a class-bound attribute
        self.llm = ChatGroq(model=self.model, temperature=self.temperature, api_key=self.api_key)

    def process_job_listing(self, job_listing_content):
        """
        Rewrite the job listing, generate a JSON mapping, and return the rewritten listing and mapping as a dictionary.
        """
        # job_listing_content = job['job_listing']
        # Step 1: Generate a unique rewritten job listing
        

        # Step 2: Generate a JSON mapping for the new job listing
        timeout = 1
        while True:
            new_job_listing = self.rewrite_chain.invoke({"job_listing": job_listing_content}).content
            mapping_json_str = self.mapping_chain.invoke({"job_listing": new_job_listing}).content
            json_match = re.search(r"(\{.*\})", mapping_json_str, re.DOTALL)
            if json_match:
                json_string = json_match.group(1)
                json_string = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', json_string)  # Removes ASCII control characters
                json_string = json_string.replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")
                with open("mapping.txt", "w", encoding="utf-8") as m:
                    m.write(json_string)
                try:
                    # Clean up control characters if necessary
                    json_string = json.dumps(json.loads(json_string))  # Ensures valid JSON encoding
                    mapping_dict = json.loads(json_string)
                except Exception as e:
                    print(f" error: {e}")
                    # Handle the error, e.g., log it, reformat, or retry
                    if timeout == 5:
                        print("Timeout limit exceeded")
                        break
                    else:
                        print("REtrying")
                        timeout +=1
                else:
                    formatted_html = self.html_conversion_chain.invoke({"text": mapping_dict['Job description']}).content
                    mapping_dict['Job description'] = formatted_html
                    mapping_dict['Job title'] = mapping_dict['Job title'].capitalize()
                    # print(mapping_dict)
                    # Save the original and rewritten job listings for reference

                    with open("new.txt", "w", encoding="utf-8") as n:
                        n.write(new_job_listing)
                    
                    return mapping_dict
            else:
                print("No JSON found in the response.Trying again.")
                if timeout == 5:
                    print("Timeout limit exceeded")
                    break
                else:
                    print("REtrying")
                    timeout +=1


        # Invoke the chain with the text content
        

    def process_job(self, job, check_duplicates=True):
        job_url = job['job_url']
        print("Processing job for the url:", job_url)
        job_content = job['job_listing']
        with open("original.txt", "w", encoding="utf-8") as o:
            o.write(job_content)

        # Check for duplicates in WordPress and Manatal mappings
        duplicate_in_wp = job_url in self.job_url_to_id_mapping_wp and check_duplicates
        duplicate_in_manatal = job_url in self.job_url_to_id_mapping_manatal and check_duplicates
        
        # Determine which platform(s) need processing
        if duplicate_in_wp and duplicate_in_manatal:
            print(f"Job at {job_url} already processed for both WordPress and Manatal. Skipping.")
            return None, None, ""
        elif not duplicate_in_wp and not duplicate_in_manatal:
            processing_status = "Both"
        elif not duplicate_in_wp:
            print(f"Job at {job_url} processing for wp.")
            processing_status = "WordPress"
        else:
            print(f"Job at {job_url} processing for manatal.")
            processing_status = "Manatal"

        # Generate unique job ID from the job URL
        job_id = hashlib.md5(job_url.encode()).hexdigest()

        # Process the job listing and generate its dictionary mapping
        job_dict = self.process_job_listing(job_content)
        if job_dict:
            today = date.today()
            d = today.strftime("%B %d, %Y")

            # Save the job ID to the dictionary and the mapping
            job_dict["id"] = job_id
            if check_duplicates:
                self.jobs_mapping[job_url] = job_dict
                self.jobs_mapping['date'] = d
                self.save_jobs_json()
            
            # Save to WordPress mapping if not a duplicate
            if not duplicate_in_wp:
                self.job_url_to_id_mapping_wp[job_url] = job_id
                self.job_url_to_id_mapping_wp['date'] = d
                self.save_job_url_to_id_mapping_wp()
                
            # Save to Manatal mapping if not a duplicate
            if not duplicate_in_manatal:
                self.job_url_to_id_mapping_manatal[job_url] = job_id
                self.job_url_to_id_mapping_manatal['date'] = d
                self.save_job_url_to_id_mapping_manatal()
                
            return job_url, job_dict, processing_status
        else:
            print(f"Failed to process Job from {job_url}")
            return job_url, None, "Failed"
# Usage example

if __name__ == "__main__":
    from dotenv    import load_dotenv
    load_dotenv()
    from prompts import job_listing_json_prompt, rewrite_prompt, to_html
    import os
    from job_retrieval import get_centrumtandzorg, get_puur, get_orthocenter, get_dentalvacancies_eu, get_freshtandartsen, get_lassus

    processor = JobListingProcessor(rewrite_prompt=rewrite_prompt, job_listing_json_prompt=job_listing_json_prompt, html_prompt=to_html, test=False)
    url, dic, status= processor.process_job(get_dentalvacancies_eu()[3], check_duplicates=False)
    if status:
        print(dic['Job title'])
        print(dic['Job description'])