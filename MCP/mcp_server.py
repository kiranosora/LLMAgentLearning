# server.py
from mcp.server.fastmcp import FastMCP
from playwright.async_api import async_playwright
import json
import traceback

# Create an MCP server
mcp = FastMCP("ou_mou_mcp")


# Add arXiv tools for searching and retrieving academic papers
@mcp.tool()
def search_arxiv_papers(query: str, max_results: int = 10, sort_by: str = "relevance",
                        sort_order: str = "descending") -> dict:
    """
    Search for academic papers on arXiv based on a query.

    Args:
        query (str): Search query (e.g., "quantum computing", "machine learning")
        max_results (int, optional): Maximum number of results to return. Defaults to 10.
        sort_by (str, optional): Sort criterion - "relevance", "lastUpdatedDate", "submittedDate". Defaults to "relevance".
        sort_order (str, optional): Sort order - "ascending" or "descending". Defaults to "descending".

    Returns:
        dict: Search results with paper information
    """
    try:
        import arxiv

        # Map string parameters to enum values
        sort_by_mapping = {
            "relevance": arxiv.SortCriterion.Relevance,
            "lastUpdatedDate": arxiv.SortCriterion.LastUpdatedDate,
            "submittedDate": arxiv.SortCriterion.SubmittedDate
        }

        sort_order_mapping = {
            "ascending": arxiv.SortOrder.Ascending,
            "descending": arxiv.SortOrder.Descending
        }

        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=sort_by_mapping.get(sort_by, arxiv.SortCriterion.Relevance),
            sort_order=sort_order_mapping.get(sort_order, arxiv.SortOrder.Descending)
        )

        results = []
        for paper in arxiv.Client().results(search):
            results.append({
                "id": paper.get_short_id(),
                "entry_id": paper.entry_id,
                "title": paper.title,
                "authors": [author.name for author in paper.authors],
                "summary": paper.summary[:500] + "..." if len(paper.summary) > 500 else paper.summary,
                "published": paper.published.isoformat() if paper.published else None,
                "updated": paper.updated.isoformat() if paper.updated else None,
                "primary_category": paper.primary_category,
                "categories": paper.categories,
                "pdf_url": paper.pdf_url
            })

        return {
            "status": "success",
            "query": query,
            "total_results": len(results),
            "results": results
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to search arXiv papers: {str(e)}"
        }


@mcp.tool()
def get_arxiv_paper_details(paper_id: str) -> dict:
    """
    Get detailed information about a specific arXiv paper by its ID.

    Args:
        paper_id (str): The arXiv paper ID (e.g., "2106.01234" or "2106.01234v1")

    Returns:
        dict: Detailed information about the paper
    """
    try:
        import arxiv

        search = arxiv.Search(id_list=[paper_id])
        paper = next(arxiv.Client().results(search))
        if paper:
            return {
                "status": "success",
                "paper": {
                    "id": paper.get_short_id(),
                    "entry_id": paper.entry_id,
                    "title": paper.title,
                    "authors": [author.name for author in paper.authors],
                    "summary": paper.summary,
                    "published": paper.published.isoformat() if paper.published else None,
                    "updated": paper.updated.isoformat() if paper.updated else None,
                    "primary_category": paper.primary_category,
                    "categories": paper.categories,
                    "journal_ref": paper.journal_ref,
                    "doi": paper.doi,
                    "comment": paper.comment,
                    "pdf_url": paper.pdf_url
                }
            }
        else:
            return {
                "status": "error",
                "message": f"No paper found with ID: {paper_id}"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to get paper details: {str(e)}"
        }

# Add stock market tool using Alpha Vantage API
@mcp.tool()
def get_stock_quote(symbol: str) -> dict:
    """
    Get stock quote information from Alpha Vantage API.

    Args:
        symbol (str): Stock symbol (e.g., 'IBM', 'AAPL', 'GOOGL')

    Returns:
        dict: Stock quote information or error message
    """
    import requests
    import os

    # Alpha Vantage API configuration
    API_KEY = "1ALV5EMQV42YJF0S"
    BASE_URL = "https://www.alphavantage.co/query"

    try:
        # Make request to Alpha Vantage API
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': API_KEY
        }

        response = requests.get(BASE_URL, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()

        # Check if there's an error in the response
        if "Error Message" in data:
            return {"error": data["Error Message"]}

        if "Information" in data:
            return {"info": data["Information"]}

        # Extract global quote data
        if "Global Quote" in data:
            quote = data["Global Quote"]
            if quote:
                # Convert to a more user-friendly format
                result = {
                    "symbol": quote.get("01. symbol", ""),
                    "open": quote.get("02. open", ""),
                    "high": quote.get("03. high", ""),
                    "low": quote.get("04. low", ""),
                    "price": quote.get("05. price", ""),
                    "volume": quote.get("06. volume", ""),
                    "latest_trading_day": quote.get("07. latest trading day", ""),
                    "previous_close": quote.get("08. previous close", ""),
                    "change": quote.get("09. change", ""),
                    "change_percent": quote.get("10. change percent", "")
                }
                return {"status": "success", "data": result}
            else:
                return {"error": "No quote data found for the symbol"}
        else:
            return {"error": "Unexpected API response format"}

    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to connect to Alpha Vantage API: {str(e)}"}
    except Exception as e:
        return {"error": f"Failed to get stock quote: {str(e)}"}


# Add stock market index tool using Alpha Vantage API
@mcp.tool()
def get_market_index(index: str = "SPX") -> dict:
    """
    Get major market index information from Alpha Vantage API.

    Args:
        index (str): Market index symbol.
                    Common values: 'SPX' (S&P 500), 'DJI' (Dow Jones), 'IXIC' (NASDAQ)

    Returns:
        dict: Market index information or error message
    """
    import requests

    # Alpha Vantage API configuration
    API_KEY = "1ALV5EMQV42YJF0S"
    BASE_URL = "https://www.alphavantage.co/query"

    # Map common index symbols to Alpha Vantage symbols
    index_mapping = {
        "SPX": "SPX",
        "DJI": "DJI",
        "IXIC": "IXIC",
        "NDX": "NDX"
    }

    # Use mapping or default to provided index
    #symbol = index_mapping.get(index.upper(), index.upper())
    symbol = index

    try:
        # Make request to Alpha Vantage API for market index
        params = {
            'function': 'TIME_SERIES_DAILY',
            'apikey': API_KEY,
            'symbol': symbol
        }
        url = f"{BASE_URL}/?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}"
        response = requests.get(BASE_URL, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()

        # Check if there's an error in the response
        if "Error Message" in data:
            return {"error": data}

        # Extract market status information
        if "Time Series (5min)" in data:
            time_series = data["Time Series (5min)"]
            meta_data = data["Meta Data"]

            return {
                "status": "success",
                "meta_data" : meta_data,
                "time series": time_series
            }
        else:
            return {"error": "Unexpected API response format", "response":data}

    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to connect to Alpha Vantage API: {str(e)}"}
    except Exception as e:
        return {"error": f"Failed to get market index: {str(e)}"}

# Add accounting tools
@mcp.tool()
def init_accounting_db():
    """
    Initialize the accounting database with necessary tables.
    """
    import sqlite3
    import os

    # Create data directory if it doesn't exist
    db_dir = "data"
    db_path = os.path.join(db_dir, "accounting.db")

    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create categories table
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS categories
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       name
                       TEXT
                       UNIQUE
                       NOT
                       NULL,
                       created_at
                       TIMESTAMP
                       DEFAULT
                       CURRENT_TIMESTAMP
                   )
                   ''')

    # Create expenses table
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS expenses
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       category_id
                       INTEGER,
                       amount
                       REAL
                       NOT
                       NULL,
                       description
                       TEXT,
                       date
                       DATE
                       NOT
                       NULL
                       DEFAULT (
                       DATE
                   (
                       'now'
                   )),
                       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       FOREIGN KEY
                   (
                       category_id
                   ) REFERENCES categories
                   (
                       id
                   )
                       )
                   ''')

    # Insert some default categories if they don't exist
    default_categories = ['Food', 'Transportation', 'Entertainment', 'Utilities', 'Shopping', 'Other']
    for category in default_categories:
        cursor.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (category,))

    conn.commit()
    conn.close()

    return {"status": "success", "message": f"Database initialized at {db_path}"}


@mcp.tool()
def add_expense(category: str, amount: float, description: str = "", date: str = None):
    """
    Add a new expense record.

    Args:
        category (str): Category of the expense
        amount (float): Amount of the expense
        description (str, optional): Description of the expense
        date (str, optional): Date of the expense in YYYY-MM-DD format. Defaults to today.

    Returns:
        dict: Result of the operation
    """
    import sqlite3
    import os
    from datetime import datetime

    try:
        db_path = os.path.join("data", "accounting.db")

        # Check if database exists, if not initialize it
        if not os.path.exists(db_path):
            init_accounting_db()

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if category exists, if not create it
        cursor.execute('SELECT id FROM categories WHERE name = ?', (category,))
        category_row = cursor.fetchone()

        if category_row is None:
            # Create new category
            cursor.execute('INSERT INTO categories (name) VALUES (?)', (category,))
            category_id = cursor.lastrowid
        else:
            category_id = category_row[0]

        # Insert expense
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        cursor.execute('''
                       INSERT INTO expenses (category_id, amount, description, date)
                       VALUES (?, ?, ?, ?)
                       ''', (category_id, amount, description, date))

        expense_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return {
            "status": "success",
            "message": f"Expense added successfully with ID: {expense_id}",
            "expense_id": expense_id
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to add expense: {str(e)}"}


@mcp.tool()
def get_expenses(month: str = None, category: str = None):
    """
    Get expenses, optionally filtered by month and category.

    Args:
        month (str, optional): Month in YYYY-MM format
        category (str, optional): Category to filter by

    Returns:
        dict: List of expenses matching criteria
    """
    import sqlite3
    import os

    try:
        db_path = os.path.join("data", "accounting.db")

        # Check if database exists
        if not os.path.exists(db_path):
            return {"status": "error", "message": "Database not initialized. Please add an expense first."}

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Build query with optional filters
        query = '''
                SELECT e.id, c.name as category, e.amount, e.description, e.date, e.created_at
                FROM expenses e
                         JOIN categories c ON e.category_id = c.id \
                '''

        conditions = []
        params = []

        if month:
            conditions.append("strftime('%Y-%m', e.date) = ?")
            params.append(month)

        if category:
            conditions.append("c.name = ?")
            params.append(category)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY e.date DESC, e.created_at DESC"

        cursor.execute(query, params)
        expenses = cursor.fetchall()

        # Calculate total
        total_amount = sum(expense[2] for expense in expenses)

        # Format results
        result = []
        for expense in expenses:
            result.append({
                "id": expense[0],
                "category": expense[1],
                "amount": expense[2],
                "description": expense[3],
                "date": expense[4],
                "created_at": expense[5]
            })

        conn.close()

        return {
            "status": "success",
            "total_expenses": len(result),
            "total_amount": total_amount,
            "expenses": result
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to get expenses: {str(e)}"}


@mcp.tool()
def get_monthly_summary(year_month: str = None):
    """
    Get monthly expense summary by category.

    Args:
        year_month (str, optional): Month in YYYY-MM format. Defaults to current month.

    Returns:
        dict: Summary of expenses by category for the month
    """
    import sqlite3
    import os

    # If no year_month provided, use current month
    if year_month is None:
        year_month = datetime.datetime.now().strftime("%Y-%m")
    try:
        db_path = os.path.join("data", "accounting.db")

        # Check if database exists
        if not os.path.exists(db_path):
            return {"status": "error", "message": "Database not initialized. Please add an expense first."}

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get summary by category
        query = '''
                SELECT c.name, SUM(e.amount) as total_amount, COUNT(*) as count
                FROM expenses e
                    JOIN categories c \
                ON e.category_id = c.id
                WHERE strftime('%Y-%m', e.date) = ?
                GROUP BY c.name
                ORDER BY total_amount DESC \
                '''

        cursor.execute(query, (year_month,))
        summary_data = cursor.fetchall()

        # Calculate overall total
        total_amount = sum(row[1] for row in summary_data)

        # Format results
        result = []
        for row in summary_data:
            result.append({
                "category": row[0],
                "amount": row[1],
                "count": row[2]
            })

        conn.close()

        return {
            "status": "success",
            "month": year_month,
            "total_amount": total_amount,
            "summary": result
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to get monthly summary: {str(e)}"}


@mcp.tool()
def download_with_aria2(URI: str, path: str = "/Volumes/新加卷/aria2-dl") -> dict:
    """
    Use aria2p to download content via RPC calls with organized directory structure.

    Args:
        URI (str): The URI to download, can be a torrent file or regular URL
        path (str): The base directory path where files will be downloaded.
                   Defaults to "/Volumes/新加卷/aria2-dl" with organized subdirectories.

    Returns:
        dict: A dictionary containing the download result or error information
    """
    import urllib.request, urllib.parse, json
    import datetime, os
    import aria2p

    try:
        # Create organized directory structure based on URI type and date
        if URI.startswith("magnet:"):
            uri_type = "magnet"
        else:
            uri_type = "http"

        datestr = datetime.date.today().strftime("%Y-%m")
        final_path = os.path.join(path, uri_type, datestr)
        os.makedirs(final_path, exist_ok=True)

        # Handle torrent files
        if URI.endswith(".torrent") or URI.startswith("magnet:"):
            # Connect to aria2 RPC
            aria2 = aria2p.API(
                aria2p.Client(
                    host="http://localhost",
                    port=6800,
                    secret=""
                )
            )

            # Set download options
            opt = aria2p.Options(aria2, dict(dir=final_path))

            if URI.endswith(".torrent"):
                # Add torrent file download
                # Note: This assumes the torrent file is already downloaded to tmpFile/
                download_result = aria2.add_torrent(torrent_file_path=f'tmpFile/{URI}', options=opt)
            else:
                # Add magnet link download
                download_result = aria2.add_magnet(URI, options=opt)

            return {"status": "success", "gid": download_result.gid,
                    "message": f"Torrent/magnet download started with GID: {download_result.gid}", "path": final_path}
        else:
            # Handle regular URLs
            jsonDownload = json.dumps({
                'jsonrpc': '2.0',
                'id': 'qwer',
                'method': 'aria2.addUri',
                'params': [[URI], dict(dir=final_path)]
            })

            # Send request to aria2 RPC
            c = urllib.request.urlopen('http://localhost:6800/jsonrpc', jsonDownload.encode('utf-8'))
            aStr = json.loads(c.read())

            # Check for errors
            if 'error' in aStr:
                return {"status": "error", "message": f"Download failed: {aStr['error']}"}

            gid = aStr.get('result', 'unknown')
            return {"status": "success", "gid": gid, "message": f"Download started with GID: {gid}", "path": final_path}

    except Exception as e:
        return {"status": "error", "message": f"Failed to start download: {str(e)}"}


@mcp.tool()
def query_aria2_download_status() -> dict:
    """
    Query the status of all current aria2 downloads.

    Returns:
        dict: A dictionary containing the download status information
    """
    import aria2p

    try:
        # Connect to aria2 RPC
        aria2 = aria2p.API(
            aria2p.Client(
                host="http://localhost",
                port=6800,
                secret=""
            )
        )

        # Get all downloads
        downloads = aria2.get_downloads()

        # Process download information
        result = []
        active_count = 0

        for download in downloads:
            download_info = {
                "name": download.name,
                "status": download.status,
                "download_speed_kibs": download.download_speed_string(),
                "upload_speed_kibs": download.upload_speed_string(),
                "progress": download.progress_string(),
                "gid": download.gid,
                "size_mib": round(download.total_length / (1024 * 1024), 2) if download.total_length > 0 else 0
            }

            result.append(download_info)

            if download.status == "active":
                active_count += 1

        # Remove tasks if too many active downloads
        if active_count >= 5:
            # Note: remove_tasks() function should be defined elsewhere
            pass

        return {
            "status": "success",
            "active_downloads": active_count,
            "total_downloads": len(downloads),
            "downloads": result
        }

    except Exception as e:
        return {"status": "error", "message": f"Failed to query download status: {str(e)}"}


# New tool for downloading and extracting text from PDF files
@mcp.tool()
def download_and_extract_pdf(url: str, max_length: int = 20000) -> dict:
    """
    Download a PDF file from a URL and extract its text content.
    If the extracted text is longer than max_length characters, only the first max_length/2
    and last max_length/2 characters will be returned.

    Args:
        url (str): The URL of the PDF file to download and extract
        max_length (int, optional): Maximum length of extracted text. Defaults to 20000.

    Returns:
        dict: A dictionary containing the extracted text or error information
    """
    import requests
    import io
    import pdfplumber

    try:
        # Download the PDF file
        response = requests.get(url, timeout=60)
        response.raise_for_status()

        # Check if the content is actually a PDF
        content_type = response.headers.get('content-type', '')
        if 'application/pdf' not in content_type and not response.content.startswith(b'%PDF'):
            return {"error": f"URL does not point to a valid PDF file. Content-Type: {content_type}"}

        # Extract text from the PDF
        text_content = ""
        with pdfplumber.open(io.BytesIO(response.content)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:  # Only add if there's text on the page
                    text_content += page_text + "\n\n"

        # Process long text (more than max_length characters)
        TRUNCATED_LENGTH = int(max_length / 2)

        if len(text_content) > max_length:
            # Keep first and last parts with a notice in between
            beginning = text_content[:TRUNCATED_LENGTH]
            end = text_content[-TRUNCATED_LENGTH:]
            text_content = beginning + f"\n\n[... content truncated, {len(text_content)} characters total ...]\n\n" + end

        return {
            "url": url,
            "text_content": text_content.strip() if text_content else "No text content found in the PDF",
            "pages_processed": len(pdf.pages),
            "total_characters": len(text_content)
        }
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to download PDF: {str(e)}"}
    except Exception as e:
        return {"error": f"Failed to extract text from PDF: {str(e)}"}


# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


# ... existing code ...

import requests


# ... rest of the code ...

import playwright
# @mcp.tool()
#
# async def scrape_web_content_from_url(url): # Wrap in an async function for example
#     browser = None # Initialize browser to None for finally block
#     try:
#         async with async_playwright() as p:
#             browser = await p.chromium.launch(proxy={"server": "http://127.0.0.1:1087"}, headless=True)
#             page = await browser.new_page()
#             try:
#                 response = await page.goto(url, timeout=30000, wait_until='domcontentloaded') # Consider 'domcontentloaded' or 'load'
#                 if response is None:
#                     # This case might be rare with goto, usually throws error or returns response
#                     raise ValueError(f"page.goto() returned None for url {url}")
#                 if not response.ok:
#                      # Check status code
#                      print(f"Warning: Received status code {response.status} for {url}")
#                      # Decide if you want to proceed or raise error based on status
#
#                 # Wait for body explicitly if needed, though inner_text usually handles this
#                 # await page.wait_for_selector('body', timeout=5000) # Optional: add a small wait
#
#                 content = await page.inner_text("body")
#                 truncated_content = content[:8192]
#                 print(f"Successfully got content for {url}")
#                 # Close browser here in the success path of the inner try
#                 await browser.close()
#                 browser = None # Set browser to None after successful close
#                 return content
#
#             except Exception as page_error:
#                  return f"Error processing {url}: {traceback.format_exc()}, {type(page_error)}"
#
#     # Catch broader exceptions like launch failure
#     except Exception as page_error:
#         print(f"Error during page interaction for {url}: {page_error}")
#         return f"Error processing {url}: {traceback.format_exc()}, {type(page_error)}"
#     finally:
#         # Ensure browser is closed even if errors occurred before explicit close
#         if browser:
#             print("Closing browser in finally block...")
#             await browser.close()


# New tool for scraping web content using locally deployed firecrawl
@mcp.tool()
def scrape_with_firecrawl(url: str) -> dict:
    """
    Scrape web content using locally deployed firecrawl service.

    Args:
        url (str): The URL to scrape

    Returns:
        dict: Scraped content or error information
    """
    import requests
    import os

    try:
        # Default firecrawl API endpoint (adjust as needed for your local deployment)
        firecrawl_url = os.getenv("FIRECRAWL_API_URL", "http://localhost:3002/v0/scrape")

        # Prepare the request payload
        payload = {
            "url": url
        }

        # Make request to firecrawl API
        response = requests.post(firecrawl_url, json=payload, timeout=60)
        response.raise_for_status()

        # Return the JSON response
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to scrape with firecrawl: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
def get_memory():
    """
    Return available memory on this machine.
    """
    import psutil
    lms = 0
    mem = psutil.virtual_memory()
    for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'memory_percent']):
        if 'LM Studio Helper' in proc.info['name'] :
            lms += proc.info['memory_info'].rss
    print({"total_memory":f"{round(mem.total/1024/1024)}MB","free_memory":f"{round(mem.free/1024/1024)}MB"})
    return json.dumps({"total_memory":f"{round(mem.total/1024/1024/1024)}GB","free_memory":f"{round(mem.free/1024/1024/1024)}GB","wired_memory":f"{round(mem.wired/1024/1024/1024)}GB","memory used by lm studio":f"{round(lms/1024/1024/1024)}GB"})

import datetime
@mcp.tool()
def get_current_local_time():
    """
    Returns the current time in local timezone in ISO format.
    """
    return {"local_time": datetime.datetime.now().isoformat()}

@mcp.tool()
def list_inference_model() -> dict:
    """List large models which can be used as an inference model via lms ps command (JSON format)"""
    import subprocess
    import json
    try:
        result = subprocess.run(["lms", "ps", "--json"], capture_output=True, text=True, check=True)
        obj = json.loads(result.stdout)
        for model_info in obj:
            model_size = model_info.pop("sizeBytes", None)
            if model_size != None:
                model_size = model_size /1024/1024/1024
                model_info["sizeGB"] = model_size
        return {"output": obj}
    except Exception as e:
        return {"error": f"Failed to list models: {str(e)}"}

# New tool for listing downloaded models
@mcp.tool()
def list_downloaded_models() -> dict:
    """List all downloaded models via lms ls --json (machine-readable format)"""
    import subprocess
    try:
        result = subprocess.run(["lms", "ls", "--json"], capture_output=True, text=True, check=True)
        obj = json.loads(result.stdout)
        for model_info in obj:
            model_size = model_info.pop("sizeBytes", None)
            if model_size != None:
                model_size = model_size /1024/1024/1024
                model_info["sizeGB"] = model_size
        return json.dumps({"output": obj})
        #return "models"
    except Exception as e:
        return {"error": f"Command failed: {str(e)}"}

# New tool for loading a model with GPU acceleration
@mcp.tool()
def load_model(model_path: str) -> dict:
    """Load a model with maximum GPU acceleration without confirmation
        Args:
        model_path (str): the path of model
    """
    import subprocess
    try:
        result = subprocess.run(["lms", "load", model_path, "-y"], capture_output=True, text=True, check=True)
        return {"output": result.stdout.strip()}
    except Exception as e:
        return {"error": f"Failed to load model: {str(e)}"}
    
# New tool for loading a model with GPU acceleration
@mcp.tool()
def unload_model(model_identifier: str) -> dict:
    """unload a model without confirmation
            Args:
        model_identifier (str): the identifier of model
    """
    import subprocess
    try:
        result = subprocess.run(["lms", "unload", model_identifier], capture_output=True, text=True, check=True)
        ret = result.stdout.strip()
        if len(ret) == 0:
            ret = f"unload model {model_identifier} succeed"
        return {"output": ret}
    except Exception as e:
        return {"error": f"Failed to load model: {str(e)}"}
    
# New tool for downloading a model
@mcp.tool()
def download_model(model_path: str) -> dict:
    """download a model with model_path"""
    import subprocess
    try:
        result = subprocess.run(["lms", "get", model_path, "-y"], capture_output=True, text=True, check=True)
        ret = result.stdout.strip()
        if len(ret) == 0:
            ret = f"get model {model_path} succeed"
        return {"output": ret}
    except Exception as e:
        return {"error": f"Failed to load model: {str(e)}"}

@mcp.tool()
def calculator(representation:str):
    """
    calculate value of the representation.
    """
    return eval(representation.replace('×','*'))


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

@mcp.prompt()
def echo_prompt(message: str) -> str:
    """Create an echo prompt"""
    return f"Please process this message: {message}"


if __name__ == "__main__":
    mcp.run()
