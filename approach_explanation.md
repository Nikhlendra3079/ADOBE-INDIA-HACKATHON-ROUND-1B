# Round 1B: Persona-Driven Document Intelligence
# Theme: “Connect What Matters — For the User Who Matters”


## Challenge Brief

You will build a system that acts as an intelligent document analyst, extracting
and prioritizing the most relevant sections from a collection of documents based
on a specific persona and their job-to-be-done.

## Approach

This solution extracts and ranks the most relevant sections from PDF documents by combining simple text extraction with modern semantic embeddings. Unlike rule-heavy or template-based extractors, this approach is designed to work generically across diverse document types without hardcoding any file-specific logic.

The core of the solution is a lightweight pipeline that works as follows:

1. **Input Processing**  
   The script reads a single JSON input file that describes the target *persona* and *job to be done*, along with a list of PDF filenames to analyze. The PDFs are placed in an organized `input/PDFs` folder.  

2. **Candidate Section Extraction**  
   For each PDF, the script uses `PyPDF2` to extract text page by page. From each page, the first few non-empty lines are treated as candidate section headings, under the assumption that headings or prominent content usually appear near the top of a page. This heuristic avoids complex layout parsing while reliably surfacing potential sections of interest.

3. **Semantic Similarity Ranking**  
   The solution uses a locally stored `SentenceTransformer` model (`all-mpnet-base-v2`) to compute embeddings for both the user query (persona + job to be done) and all candidate section titles.  
   It then computes pairwise cosine similarity scores between the query embedding and each candidate’s embedding. This semantic similarity step enables the system to connect the user’s intent with the content, even when relevant sections do not contain exact keyword matches.

4. **Selecting the Best Sections**  
   All candidate sections are ranked by their similarity score. The top five are selected and added to the final output. For each, the script records the document name, page number, and heading text. It also saves a short snippet of the surrounding page text for further context.

5. **Output Generation**  
   The final output is a clean JSON file that includes:
   - Metadata (input files, persona, task, and timestamp)
   - The top-ranked section titles with page references and ranks
   - A refined text snippet for each, supporting downstream summarization or analysis

## Libraries Used

- **PyPDF2**: A robust PDF text extraction library.
- **SentenceTransformers**: Provides the `all-mpnet-base-v2` model for efficient semantic similarity matching.

## How to Build and Run

1. **Prepare the Inputs**  
   Place your PDFs in `input/PDFs` and your `challenge1b_input.json` in the `input` folder.

2. **Build the Docker Image**  
   ```bash
   docker build --platform linux/amd64 -t mysolutionname:somerandomidentifier .
   ```

3.  **Run the container**:
    * For Windows (CMD):
        ```bash
        docker run --rm -v "%CD%/input:/app/input" -v "%CD%/output:/app/output" --network none mysolutionname:somerandomidentifier
        ```
    * For macOS, Linux, or PowerShell:
        ```bash
        docker run --rm -v "$(pwd)/input:/app/input" -v "$(pwd)/output:/app/output" --network none mysolutionname:somerandomidentifier
        ```

The ranked output will appear in the `output` folder.
