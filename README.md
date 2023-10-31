# VertexAIDocExplorer 🚀

Unlock the power of VertexAI Search with `VertexAIDocExplorer`, a two-tiered search pipeline designed to make document sourcing and searching smarter and more efficient. Easily source PDF documents from URLs and perform question-answering on indexed documents using Google's state-of-the-art PaLM-2 model.

## 🌟 Features

- **URL Indexing:** 🌐 Index and search for links leading to PDF documents from a list of company website URLs.
- **LLM Pruning:** 🧠 Classify URLs into five categories using VertexAI search metadata and the PaLM-2 model.
- **Async Downloader:** ⚡ Asynchronously download PDF documents.
- **Cloud Storage Uploader:** ☁️ Seamlessly upload documents to Google Cloud Storage.
- **Document Indexing:** 📖 Index relevant PDFs for efficient searching.
- **Question Answering:** ❓ Enable question-answering capabilities on the indexed documents.

## 🚀 Getting Started

### 🛠️ Prerequisites

- Follow the [Installation steps for VertexAI Search](#).
- Ensure you have Python 3.8+ (3.9+ recommended) installed.
- We recommend using Visual Studio Code for the best experience, but any IDE will work.

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

Navigate to the `src/` directory to view the project's source code. Begin by exploring the `config` folder, which contains:

- `config.yml`: Configuration for GCP project ID, credentials, and other settings.
- `doc-search-queries.jsonl`: Queries for evaluating document search results.
- `site-search-queries.jsonl`: Queries for evaluating site search results.
- `topics.jsonl`: Metadata for classifying PDF URL links.
- `sites.jsonl`: Collection of sites to index with VertexAI search.

The `run/` directory contains scripts for testing and evaluating:

- `site_search.py`: Finds PDFs across indexed sites.
   ```bash
   python src/run/site_search.py
   ```

- `pruner.py`: Prunes site search results by classification.
   ```bash
   python src/run/pruner.py
   ```

- `downloader.py`: Downloads PDFs from pruned URL links.
   ```bash
   python src/run/downloader.py
   ```

- `uploader.py`: Uploads PDFs to Google Cloud Storage.
   ```bash
   python src/run/uploader.py
   ```

- `doc_search.py`: Performs document search with relevant passages and answers.
   ```bash
   python src/run/doc_search.py
   ```

- `evaluate.py`: Evaluates the explorer for both site and document search.
   ```bash
   python src/run/evaluate.py
   ```

- `generate_reports.py`: Converts evaluation results to Excel sheets.
   ```bash
   python src/run/generate_reports.py
   ```

**Note:** Before performing site search, create a search app and data store using the list of sites. Before performing document search, create a search app pointing to the GCS bucket with the PDFs from `downloader.py`.

## Appendix

- [Creating a Datastore and Ingesting Data](https://cloud.google.com/generative-ai-app-builder/docs/create-datastore-ingest)