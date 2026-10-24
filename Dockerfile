ARG ERPNEXT_VERSION=version-15
FROM frappe/erpnext:${ERPNEXT_VERSION}

# Our custom app lives next to ERPNext inside the same image.
COPY --chown=frappe:frappe apps/zatca_core /home/frappe/frappe-bench/apps/zatca_core
RUN /home/frappe/frappe-bench/env/bin/pip install --no-cache-dir -e /home/frappe/frappe-bench/apps/zatca_core
