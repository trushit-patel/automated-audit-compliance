from pydantic import BaseModel, Field
from typing import List, Optional

class AuditReport(BaseModel):  # ← Wrapper for multiple
    audit_results: List[AuditResult] = Field(..., description="List of ALL reviewed transactions")
    summary: str = Field(..., description="Overall audit findings")
    total_reviewed: int = Field(..., description="Total transactions checked")

class AuditResult(BaseModel):
    transaction_id: str = Field(..., description="Must match the input transaction_id")
    is_compliant: bool = Field(..., description="True if the transaction follows company policy, False if it violates it")
    flag_reason: Optional[str] = Field(None, description="If is_compliant is False, explain exactly why it failed. If True, leave null.")
    policy_reference: str = Field(..., description="Quote the exact sentence or section from the policy document used to make this decision")
    confidence_score: float = Field(..., description="A score from 0.0 to 1.0 indicating the AI's confidence in this assessment")

class Transaction(BaseModel):
    transaction_id: str = Field(..., description="Unique alphanumeric identifier for the transaction record.")
    employee_id: str = Field(..., description="Unique internal ID of the employee who made the purchase.")
    employee_name: str = Field(..., description="Full name of the employee.")
    department: str = Field(..., description="The internal corporate department the employee belongs to (e.g., Sales, Engineering).")
    date: str = Field(..., description="Date the transaction occurred, formatted as YYYY-MM-DD.")
    amount: float = Field(..., description="Total monetary cost of the transaction.")
    currency: str = Field(..., description="The three-letter currency code (e.g., USD, CAD, EUR).")
    category: str = Field(..., description="High-level expense category (e.g., Airfare, Meals, Lodging, Software).")
    subcategory: str = Field(..., description="Detailed breakdown of the category (e.g., Domestic Flight, Client Dinner).")
    vendor: str = Field(..., description="The name of the merchant or airline where the transaction occurred.")
    merchant_category_code: str = Field(..., description="The 4-digit MCC code standardizing the type of business the vendor is.")
    payment_method: str = Field(..., description="How the transaction was paid for (e.g., CorporateCard, PersonalCard, OutOfPocket).")
    description: str = Field(..., description="Short summary of the purchased item or service.")
    business_purpose: str = Field(..., description="Detailed justification explaining why this expense was necessary for business operations.")
    has_itemized_receipt: bool = Field(..., description="True if the employee provided a line-by-line receipt, False if missing or summary-only.")
    receipt_type: Optional[str] = Field(None, description="File format of the receipt (e.g., PDF, JPEG). Null if no receipt is attached.")
    cost_center: str = Field(..., description="The accounting code that this expense will be billed against.")
    approver_id: str = Field(..., description="Unique internal ID of the manager who approved this expense.")
    approver_role: str = Field(..., description="The corporate title of the approver (e.g., Sales Manager, VP of Engineering).")
    approved: bool = Field(..., description="True if the expense has been approved by management, False otherwise.")
    approval_level: int = Field(..., description="The authority tier of the approver (1 = Supervisor, 2 = Manager, 3 = VP/Director). Higher levels can approve larger amounts.")
    submitted_at: str = Field(..., description="Date the employee submitted the expense report, formatted as YYYY-MM-DD.")
    approved_at: Optional[str] = Field(None, description="Date the manager approved the expense, formatted as YYYY-MM-DD. Null if not yet approved.")