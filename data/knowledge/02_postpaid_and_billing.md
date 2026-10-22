# Dialog Care Copilot — Postpaid Plans & Billing (SAMPLE DATA)

> **Training data only.** Invented for the hONE × Dialog Foundry workshop.
> NOT real Dialog Axiata tariffs or policies.

## Postpaid plans

| Plan code | Name | Monthly rental (LKR, incl. taxes) | Data | Voice | Extras |
|---|---|---|---|---|---|
| POST-890 | Blaster 890 | 890 | 15 GB | 500 any-network min | — |
| POST-1690 | Blaster 1690 | 1,690 | 40 GB | Unlimited local | 2 GB roaming data in South Asia/month |
| POST-2990 | Blaster Elite | 2,990 | 100 GB | Unlimited local | 5 GB roaming data in Asia/month, free 5G priority |
| POST-FAM | Family Share 3990 | 3,990 | 150 GB shared across up to 4 SIMs | Unlimited local | Parental controls |

## Bill cycle and payment

- The bill cycle runs from the **1st to the last day of each month**. The bill is
  issued on the 3rd and is **due on the 21st** of the same month.
- Customers can pay through the MyCare app, online banking, mobile wallets, Care
  Centres, or set up **auto-debit** from a credit card or bank account.
- **Late payment**: if the bill is not paid by the due date, a late-payment fee of
  LKR 150 is added to the next bill. Outgoing services are **barred 14 days after
  the due date** if the balance is still unpaid. Incoming calls continue for a further 30 days.
- **Reconnection** happens automatically within 2 hours of full payment. No
  reconnection fee is charged for the first barring in a 12-month period;
  after that, a fee of LKR 250 applies.

## Disputes and refunds

- Customers can dispute any charge within **60 days** of the bill date.
- Billing agents can **approve credit adjustments up to LKR 2,000** without
  supervisor approval. Anything above LKR 2,000 must be escalated to a supervisor
  by raising a ticket of category `BILLING_ESCALATION`.
- Approved refunds are credited to the next bill, never paid in cash.
- Value-added service (VAS) subscriptions that the customer did not knowingly
  activate (for example, content subscriptions) are refunded in full for the
  last 2 billing cycles, and the VAS is deactivated.

## Credit limit

- New postpaid connections get a credit limit of 1.5× the monthly rental.
- When usage reaches 90 % of the credit limit, an SMS warning is sent. At 100 %,
  outgoing services are temporarily barred until a payment is made.

## Changing plans

- Upgrades take effect immediately and the rental is pro-rated.
- Downgrades take effect from the next bill cycle.
- There is no lock-in period on postpaid plans unless the customer took a
  subsidised device bundle (12- or 24-month lock-in).
