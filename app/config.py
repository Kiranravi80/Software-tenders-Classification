from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
MONGODB_URL = os.getenv("MONGODB_URL")
PROJECT_NAME = "GeM AI Tender Intelligence"

BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_DIR = BASE_DIR / "output"
PDF_DIR = BASE_DIR / "pdfs"
LOG_DIR = BASE_DIR / "logs"

OUTPUT_DIR.mkdir(exist_ok=True)
PDF_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# ===========================
# GEM
# ===========================

BASE_URL = "https://bidplus.gem.gov.in"

ALL_BIDS_URL = f"{BASE_URL}/all-bids"

ALL_BIDS_API = f"{BASE_URL}/all-bids-data"

DETAIL_URL = f"{BASE_URL}/showbidDocument"

OTHER_DETAILS_URL = f"{BASE_URL}/public-bid-other-details"

CORRIGENDUM_URL = f"{BASE_URL}/bidding/bid/viewCorrigendum"

REPRESENTATION_URL = f"{BASE_URL}/publish-representations"

# ===========================
# SCRAPER
# ===========================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        " AppleWebKit/537.36"
        " Chrome/137.0.0.0 Safari/537.36"
    )
}

REQUEST_TIMEOUT = 30

RETRY_COUNT = 5

PAGE_SIZE = 10