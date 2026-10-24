import hashlib

import frappe


def on_submit(doc, method=None):
    """Chain every submitted invoice to the previous one and queue it for ZATCA.

    NOTE: this hash is a tamper-evidence placeholder. The real Phase 2 hash is
    computed over the canonical signed XML and belongs in zatca_client.py.
    """
    # FOR UPDATE serialises concurrent submits so the chain never forks.
    prev = frappe.db.sql(
        "SELECT zatca_hash FROM `tabSales Invoice` "
        "WHERE zatca_hash IS NOT NULL AND zatca_hash != '' "
        "ORDER BY creation DESC LIMIT 1 FOR UPDATE"
    )
    pih = prev[0][0] if prev else "0"
    raw = f"{doc.name}|{doc.posting_date}|{doc.posting_time}|{doc.grand_total:.2f}|{pih}"
    doc.db_set(
        {
            "zatca_pih": pih,
            "zatca_hash": hashlib.sha256(raw.encode()).hexdigest(),
            "zatca_status": "Pending",
        },
        update_modified=False,
    )
