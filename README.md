# VertexAIDocExplorer 🚀

Unlock the power of VertexAI Search with VertexAIDocExplorer, a two-tiered search pipeline designed to make document searching smarter and more efficient. Easily source PDF documents from URLs and perform question-answering on indexed documents with Google's state-of-the-art PaLM-2 model.

## 🌟 Features

- **URL Indexing:** 🌐 Index and search for links leading to PDF documents from a list of company website URLs.
- **LLM Pruning:** 🧠 Harness the power of Large Language Models for intelligent pruning of PDF links. Classify URLs into five categories using VertexAI search metadata and the PaLM-2 model.
- **Async Downloader:** ⚡ Download all the PDF documents asynchronously.
- **Cloud Storage Uploader:** ☁️ Upload documents seamlessly to Google Cloud Storage.
- **Document Indexing:** 📖 Index the identified relevant PDFs for efficient searching.
- **Question Answering:** ❓ Use a secondary search application to enable top-notch question-answering capabilities on the indexed documents.

## 🚀 Getting Started

### 🛠️ Prerequisites

- Complete the [Installation steps for VertexAI Search](#).
- Python 3.8+ (3.9+ recommended) installed in your local work environment.
- We recommend Visual Studio Code for the best experience, but any IDE will work.

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

[Your step-by-step guide on how to use the application will fit perfectly here!]

Navigate to the `src/` folder to view the project's source code. Get started by exploring the `config` folder:

- `config.yml`
- `doc-search-queries.jsonl` - Queries needed for evaluating document search results.
- `site-search-queries` - Queries for evaluating site search results (document sourcing).
- `topics.jsonl` - Contains metadata for classifying PDF URL links identified by site search for a given query.
- `sites.jsonl` - Collection of sites to index by VertexAI search.

The `run/` directory contains:

- `site_search.py` - Finds matching PDFs across indexed sites from `sites.jsonl`.
   ```bash
   $ python src/run/site_search.py
   ```

- `pruner.py` - Prunes site search results by classification into topics using text bison LLM.
   ```bash
   $ python src/run/pruner.py
   ```

- `downloader.py` - Downloads PDFs from pruned URL links asynchronously to local disk.
   ```bash
   $ python src/run/downloader.py
   ```

- `uploader.py` - Uploads downloaded PDFs from local storage to Google Cloud Storage (GCS).
   ```bash
   $ python src/run/uploader.py
   ```

- `doc_search.py` - Performs document search, finding relevant passages and generating answers with citations.
   ```bash
   $ python src/run/doc_search.py
   ```

- `generate_reports.py` - Transforms evaluation output results from JSONL format to human-readable Excel sheets.
   ```bash
   $ python src/run/generate_reports.py
   ```

**Note:** Before performing site search, create a search app and data store using the list of sites. Similarly, before performing document search, create a search app by pointing to the GCS bucket containing the PDFs downloaded by `downloader.py`.

## Appendix

- [Creating a Datastore and Ingesting Data](https://cloud.google.com/generative-ai-app-builder/docs/create-datastore-ingest)