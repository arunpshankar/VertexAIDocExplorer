from src.prune.llm import LLM
import json
import json


class Pruner:
    def __init__(self):
        # Define base directories for easier reference later
        self.base_pdf_dir = './data/collected_pdfs/'
        self.base_url_dir = './data/crawled_urls/'
        self.base_metadata_dir = './data/selected_urls/'

    def is_pdf_url(self, url):
        """
        Check if the URL points to a PDF.
        """
        return url.lower().endswith('.pdf')

    def classify_content(self, content, child_url, llm_instance):
        """
        Classify the content into one of the specified topics using the LLM prompt.
        """
        prompt = llm_instance.construct_prompt(content, child_url)
        response_str = llm_instance.classify(prompt)
        clean_response_str = response_str.replace('```JSON\n', '').replace('```', '').strip()
        
        # Check the content before parsing
        if not clean_response_str:
            print(f"No content returned from LLM for URL: {child_url}")
            return 'Unclassified', 'No content to classify'

        try:
            classification_json = json.loads(clean_response_str)
            classification = classification_json['classification']
            rationale = classification_json['rationale']
            return classification, rationale
        except json.JSONDecodeError:
            print(f"Error decoding JSON for URL: {child_url}. Content: {clean_response_str}")
            return 'Unclassified', 'Error decoding response'


    def download_pdf(self, url, company_name, file_name):
        """
        Download the PDF from the given URL and save it with the specified filename.
        """
        response = requests.get(url)
        company_dir = os.path.join(self.base_pdf_dir, company_name)
        if not os.path.exists(company_dir):
            os.makedirs(company_dir)
        with open(os.path.join(company_dir, f'{file_name}.pdf'), 'wb') as file:
            file.write(response.content)

    def append_metadata(self, metadata, company_name):
        """
        Append the classification and rationale as metadata to the company's JSONL file.
        """
        with open(os.path.join(self.base_metadata_dir, f'{company_name}_metadata.jsonl'), 'a') as file:
            json.dump(metadata, file)
            file.write('\n')  # New line for next JSON entry

    def process_single_line(self, line, company_name):
        llm_instance = LLM()

        data = json.loads(line)
        child_url = data['child']
        if self.is_pdf_url(child_url):
            pdf_name = child_url.split('/')[-1].replace('.pdf', '')
            print(f'Processing URL: {child_url}')

            response = requests.get(data['parent'])
            soup = BeautifulSoup(response.text, 'html.parser')

            classification, rationale = self.classify_content(soup.text, child_url, llm_instance)
            if classification.lower() != 'unclassified':
                self.download_pdf(child_url, company_name, pdf_name)

                metadata = {
                    'company': company_name,
                    'filename': pdf_name,
                    'classification': classification,
                    'rationale': rationale
                }
                self.append_metadata(metadata, company_name)

    def process_files(self):
        """
        Process all the JSONL files in the data/crawled_urls/ directory.
        """
        # Ensure required directories exist
        if not os.path.exists(self.base_pdf_dir):
            os.makedirs(self.base_pdf_dir)
        if not os.path.exists(self.base_metadata_dir):
            os.makedirs(self.base_metadata_dir)

        # Use a Pool of workers
        with Pool(cpu_count()) as pool:
            # Iterate over all the JSONL files in the directory
            for filename in os.listdir(self.base_url_dir):
                with open(os.path.join(self.base_url_dir, filename), 'r') as file:
                    company_name = filename.split('.')[0]
                    try:
                        # Use starmap to pass multiple arguments to process_single_line
                        pool.starmap(self.process_single_line, [(line, company_name) for line in file])
                    except Exception as e:
                        print(f"Error processing file {filename}. Reason: {e}")
                        continue  
               
if __name__ == '__main__':
    pruner = Pruner()
    pruner.process_files()