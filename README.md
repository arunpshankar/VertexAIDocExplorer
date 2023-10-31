# VertexAIDocExplorer 🚀

Unlock the power of VertexAI Search with `VertexAIDocExplorer`, a two-tiered search pipeline designed to source and search documents intelligently. Source PDF documents from URLs and perform question-answering on indexed documents using Google's state-of-the-art PaLM-2 model.

## 🌟 Features

- 🌐 **URL Indexing:** Index and search for links leading to PDF documents from a list of company website URLs.
- 🧠 **LLM Pruning:** Classify URLs into five categories using VertexAI search metadata and the PaLM-2 model.
- ⚡ **Async Downloader:** Download PDF documents asynchronously.
- ☁️ **Cloud Storage Uploader:** Upload documents to Google Cloud Storage seamlessly.
- 📖 **Document Indexing:** Index relevant PDFs for efficient searching.
- ❓ **Question Answering:** Enable question-answering capabilities on the indexed documents.

## 🚀 Getting Started

### 🛠️ Prerequisites

- Follow the [Installation steps for VertexAI Search](#).
- Python 3.8+ (3.9+ recommended).
- Recommended IDE: Visual Studio Code (but any IDE will work).

### 📥 Installation

1. **Clone** the repository:
```bash
git clone https://github.com/arunpshankar/VertexAIDocExplorer.git
```

2. **Navigate** to the project directory:
```bash
cd VertexAIDocExplorer
```

3. **Set Up Virtual Environment** (optional but recommended):
```bash
python3 -m venv .venv
source .venv/bin/activate
```

4. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

5. **Update your PYTHONPATH**:
```bash
export PYTHONPATH=$PYTHONPATH:.
```

### 📘 Usage

Navigate to `src/` to view the source code. Start with the `config` folder:

- `config.yml`: Configurations for GCP project ID, credentials, and more.
- `doc-search-queries.jsonl`: Queries to evaluate document search results.
- `site-search-queries.jsonl`: Queries to evaluate site search results.
- `topics.jsonl`: Metadata for classifying PDF URL links.
- `sites.jsonl`: Collection of sites to index with VertexAI search.

The `run/` directory contains scripts for testing and evaluation:

- `site_search.py`: Find PDFs across indexed sites.
```bash
python src/run/site_search.py
```

- `pruner.py`: Prune site search results by classification.
```bash
python src/run/pruner.py
```

- `downloader.py`: Download PDFs from pruned URL links.
```bash
python src/run/downloader.py
```

- `uploader.py`: Upload PDFs to Google Cloud Storage.
```bash
python src/run/uploader.py
```

- `doc_search.py`: Search documents with relevant passages and answers.
```bash
python src/run/doc_search.py
```

- `evaluate.py`: Evaluate the explorer for both site and document searches.
```bash
python src/run/evaluate.py
```

- `generate_reports.py`: Convert evaluation results to Excel sheets.
```bash
python src/run/generate_reports.py
```

> **Note:** Before site searching, create a search app and data store using the list of sites. Before document searching, create a search app pointing to the GCS bucket with the PDFs from `downloader.py`.

## Sample Outputs

### Site Search Result:

```json
{
   "question": "what is hsbc LCR 2021",
   "rank": 7,
   "document": "gs://financial-pdf-documents/HSBC Holdings plc  Annual Report and Accounts 2020.pdf",
   "segments": [
      {
         "segment": "• HSBC Bank Middle East – UAE branch remained in a strong liquidity position, with a liquidity ratio of 280%. • HSBC Canada increased its LCR to 165%, mainly driven by increased customer deposits and covered bond issuance.",
         "page": "179"
      }
   ],
   "answer": "The liquidity coverage ratio (LCR) is a measure of a bank's ability to meet its liquidity needs for a 30-day period under stressed conditions [1]. The LCR is calculated by dividing a bank's high-quality liquid assets by its net cash outflows over a 30-day period [1]. The LCR is based on the average values of the preceding 12 months [4]. In 2021, HSBC's LCR was 150% [5]."
}
```

**Fields:**

- **question:** The query posed by the user.
- **rank:** The rank of the document in search results.
- **document:** The GCS path to the relevant PDF document.
- **segments:** List of relevant segments from the document.
  - **segment:** A text snippet from the document that's relevant to the query.
  - **page:** The page number where the segment can be found.
- **answer:** A concise answer to the query.

### Document Search Result:

```json
{
   "question": "Does the company have a Human Rights policy or a commitment to promote and respect human rights, and to prevent human rights violations or indigenous rights?",
   "rank": 6,
   "document": "gs://financial-pdf-documents/HSBC Supplier Code of Conduct  English.pdf",
   "segments": [
      {
         "segment": "¡ Not employ children, prohibit the use of child labour in their operations and supply chain, and take immediate and effective measures to stop child labour as a matter of urgency.",
         "page": "5"
      }
   ],
   "answer": "HSBC has commitments and rules in place to mitigate risks and prevent serious infringements of human rights and fundamental freedoms [5]. They also have policies to protect the environment and safeguard the health and safety of individuals [5]."
}
```

**Fields:** Similar to the Site Search Result fields.

## Appendix

- [Creating a Datastore and Ingesting Data](https://cloud.google.com/generative-ai-app-builder/docs/create-datastore-ingest)
- [Preview Search Results](https://cloud.google.com/generative-ai-app-builder/docs/preview-search-results)