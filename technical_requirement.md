# Option 1: **Search Price from Large PDF**

**Goal**

Build a search tool that takes one **free-form line** and returns the **base list rate (USD)** from PDF. 

> **One input → one price.**
> 

**Data Source (single source of truth)**

**Sample 1:**
https://www.fedex.com/content/dam/fedex/us-united-states/services/FedEx_Standard_List_Rates_2025.pdf

**Sample 2:**

[PriceAnnex.xlsx.pdf](attachment:4f02822e-5f1d-43db-862b-f54384d04f01:PriceAnnex.xlsx.pdf)

---

## **What you build (in 3-6 hours)**

- A function: get_price(line: str)
- A minimal way to demo it: CLI, HTTP endpoint (POST /price with { line }), or a one-field web UI.

---

## **Input (free text, one line)**

Examples we’ll send (order/synonyms vary):

- FedEx 2Day, Zone 5, 3 lb
- Standard Overnight, z2, 10 lbs, other packaging
- Express Saver Z8 1 lb
- Ground Z6 12 lb
- Home Delivery zone 3 5 lb

---

## **Requirements**

- **Prices must come from the PDF tables.**
- **Be able to process different documents using this method without code change.**

---

---

## **Deliverables**

1. **Repo link**
2. **README** (short): solution architecture, how you parsed the PDF, stored the data and find the answear.
3. **Demo and Discussion**