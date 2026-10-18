import pymupdf

doc = pymupdf.open("CloudNotesProjectReport.pdf")

# Let's inspect the entire PDF for tables
print("=== LOCATING ALL TABLES IN THE 27 PAGES ===")

# In CloudNotes_Project_Report.md, the tables are:
# 1. Tech Stack (Section 2.1)
# 2. REST API Endpoints (Section 2.2)
# 3. Prometheus Alert Rules (Section 6.2)
# 4. Grafana Dashboard Panels (Section 6.3)
# 5. Risk Assessment (Section 7.2)
# 6. Verification Summary (Section 9.2)
# 7. Course Outcomes (CO) Mapping (Section 10.1)
# 8. Project Structure (Appendix A)

tables_info = [
    ("Tech Stack", "Layer", "Purpose"),
    ("REST API Endpoints", "Endpoint", "Status"),
    ("Prometheus Alert Rules", "Alert Name", "When It Fires"),
    ("Grafana Dashboard Panels", "Panel", "What It Shows"),
    ("Risk Assessment", "Area", "Future Improvement"),
    ("Verification Summary", "What I Tested", "Result"),
    ("Course Outcomes Mapping", "CO", "How It Demonstrates"),
    ("Project Structure", "Directory / File", "Description"),
]

for name, col1, col2 in tables_info:
    matched_pages = []
    for i, page in enumerate(doc):
        text = page.get_text()
        if col1 in text and col2 in text:
            matched_pages.append(i + 1)
    print(f"{name:30}: pages {matched_pages}")
