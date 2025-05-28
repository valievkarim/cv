import sys

import pikepdf

if __name__ == '__main__':
    with pikepdf.open(sys.argv[1]) as pdf:
        for page in pdf.pages:
            if "/Annots" in page:
                annots = page["/Annots"]
                new_annots = []
                for annot in annots:
                    print(annot)
                    annot_obj = annot  # .get_object()
                    if annot_obj.get("/Subtype") == "/Text":
                        # Annotation is note (22)
                        continue
                    elif annot_obj.get("/Subtype") == "/Popup":
                        parent = annot_obj.get("/Parent")
                        if parent and parent.get("/Subtype") == "/Text":
                            # Annotation is popup (23) linked to the note
                            continue
                    new_annots.append(annot)
                page["/Annots"] = pikepdf.Array(new_annots)
        pdf.save(sys.argv[2])
