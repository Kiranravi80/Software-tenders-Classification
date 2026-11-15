import re
from urllib.parse import urljoin

from scrapling import Fetcher

from app.config import ALL_BIDS_URL
from app.utils.logger import log


class ListingScraper:

    def __init__(self, session):

        self.session = session

        self.fetcher = Fetcher()

    def _text(self, node):

        if node is None:
            return ""

        return node.text.strip()

    def parse_cards(self):

        log.info("Loading GeM listing page...")

        response = self.session.get(
            ALL_BIDS_URL,
            timeout=60
        )

        response.raise_for_status()

        page = self.fetcher.from_string(response.text)

        # Update selector if required
        cards = page.css(".bid-card")

        log.info(f"Found {len(cards)} cards")

        tenders = []

        for card in cards:

            try:

                bid_number = ""
                ra_number = ""

                text = card.text

                bid = re.search(
                    r"Bid\s*No\.?\s*:\s*(GEM/\d+/B/\d+)",
                    text,
                    re.IGNORECASE
                )

                if bid:
                    bid_number = bid.group(1)

                ra = re.search(
                    r"RA\s*NO\.?\s*:\s*(GEM/\d+/R/\d+)",
                    text,
                    re.IGNORECASE
                )

                if ra:
                    ra_number = ra.group(1)

                item = ""

                m = re.search(
                    r"Items:\s*(.*?)\s*Quantity:",
                    text,
                    re.S
                )

                if m:
                    item = m.group(1).strip()

                quantity = 0

                q = re.search(
                    r"Quantity:\s*(\d+)",
                    text
                )

                if q:
                    quantity = int(q.group(1))

                ministry = ""
                department = ""

                dept = re.search(
                    r"Department Name And Address:\s*(.*?)\s*Start Date:",
                    text,
                    re.S
                )

                if dept:

                    lines = [
                        i.strip()
                        for i in dept.group(1).splitlines()
                        if i.strip()
                    ]

                    if len(lines) >= 1:
                        ministry = lines[0]

                    if len(lines) >= 2:
                        department = lines[1]

                start_date = ""

                m = re.search(
                    r"Start Date:\s*(.*?)\s*End Date:",
                    text,
                    re.S
                )

                if m:
                    start_date = m.group(1).strip()

                end_date = ""

                m = re.search(
                    r"End Date:\s*(.*)",
                    text
                )

                if m:
                    end_date = m.group(1).strip()

                corrigendum = ""

                for a in card.css("a"):

                    href = a.attrib.get("href", "")

                    if "Corrigendum" in a.text:

                        corrigendum = urljoin(
                            ALL_BIDS_URL,
                            href
                        )

                tenders.append({

                    "bid_number": bid_number,

                    "ra_number": ra_number,

                    "items": item,

                    "quantity": quantity,

                    "ministry": ministry,

                    "department": department,

                    "start_date": start_date,

                    "end_date": end_date,

                    "corrigendum": corrigendum

                })

            except Exception as e:

                log.error(e)

        return tenders