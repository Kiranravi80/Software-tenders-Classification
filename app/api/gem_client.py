import json
import re

import requests

from app.config import *
from app.utils.logger import log
from app.utils.retry import retry_request
from datetime import datetime, timezone
from app.api.listing_scraper import ListingScraper


class GeMClient:

    def __init__(self):

        self.session = requests.Session()

        self.session.headers.update(HEADERS)

        self.csrf = None

    @retry_request
    def initialize(self):

        log.info("Opening GeM...")

        response = self.session.get(
            ALL_BIDS_URL,
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        match = re.search(
            r"csrf_bd_gem_nk':\s*'([a-zA-Z0-9]+)'",
            response.text
        )

        if not match:
            raise Exception("Unable to find CSRF token")

        self.csrf = match.group(1)

        log.success("CSRF Token Loaded")

    @retry_request
    def fetch_page(self, page=1):

        payload = {
            "page": page,
            "param": {
                "searchBid": "",
                "searchType": "fullText"
            },
            "filter": {
                "bidStatusType": "ongoing_bids",
                "byType": "all",
                "highBidValue": "",
                "byEndDate": {
                    "from": "",
                    "to": ""
                },
                "sort": "Bid-Start-Date-Latest"
            }
        }

        response = self.session.post(
            ALL_BIDS_API,
            data={
                "payload": json.dumps(payload),
                "csrf_bd_gem_nk": self.csrf
            },
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        return response.json()

    def fetch_all(self):

        page = 1
        tenders = []

        today = datetime.now(timezone.utc).date()

        while True:

            log.info(f"Fetching Page {page}")

            data = self.fetch_page(page)

            docs = data["response"]["response"]["docs"]

            if not docs:
                log.info("No more tenders found.")
                break

            stop_scraping = False

            for tender in docs:

                start_date = tender.get("final_start_date_sort", [])

                if not start_date:
                    continue

                try:

                    tender_date = datetime.fromisoformat(
                        start_date[0].replace("Z", "+00:00")
                    ).date()

                    # Only today's tenders
                    if tender_date == today:
                        tenders.append(tender)

                    # Since results are sorted newest → oldest,
                    # stop once we hit an older date.
                    elif tender_date < today:
                        stop_scraping = True
                        break

                except Exception as e:
                    log.error(f"Date parsing failed: {e}")

            log.info(f"Today's tenders collected: {len(tenders)}")

            if stop_scraping:
                log.success("Reached tenders older than today. Stopping scraper.")
                break

            page += 1

        return tenders
    def scrape_listing(self):

        scraper = ListingScraper(self.session)

        return scraper.parse_cards()