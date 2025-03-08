import openai
import json
import os
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Load environment variables
load_dotenv()

# OpenAI Client initialization
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def load_json(file_path):
    """Load data from the input JSON file."""
    logger.info(f"Loading JSON data from {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            items = json.load(file)
            logger.info(f"Loaded {len(items)} items from the file")
            # Extract URL, title, and description
            data = [{"url": x['url'], "title": x.get('title', ''), "description": x.get('metadata', '')} for x in
                    items]
            return data
    except Exception as e:
        logger.error(f"Error loading JSON file: {e}")
        raise


def is_scm_related(title,doc_content):
    """Determine if the documentation content is related to SCM."""
    prompt = f"""
    Determine whether the following documentation content is related to Source Code Management (SCM).
    If it is related to SCM (such as organisation, repositories, commits, pull requests, branches, etc.), return 'SCM Related web page links' from the given list of input urls.
    Otherwise, return 'Not SCM Related'.

    Documentation Content:
    {doc_content[:4000]}  # Provide only the first 4000 characters

    Please return only 'SCM Related' or 'Not SCM Related'.
    """

    logger.info("Checking if documentation is SCM related")
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # You can change this to the model you have access to
            messages=[
                {"role": "system", "content": "You are an API extraction assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        # Get the response text
        extracted_text = response.choices[0].message.content.strip()

        # Check if the content is SCM related
        if "SCM Related" in extracted_text:
            return True
        else:
            return False

    except Exception as e:
        logger.error(f"Error during SCM check: {e}")
        raise


def save_to_json(extracted_data, filename="scm_related_urls.json"):
    """Save the extracted SCM-related URLs to a JSON file."""
    try:
        with open(filename, "w", encoding="utf-8") as json_file:
            json.dump(extracted_data, json_file, indent=4)
        logger.info(f"Extracted data saved to {filename}")
    except Exception as e:
        logger.error(f"Error saving to JSON file: {e}")
        raise


def main():
    input_file = "output.json"
    output_file = "scm_related_urls.json"

    # Load the JSON data from the input file
    try:
        data = load_json(input_file)
    except Exception as e:
        logger.error(f"Failed to load input file {input_file}: {e}")
        return

    # Prepare a list to store the SCM-related URLs
    scm_related_urls = []
    processed_urls=set()

    # Process each document to determine if it's SCM related
    for item in data:
        url = item['url']
        title = item['title']
        description = item['description']


        if url in processed_urls:
            logger.info(f"Duplicate URL found: {url},skipping...")
            continue
        # Check if the content is related to SCM
        if description:  # Only check if there is a description
            try:
                if is_scm_related(title,description):
                    scm_related_urls.append({
                        "url": url,
                        # "title": title,
                        # "description": description
                    })
            except Exception as e:
                logger.error(f"Failed to determine SCM relevance for {url}: {e}")
        else:
            logger.info(f"No description available for URL: {url}, skipping...")

    # Save the SCM-related URLs to a JSON file
    try:
        save_to_json(scm_related_urls, output_file)
    except Exception as e:
        logger.error(f"Failed to save the extracted data to {output_file}: {e}")
        return

    logger.info(f"Successfully processed {len(scm_related_urls)} SCM-related items. Results saved to {output_file}.")


if __name__ == "__main__":
    main()
