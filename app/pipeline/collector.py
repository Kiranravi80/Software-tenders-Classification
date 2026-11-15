import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime, timezone

from app.config import BASE_URL


class TenderCollector:

    def __init__(self):
        self.pdf_base = f"{BASE_URL}/showbidDocument"

    @staticmethod
    def _first(data, default=None):
        if isinstance(data, list):
            return data[0] if data else default
        return data if data is not None else default

    def is_recent_tender(self, tender: Dict) -> bool:
        """
        Keep only tenders whose start date is today or later.
        """

        start_date = self._first(
            tender.get("final_start_date_sort"),
            ""
        )

        if not start_date:
            return False

        try:
            tender_date = datetime.fromisoformat(
                start_date.replace("Z", "+00:00")
            ).date()

            today = datetime.now(timezone.utc).date()

            return tender_date >= today

        except Exception:
            return False

    def normalize(self, tender: Dict) -> Dict:

        bid_type = self._first(
            tender.get("b_bid_type"),
            0
        )

        is_ra = bid_type == 2

        if is_ra:

            bid_id = self._first(
                tender.get("b_id_parent")
            )

            bid_number = self._first(
                tender.get("b_bid_number_parent")
            )

            ra_id = self._first(
                tender.get("b_id")
            )

            ra_number = self._first(
                tender.get("b_bid_number")
            )

        else:

            bid_id = self._first(
                tender.get("b_id")
            )

            bid_number = self._first(
                tender.get("b_bid_number")
            )

            ra_id = None

            ra_number = None

        return {

            # -----------------------
            # IDs
            # -----------------------

            "id": bid_id,

            "bid_id": bid_id,

            "ra_id": ra_id,

            # -----------------------
            # Numbers
            # -----------------------

            "bid_number": bid_number,

            "ra_number": ra_number,

            "is_reverse_auction": is_ra,

            # -----------------------
            # Tender
            # -----------------------

            "items": self._first(
                tender.get("b_category_name"),
                ""
            ),

            "quantity": self._first(
                tender.get("b_total_quantity"),
                0
            ),

            # -----------------------
            # Department
            # -----------------------

            "ministry": self._first(
                tender.get("ba_official_details_minName"),
                ""
            ),

            "department": self._first(
                tender.get("ba_official_details_deptName"),
                ""
            ),

            # -----------------------
            # Dates
            # -----------------------

            "start_date": self._first(
                tender.get("final_start_date_sort"),
                ""
            ),

            "end_date": self._first(
                tender.get("final_end_date_sort"),
                ""
            ),

            # -----------------------
            # Status
            # -----------------------

            "status": (
                "Open"
                if self._first(
                    tender.get("b_status"),
                    0
                ) == 1
                else "Closed"
            ),

            "bid_type": bid_type,

            "high_value": bool(
                self._first(
                    tender.get("is_high_value"),
                    False
                )
            ),

            "global_tender": bool(
                self._first(
                    tender.get("ba_is_global_tendering"),
                    0
                )
            ),

            "rate_contract": bool(
                self._first(
                    tender.get("is_rc_bid"),
                    0
                )
            ),

            "custom_item": bool(
                self._first(
                    tender.get("b_is_custom_item"),
                    0
                )
            ),

            # -----------------------
            # URLs
            # -----------------------

            "pdf_url": (
                f"{BASE_URL}/showbidDocument/{bid_id}"
                if bid_id
                else None
            ),

            "ra_pdf_url": (
                f"{BASE_URL}/showradocumentPdf/{ra_id}"
                if ra_id
                else None
            ),

            "detail_url": (
                f"{BASE_URL}/showbidDocument/{bid_id}"
                if bid_id
                else None
            ),

            # -----------------------
            # AI
            # -----------------------

            "is_software": None,

            "confidence": None,

            "category": None,

            "reason": None,

            # -----------------------

            "source": "GeM"
        }

    def process(self, tenders: List[Dict]) -> List[Dict]:

        cleaned = []

        seen = set()

        skipped = 0

        duplicates = 0

        for tender in tenders:

            if not self.is_recent_tender(tender):
                skipped += 1
                continue

            normalized = self.normalize(tender)

            if normalized["id"] in seen:
                duplicates += 1
                continue

            seen.add(normalized["id"])

            cleaned.append(normalized)

        print(f"Recent     : {len(cleaned)}")
        print(f"Skipped    : {skipped}")
        print(f"Duplicates : {duplicates}")

        return cleaned

    def save(self, tenders: List[Dict], output_file: str):

        Path(output_file).parent.mkdir(
            exist_ok=True,
            parents=True
        )

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                tenders,
                f,
                indent=4,
                ensure_ascii=False
            )