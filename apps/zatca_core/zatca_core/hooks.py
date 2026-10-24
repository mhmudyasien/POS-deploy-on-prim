app_name = "zatca_core"
app_title = "ZATCA Core"
app_publisher = "Your Company"
app_description = "ZATCA invoice hash chain and submission queue"
app_license = "MIT"
required_apps = ["erpnext"]

after_install = "zatca_core.install.after_install"

doc_events = {
    "Sales Invoice": {"on_submit": "zatca_core.invoice.on_submit"},
}

scheduler_events = {
    "cron": {"*/5 * * * *": ["zatca_core.queue.process_pending"]},
}
