import os
import zipfile
import pymupdf

def render_preview_pages(pdf_path: str, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    doc = pymupdf.open(pdf_path)
    print(f"Rendering {len(doc)} pages from {pdf_path} to {out_dir}...")
    for idx, page in enumerate(doc):
        pix = page.get_pixmap(dpi=150)
        out_path = os.path.join(out_dir, f"page_{idx+1:02d}.png")
        pix.save(out_path)
    print(f"Rendered {len(doc)} pages.")

def create_source_package(zip_path: str):
    print(f"Creating source package {zip_path}...")
    files_to_add = [
        "CloudNotesProjectReport.pdf",
        "CloudNotes_Project_Report.md",
    ]
    dirs_to_add = [
        "diagrams",
        "screenshots",
        "assets",
        "scripts",
        "docs/report_pages",
    ]

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for f in files_to_add:
            if os.path.exists(f):
                z.write(f, arcname=f)
                print(f"  Added {f}")
        for d in dirs_to_add:
            if not os.path.exists(d):
                continue
            for root, _, files in os.walk(d):
                if "__pycache__" in root:
                    continue
                for file in files:
                    full_p = os.path.join(root, file)
                    rel_p = os.path.relpath(full_p, ".")
                    z.write(full_p, arcname=rel_p.replace("\\", "/"))
                    print(f"  Added {rel_p}")

    print(f"Package created: {os.path.getsize(zip_path):,} bytes")

if __name__ == "__main__":
    render_preview_pages("CloudNotesProjectReport.pdf", "docs/report_pages")
    create_source_package("CloudNotes_Project_Report_Source_Package.zip")
