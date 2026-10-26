"""Function tools for the Dialog Care Copilot.

They read the fictional data in /data, so the labs run without any Dialog
back-end systems. In production these would call real billing/CRM/NOC APIs.
"""

import json
from datetime import datetime
from typing import Annotated

from agent_framework import tool
from pydantic import Field

from .config import DATA_DIR

_CUSTOMERS = {c["mobile"]: c for c in json.loads((DATA_DIR / "customers.json").read_text(encoding="utf-8"))["customers"]}
_OUTAGES = json.loads((DATA_DIR / "outages.json").read_text(encoding="utf-8"))["outages"]
_TICKETS: list[dict] = []


def _normalise(mobile: str) -> str:
    digits = "".join(ch for ch in mobile if ch.isdigit())
    if digits.startswith("94"):
        digits = "0" + digits[2:]
    return digits


def _verified(mobile: str, nic_last4: str) -> dict | None:
    customer = _CUSTOMERS.get(_normalise(mobile))
    if customer and customer["nic_last4"] == nic_last4.strip():
        return customer
    return None


@tool(approval_mode="never_require")
def verify_customer(
    mobile: Annotated[str, Field(description="Customer mobile number, e.g. 0771234501 or +94771234501")],
    nic_last4: Annotated[str, Field(description="Last 4 digits of the customer's NIC")],
) -> str:
    """Verify a customer's identity. Must succeed before any account details are shared."""
    customer = _verified(mobile, nic_last4)
    if not customer:
        return "VERIFICATION FAILED: mobile number and NIC digits do not match our records."
    return json.dumps(
        {"verified": True, "first_name": customer["first_name"], "connection": customer["connection"],
         "plan": customer["plan"], "district": customer["district"], "preferred_language": customer["language"]}
    )


@tool(approval_mode="never_require")
def get_bill(
    mobile: Annotated[str, Field(description="Verified customer mobile number")],
    nic_last4: Annotated[str, Field(description="Last 4 digits of the customer's NIC")],
    month: Annotated[str | None, Field(description="Bill month as YYYY-MM. Omit for the latest bill.")] = None,
) -> str:
    """Get a postpaid customer's bill with line items."""
    customer = _verified(mobile, nic_last4)
    if not customer:
        return "VERIFICATION FAILED: cannot share bill details."
    if customer["connection"] != "postpaid":
        return "This is a prepaid connection; there are no bills. Use get_prepaid_balance."
    bills = customer.get("bills", [])
    bill = next((b for b in bills if b["month"] == month), None) if month else (bills[-1] if bills else None)
    return json.dumps(bill) if bill else f"No bill found for {month}."


@tool(approval_mode="never_require")
def get_prepaid_balance(
    mobile: Annotated[str, Field(description="Verified customer mobile number")],
    nic_last4: Annotated[str, Field(description="Last 4 digits of the customer's NIC")],
) -> str:
    """Get a prepaid customer's balance, remaining data and package expiry."""
    customer = _verified(mobile, nic_last4)
    if not customer:
        return "VERIFICATION FAILED: cannot share balance."
    if customer["connection"] != "prepaid":
        return "This is a postpaid connection. Use get_bill."
    return json.dumps({k: customer[k] for k in ("plan", "balance_lkr", "data_left_gb", "package_expiry")})


@tool(approval_mode="never_require")
def check_network_outage(
    district: Annotated[str, Field(description="Sri Lankan district, e.g. Colombo, Kandy, Jaffna")],
) -> str:
    """Check for active network outages in a district."""
    hits = [o for o in _OUTAGES if o["district"].lower() == district.strip().lower()]
    return json.dumps(hits) if hits else f"No active outages reported in {district}."


@tool(approval_mode="never_require")
def raise_support_ticket(
    mobile: Annotated[str, Field(description="Customer mobile number")],
    category: Annotated[
        str,
        Field(description="One of MOBILE_DATA, COVERAGE, FIBRE_FAULT, BILLING_ESCALATION, HUMAN_HANDOFF"),
    ],
    summary: Annotated[str, Field(description="One-sentence summary of the problem")],
) -> str:
    """Raise a support ticket and return its reference number."""
    allowed = {"MOBILE_DATA", "COVERAGE", "FIBRE_FAULT", "BILLING_ESCALATION", "HUMAN_HANDOFF"}
    if category not in allowed:
        return f"Invalid category {category}. Use one of {sorted(allowed)}."
    ticket = {"ref": f"TKT-{len(_TICKETS) + 50231}", "mobile": _normalise(mobile), "category": category,
              "summary": summary, "created": datetime.now().isoformat(timespec="minutes")}
    _TICKETS.append(ticket)
    return json.dumps(ticket)


@tool(approval_mode="never_require")
def apply_bill_credit(
    mobile: Annotated[str, Field(description="Verified customer mobile number")],
    nic_last4: Annotated[str, Field(description="Last 4 digits of the customer's NIC")],
    amount_lkr: Annotated[int, Field(description="Credit amount in LKR")],
    reason: Annotated[str, Field(description="Why the credit is being applied")],
) -> str:
    """Apply a credit adjustment to the customer's next bill (agent limit: LKR 2,000)."""
    if not _verified(mobile, nic_last4):
        return "VERIFICATION FAILED."
    if isinstance(amount_lkr, bool) or not isinstance(amount_lkr, int) or amount_lkr <= 0:
        return "REJECTED: credit amount must be a positive whole number of LKR."
    if amount_lkr > 2000:
        return "REJECTED: above the LKR 2,000 agent limit. Raise a BILLING_ESCALATION ticket instead."
    return json.dumps({"status": "credited", "amount_lkr": amount_lkr, "reason": reason,
                       "applies_to": "next bill"})


BILLING_TOOLS = [verify_customer, get_bill, get_prepaid_balance, apply_bill_credit, raise_support_ticket]
NETWORK_TOOLS = [verify_customer, check_network_outage, raise_support_ticket]
ALL_TOOLS = [verify_customer, get_bill, get_prepaid_balance, check_network_outage, apply_bill_credit,
             raise_support_ticket]
