from typing import List, Optional
from pydantic import BaseModel


class TenderClassification(BaseModel):

    is_software: bool

    category: str

    confidence: float

    reason: str


class TenderPDFExtraction(BaseModel):

    bid_number: Optional[str] = None

    dated: Optional[str] = None

    bid_end_datetime: Optional[str] = None

    bid_opening_datetime: Optional[str] = None

    bid_offer_validity_days: Optional[str] = None

    ministry_name: Optional[str] = None

    state_name: Optional[str] = None

    department_name: Optional[str] = None

    organisation_name: Optional[str] = None

    item_category: List[str] = []

    mse_relaxation: Optional[str] = None

    startup_relaxation: Optional[str] = None

    minimum_average_annual_turnover: Optional[str] = None

    documents_required: List[str] = []

    past_experience_required: Optional[str] = None

    bid_to_ra_enabled: Optional[str] = None

    evaluation_method: Optional[str] = None

    arbitration_clause: Optional[str] = None

    buyer_specification_document: Optional[str] = None

    tender_value: Optional[str] = None

    emd_value: Optional[str] = None