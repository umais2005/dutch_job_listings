import json
import hashlib
from job_retrieval import (
    get_centrumtandzorg,
    get_dentalvacancies_eu,
    get_detandartsengroep,
    get_freshtandartsen,
    get_lassus,
    get_mondzorggilde,
    get_omnios,
    get_orthocenter,
    get_puur,
    get_toportho,
    get_werkenbijdentalclinics,
    get_werkenbijpda
)
from rewrite import JobListingProcessor
from post import post_job_to_wordpress, post_manatal_jobs
from dotenv    import load_dotenv
load_dotenv()
from prompts import job_listing_json_prompt, rewrite_prompt, to_html
import os


# Initialize the JobListingProcessor with the required parameters
processor = JobListingProcessor(rewrite_prompt=rewrite_prompt, job_listing_json_prompt=job_listing_json_prompt, html_prompt=to_html, temperature=0.0)

# Define the maximum number of jobs to retrieve from each function

# List of job retrieval functions to iterate over
job_retrieval_functions = {
    # "centrumtandzorg": get_centrumtandzorg,
    # "dentalvacancies_eu": get_dentalvacancies_eu,
    # "detandartsengroep": get_detandartsengroep,
    # "freshtandartsen": get_freshtandartsen,
    # "lassus": get_lassus,
    # "mondzorggilde": get_mondzorggilde,
    # "omnios": get_omnios,
    # "orthocenter": get_orthocenter,
    # "puur": get_puur,
    # "toportho": get_toportho,
    "werkenbijdentalclinics": get_werkenbijdentalclinics,
    # "werkenbijpda": get_werkenbijpda
}
print("Starting to scrape jobs, from each website one by one.")

# Process each job retrieval function
def main(check_name=None):
    """
    Main function to retrieve job listings, process them, and post to WordPress and Manatal based on processing status.

    Parameters:
        processor (JobListingProcessor): Instance of the JobListingProcessor class for processing job listings.
        job_retrieval_functions (dict): Dictionary of job retrieval functions by name.
        post_to_wordpress (function): Function to post job to WordPress.
        post_to_manatal (function): Function to post job to Manatal.
    """
    for idx, (name, retrieve_jobs) in enumerate(job_retrieval_functions.items(), start=1):
        if check_name:
            if name != check_name:
                break

        print(f"Retrieving jobs from {name}...")
        job_listings = retrieve_jobs()  # Call each job retrieval function

        # Process each job listing
        job_n = 1
        for job in job_listings:
            job_url, job_dict, processing_status = processor.process_job(job, check_duplicates=True)
            if job_dict:
                print("+++++++++++++++++++JOB NUMBER {} for {}++++++++++++++++++++++++++++".format(job_n, name))
                job_n +=1
                try:
                    print(f"Mapping created for job at {job_url}:\n")
                    print("ID:", job_dict['id'])
                    print("Job Title:", job_dict['Job title'])
                    print("Job Description (preview):", job_dict['Job description'][:70])
                    print("Fields:", list(job_dict.keys()))

                    # Post based on the processing status
                    if processing_status in ["Both", "WordPress"]:
                        wp_response = post_job_to_wordpress(job_dict=job_dict, status="draft")
                        if wp_response:
                            print(f"Job from {job_url} posted to WordPress with post ID {wp_response['id']}")
                        else:
                            print(f"Error posting job from {job_url} to WordPress")
                    
                    if processing_status in ["Both", "Manatal"]:
                        manatal_response = post_manatal_jobs(job_dict=job_dict)
                        try:
                            career_page_url = manatal_response['career_page_url']
                            print(f"Job from {job_url} posted to Manatal with career page URL {career_page_url}")
                        except KeyError:
                            print(f"Error posting job from {job_url} to Manatal")

                except Exception as e:
                    print("Error faced:", e)
            else:
                print(f"Skipping job at {job['job_url']}.")


if __name__ == "__main__":
    main()