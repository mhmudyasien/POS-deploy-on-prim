def report(doc):
    """The ONLY place that talks to ZATCA (Fatoora).

    Not implemented yet. Phase 2 needs: UBL 2.1 XML, XAdES signature, CSID
    onboarding, then the Reporting API (simplified invoices) or Clearance API
    (standard invoices). Build against the ZATCA sandbox first.
    Raise an exception on any failure; the queue will retry.
    """
    raise NotImplementedError("ZATCA Phase 2 client is not implemented yet")
