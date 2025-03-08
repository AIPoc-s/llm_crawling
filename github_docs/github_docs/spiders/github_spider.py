from urllib.parse import urljoin

import scrapy


class GithubSpider(scrapy.Spider):
    name = 'github_spider'
    start_urls = ['https://docs.github.com/en/rest?apiVersion=2022-11-28']

    def parse(self, response):
        # Extract all hyperlinks from the page
        links = response.css('a::attr(href)').getall()

        # Iterate through each link and follow it to get the title and metadata
        for link in links:
            # Combine the base URL with the relative URL to get the full URL
            full_url = urljoin(response.url, link)

            # Follow the link and call the 'parse_link' method to extract title and metadata
            yield response.follow(full_url, self.parse_link)

    def parse_link(self, response):
        """This method will parse each individual URL to get the title and metadata"""

        # Extract the title from heading tags (e.g., <h1>, <h2>, <h3>, etc.)
        title = response.css('h1::text, h2::text, h3::text').getall()
        title = ' '.join(title).strip()  # Join all heading texts as the title
        title = self.clean_text(title)  # Clean any unwanted \n or \t

        # Extract metadata (description) from <meta> tags in the <head> section
        metadata = response.css('meta[name="description"]::attr(content)').get()  # Get content of description meta tag
        if not metadata:
            metadata = response.css(
                'meta[name="keywords"]::attr(content)').get()  # If description is not available, fall back to keywords
        if not metadata:
            # Fallback text if no metadata found
            metadata = "No metadata available for this URL."

        metadata = self.clean_text(metadata)  # Clean any unwanted \n or \t

        # Yield the URL, Title, and Metadata for the current page (URL)
        yield {
            'url': response.url,
            'title': title,
            'metadata': metadata
        }

    def clean_text(self, text):
        """Cleans unwanted newline and tab characters from text"""
        # Replace newline characters and tabs with an empty string
        return text.replace('\n', ' ').replace('\t', ' ').strip()
