import shutil
import sys

import pikepdf


def patch_type3_tounicode_to_space(pdf_path, output_path):
    # space_hex = "<0020>"
    space_hex = "<200C>"

    updated = 0

    with pikepdf.open(pdf_path) as pdf:
        for page in pdf.pages:
            resources = page.get("/Resources", {})
            fonts = resources.get("/Font", {})
            print('fonts', fonts)
            for fk, font in fonts.items():
                if font.get("/Subtype") != "/Type3":
                    continue

                # Optional: check FontDescriptor/FontName
                descriptor = font.get("/FontDescriptor", {})
                fontname = descriptor.get("/FontName", None)
                print('fontname', fontname)
                if fontname and "Emoji" not in str(fontname):
                    continue

                if "/ToUnicode" not in font:
                    print('no ToUnicode')
                    sys.exit(1)

                cmap_stream = font["/ToUnicode"]  # pdf.open_stream(font["/ToUnicode"])
                lines = cmap_stream.read_bytes().decode("latin1").splitlines()
                print('lines')
                print('\n'.join(lines))
                print()
                #                return
                new_lines = []
                inside_bfchar = False
                for line in lines:
                    stripped = line.strip()

                    if stripped.endswith("beginbfchar"):
                        inside_bfchar = True
                        new_lines.append(line)
                        continue
                    if stripped == "endbfchar":
                        inside_bfchar = False
                        new_lines.append(line)
                        continue

                    if inside_bfchar and stripped.startswith("<") and ">" in stripped:
                        parts = stripped.split()
                        if len(parts) == 2 and parts[0].startswith("<") and parts[1].startswith("<"):
                            line = f"{parts[0]} {space_hex}"

                    new_lines.append(line)

                print('new_lines')
                print('\n'.join(new_lines))
                print()
                if new_lines != lines:
                    #                font["/ToUnicode"].set_stream("\n".join(new_lines).encode("latin1"))
                    font["/ToUnicode"].write("\n".join(new_lines).encode("latin1"))
                    updated += 1
                else:
                    print('new_lines == lines')

        if updated > 0:
            print(f'updated {updated} cmaps, saving to {output_path}')
            pdf.save(output_path)
        else:
            print('no updates done, just copying to', output_path)
            shutil.copy(pdf_path, output_path)


if __name__ == "__main__":
    patch_type3_tounicode_to_space(sys.argv[1], sys.argv[2])
