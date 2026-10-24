import frappe

from zatca_core import zatca_client


def process_pending(limit=50):
    """Runs every 5 minutes. Sends queued invoices to ZATCA in order.

    Enable per site:  bench --site <site> set-config zatca_enabled 1
    Stops at the first failure (e.g. no internet) and retries on the next run.
    """
    if not frappe.conf.get("zatca_enabled"):
        return

    names = frappe.get_all(
        "Sales Invoice",
        filters={"docstatus": 1, "zatca_status": ["in", ["Pending", "Failed"]]},
        order_by="creation asc",
        limit=limit,
        pluck="name",
    )
    for name in names:
        doc = frappe.get_doc("Sales Invoice", name)
        try:
            zatca_client.report(doc)
        except Exception as e:
            doc.db_set({"zatca_status": "Failed", "zatca_error": str(e)[:500]},
                       update_modified=False)
            frappe.db.commit()
            break
        doc.db_set({"zatca_status": "Reported", "zatca_error": ""},
                   update_modified=False)
        frappe.db.commit()
