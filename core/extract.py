import pymupdf


def extract_text(pdf_file):
    doc = pymupdf.Document(pdf_file)

    num_pages = doc.page_count
    print(f"doc page count: {num_pages}")

    for page in doc:
        blist = page.get_text("blocks")
        for block in blist:
            print(block)
            r = pymupdf.Rect(block[:4])
            page.draw_rect(r, color=(1, 0, 0))

    doc.save("output.pdf")

    return True
