import re
from typing import Optional


class TenderFieldExtractor:

    def __init__(self):

        self.patterns = {

            "bid_number":
                r"Bid Number[:\s]*([A-Z0-9\/\-]+)",

            "dated":
                r"Dated[:\s]*([0-9\-\/]+)",
            
            "start_date":
                r"Start Date\s*([0-9:\-\s]+)",

            "bid_end_datetime":
                r"Bid End Date\/Time\s*([0-9:\-\s]+)",

            "bid_opening_datetime":
                r"Bid Opening\s*Date\/Time\s*([0-9:\-\s]+)",

            "bid_offer_validity_days":
                r"Bid Offer\s*Validity.*?([0-9]+)\s*\(Days\)",

            "ministry_name":
                r"Ministry\/State Name\s*(.*?)\n",

            "department_name":
                r"Department Name\s*(.*?)\n",

            "organisation_name":
                r"Organisation Name\s*(.*?)\n",

            "minimum_average_annual_turnover":
                r"Minimum Average Annual Turnover.*?\n(.*?)\n",

            "past_experience_required":
                r"Years of Past Experience Required.*?\n(.*?)\n",

            "mse_relaxation":
                r"MSE Relaxation.*?\n(Yes|No)",

            "startup_relaxation":
                r"Startup Relaxation.*?\n(Yes|No)",

            "bid_to_ra_enabled":
                r"Bid to RA enabled\s*(Yes|No)",

            "evaluation_method":
                r"Evaluation Method\s*(.*?)\n",

            "arbitration_clause":
                r"Arbitration Clause\s*(Yes|No)",

            "emd_value":
                r"EMD Amount\s*([0-9,\.]+)",

            "tender_value":
                r"Tender Value\s*([₹0-9A-Za-z,\.\s]+)"
        }

    # -------------------------------------------------

    def clean(self, value: Optional[str]):

        if value is None:
            return None

        value = value.replace("\u00a0", " ")

        value = re.sub(r"\s+", " ", value)

        value = value.strip()

        if value == "":
            return None

        return value

    # -------------------------------------------------

    def search(self, pattern, text):

        match = re.search(
            pattern,
            text,
            re.IGNORECASE | re.DOTALL
        )

        if not match:
            return None

        return self.clean(match.group(1))

    # -------------------------------------------------

    def extract_single_fields(self, text):

        data = {}

        for field, pattern in self.patterns.items():

            data[field] = self.search(
                pattern,
                text
            )

        return data

    # -------------------------------------------------

    def normalize_dates(self, data):

        # Future:
        # Convert to ISO if required

        return data

    # -------------------------------------------------

    def normalize_numbers(self, data):

        if data["emd_value"]:

            data["emd_value"] = (
                data["emd_value"]
                .replace(",", "")
            )

        return data

    # -------------------------------------------------

    def extract(self, text):

        data = self.extract_single_fields(
            text
        )

        data = self.normalize_dates(data)

        data = self.normalize_numbers(data)

        return data
    
    # -------------------------------------------------
    # Extract Item Category
    # -------------------------------------------------

    def extract_item_category(self, text):

        pattern = (
            r"Item Category\s*(.*?)"
            r"(?:GeMARPTS|Minimum Average Annual Turnover|Bid Number)"
        )

        match = re.search(
            pattern,
            text,
            re.IGNORECASE | re.DOTALL
        )

        if not match:
            return []

        value = self.clean(match.group(1))

        if not value:
            return []

        items = []

        for item in re.split(r"\s*,\s*",value):

            item = self.clean(item)

            if item:
                items.append(item)

        return items

    # -------------------------------------------------
    # Extract Documents Required
    # -------------------------------------------------

    def extract_documents(self, text):

        pattern = (
            r"Document required.*?\n"
            r"(.*?)"
            r"(?:\*In case|Do you want to show|Minimum number of bids)"
        )

        match = re.search(
            pattern,
            text,
            re.IGNORECASE | re.DOTALL
        )

        if not match:
            return []

        docs = self.clean(match.group(1))

        docs = docs.replace(
            "from seller",
            ""
        )

        if not docs:
            return []

        documents = []

        for doc in docs.split(","):

            doc = self.clean(doc)

            if doc:
                documents.append(doc)

        return documents

    # -------------------------------------------------
    # Buyer Specification Link
    # -------------------------------------------------

    def extract_specification_link(self, text):

        pattern = (
            r"https?://[^\s]+"
        )

        urls = re.findall(
            pattern,
            text
        )

        for url in urls:

            if "specification" in url.lower():

                return url

        return None

    # -------------------------------------------------
    # Final Extractor
    # -------------------------------------------------

    def extract(self, text):

        data = self.extract_single_fields(text)

        data["item_category"] = self.extract_item_category(text)

        data["documents_required"] = self.extract_documents(text)

        data["buyer_specification_document"] = (
            self.extract_specification_link(text)
        )

        data = self.normalize_dates(data)

        data = self.normalize_numbers(data)

        return data