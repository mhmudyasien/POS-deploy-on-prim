from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

FIELDS = {
    "Sales Invoice": [
        dict(fieldname="zatca_section", label="ZATCA", fieldtype="Section Break",
             insert_after="amended_from", collapsible=1),
        dict(fieldname="zatca_status", label="ZATCA Status", fieldtype="Select",
             options="\nPending\nReported\nFailed", read_only=1, no_copy=1,
             insert_after="zatca_section"),
        dict(fieldname="zatca_hash", label="Invoice Hash", fieldtype="Data",
             read_only=1, no_copy=1, insert_after="zatca_status"),
        dict(fieldname="zatca_pih", label="Previous Invoice Hash", fieldtype="Data",
             read_only=1, no_copy=1, insert_after="zatca_hash"),
        dict(fieldname="zatca_error", label="ZATCA Error", fieldtype="Small Text",
             read_only=1, no_copy=1, insert_after="zatca_pih"),
    ]
}


def after_install():
    create_custom_fields(FIELDS, update=True)
