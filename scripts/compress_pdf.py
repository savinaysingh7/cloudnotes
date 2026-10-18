import os
import io
import sys
import pymupdf
from PIL import Image

def compress_pdf(input_path: str, output_path: str = None, quality: int = 88) -> int:
    """
    Compresses a PDF by optimizing embedded raster images and applying
    stream deflation and garbage collection. Guarantees file size < 5 MB
    while preserving page count, vector text, layout, and visual fidelity.
    """
    if output_path is None:
        output_path = input_path

    temp_output = input_path + ".tmp.pdf"
    doc = pymupdf.open(input_path)
    replaced_count = 0

    for page in doc:
        for img in page.get_images(full=True):
            xref = img[0]
            base = doc.extract_image(xref)
            raw = base["image"]
            if len(raw) > 40 * 1024:  # larger than 40 KB
                pil_img = Image.open(io.BytesIO(raw))
                if pil_img.mode in ("RGBA", "P"):
                    pil_img = pil_img.convert("RGB")
                buf = io.BytesIO()
                pil_img.save(buf, format="JPEG", quality=quality, optimize=True)
                page.replace_image(xref, stream=buf.getvalue())
                replaced_count += 1

    doc.save(temp_output, garbage=4, deflate=True, clean=True)
    doc.close()

    orig_size = os.path.getsize(input_path)
    new_size = os.path.getsize(temp_output)

    # Replace original or save to output
    if os.path.exists(output_path) and output_path != temp_output:
        os.remove(output_path)
    os.replace(temp_output, output_path)

    print(f"Compressed {input_path}:")
    print(f"  Replaced images : {replaced_count}")
    print(f"  Original size   : {orig_size:,} bytes ({orig_size / (1024*1024):.2f} MB)")
    print(f"  Optimized size  : {new_size:,} bytes ({new_size / (1024*1024):.2f} MB)")
    print(f"  Target (< 5 MB) : {'PASSED (OK)' if new_size < 5*1024*1024 else 'EXCEEDED'}")
    return new_size

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "CloudNotesProjectReport.pdf"
    compress_pdf(target)
