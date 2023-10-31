# VertexAIDocExplorer 🚀

Unlock the power of VertexAI Search with VertexAIDocExplorer, a two-tiered search pipeline designed to make document searching smarter and more efficient. Easily source PDF documents from URLs and perform question-answering on indexed documents with Google's state-of-the-art PaLM-2 model.

## 🌟 Features

1. **URL Indexing:** 🌐 Given a list of company website URLs, effortlessly index and search for links leading to PDF documents.
2. **LLM Pruning:** 🧠 Harness the power of Large Language Models (LLM) for intelligent pruning of PDF links. Combine metadata from VertexAI search with the PaLM-2 model to classify URLs into five categories (modifiable as per your requirements).
3. **Async Downloader:** ⚡ A lightning-fast downloader to fetch all the PDF documents for you.
4. **Cloud Storage Uploader:** ☁️ Seamlessly upload documents to Google Cloud Storage.
5. **Document Indexing:** 📖 Once we've identified the relevant PDFs, they're indexed for efficient searching.
6. **Question Answering:** ❓ Dive deep into the indexed documents with a secondary search application, enabling top-notch question-answering capabilities.

## 🚀 Getting Started

### 🛠️ Prerequisites

- Complete the [Installation steps for VertexAI Search](#)
- Ensure you have Python 3.8+ installed (3.9+ recommended). This should be available in your local work environment.
- Any IDE will work, but we recommend Visual Studio Code for the best experience.

### 📥 Installation

1. **Clone** the repository:
   ```bash
   git clone https://github.com/[YourGitHubUsername]/VertexDocSearcher.git
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
   [installation steps...]
   ```

5. **Update your PYTHONPATH**:
   ```bash
   export PYTHONPATH=$PYTHONPATH:.
   ```

### 📘 Usage

[Your step-by-step guide on how to use the application will fit perfectly here!]

---

All the essential scripts for testing VertexAI Search across both use cases are included. Dive in and explore the future of document searching!

📝 Note: Replace placeholders such as `[installation steps...]` with the actual information or links as needed.