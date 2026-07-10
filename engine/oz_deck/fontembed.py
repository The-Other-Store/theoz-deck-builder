"""
fontembed.py - Embarque des polices TrueType dans un .pptx deja ecrit.

python-pptx ne sait pas embarquer de police : sans ca, un destinataire qui n'a
pas Quicksand installe verrait une substitution. On post-traite donc l'archive
OOXML pour injecter les fontes et les declarations attendues par PowerPoint :

  - parties        ppt/fonts/fontN.fntdata  (octets TTF bruts)
  - relations      ppt/_rels/presentation.xml.rels  (type .../font)
  - content-type   [Content_Types].xml  (Default fntdata)
  - presentation   <p:embeddedFontLst> + embedTrueTypeFonts="1"

Dependances : stdlib (zipfile) + lxml (fourni par python-pptx). Aucune au runtime
au-dela de ce que le moteur charge deja.

Limite honnete : l'embarquement est respecte par PowerPoint (Windows/Mac). Google
Slides / Keynote / LibreOffice / PowerPoint web peuvent l'ignorer et substituer.
"""
from __future__ import annotations
import os
import zipfile
from lxml import etree

_P = "http://schemas.openxmlformats.org/presentationml/2006/main"
_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
_CT = "http://schemas.openxmlformats.org/package/2006/content-types"
_PR = "http://schemas.openxmlformats.org/package/2006/relationships"
_FONT_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/font"

_PRES = "ppt/presentation.xml"
_PRES_RELS = "ppt/_rels/presentation.xml.rels"
_CT_PATH = "[Content_Types].xml"


def _qp(tag: str) -> str: return f"{{{_P}}}{tag}"


def _next_rid(rels_root) -> int:
    mx = 0
    for rel in rels_root:
        rid = rel.get("Id", "")
        if rid.startswith("rId") and rid[3:].isdigit():
            mx = max(mx, int(rid[3:]))
    return mx + 1


def _ensure_content_type(ct_root) -> bool:
    for d in ct_root.findall(f"{{{_CT}}}Default"):
        if (d.get("Extension") or "").lower() == "fntdata":
            return False
    d = etree.SubElement(ct_root, f"{{{_CT}}}Default")
    d.set("Extension", "fntdata")
    d.set("ContentType", "application/x-fontdata")
    return True


def _insert_embedded_font_lst(pres_root, entries):
    """entries: list of (typeface, {'regular': rid, 'bold': rid, ...})."""
    lst = etree.SubElement(pres_root, _qp("embeddedFontLst"))
    for typeface, rids in entries:
        ef = etree.SubElement(lst, _qp("embeddedFont"))
        font = etree.SubElement(ef, _qp("font"))
        font.set("typeface", typeface)
        for style in ("regular", "bold", "italic", "boldItalic"):
            if style in rids:
                el = etree.SubElement(ef, _qp(style))
                el.set(f"{{{_R}}}id", rids[style])
    # Position correcte dans CT_Presentation : apres notesSz/sldSz.
    anchor = None
    for tag in ("notesSz", "sldSz"):
        found = pres_root.find(_qp(tag))
        if found is not None:
            anchor = found
            break
    if anchor is not None:
        anchor.addnext(lst)


def embed_fonts(pptx_path: str, faces: list[dict]) -> None:
    """
    faces : [{"typeface": "Quicksand", "regular": "/path/Reg.ttf",
              "bold": "/path/Bold.ttf"}], styles optionnels: italic, boldItalic.
    Modifie le .pptx en place.
    """
    faces = [f for f in faces if any(os.path.exists(f.get(s, "")) for s in
             ("regular", "bold", "italic", "boldItalic"))]
    if not faces:
        return

    with zipfile.ZipFile(pptx_path, "r") as z:
        names = z.namelist()
        data = {n: z.read(n) for n in names}

    parser = etree.XMLParser(remove_blank_text=False)
    ct_root = etree.fromstring(data[_CT_PATH], parser)
    pres_root = etree.fromstring(data[_PRES], parser)
    rels_root = etree.fromstring(data[_PRES_RELS], parser)

    _ensure_content_type(ct_root)

    rid_n = _next_rid(rels_root)
    font_n = 1
    new_parts: dict[str, bytes] = {}
    entries = []
    for face in faces:
        rids = {}
        for style in ("regular", "bold", "italic", "boldItalic"):
            path = face.get(style)
            if not path or not os.path.exists(path):
                continue
            part = f"ppt/fonts/font{font_n}.fntdata"
            with open(path, "rb") as fh:
                new_parts[part] = fh.read()
            rid = f"rId{rid_n}"
            rel = etree.SubElement(rels_root, f"{{{_PR}}}Relationship")
            rel.set("Id", rid)
            rel.set("Type", _FONT_REL)
            rel.set("Target", f"fonts/font{font_n}.fntdata")
            rids[style] = rid
            rid_n += 1
            font_n += 1
        entries.append((face["typeface"], rids))

    # Attributs d'embarquement sur la racine.
    pres_root.set("embedTrueTypeFonts", "1")
    pres_root.set("saveSubsetFonts", "0")
    _insert_embedded_font_lst(pres_root, entries)

    data[_CT_PATH] = etree.tostring(ct_root, xml_declaration=True, encoding="UTF-8", standalone=True)
    data[_PRES] = etree.tostring(pres_root, xml_declaration=True, encoding="UTF-8", standalone=True)
    data[_PRES_RELS] = etree.tostring(rels_root, xml_declaration=True, encoding="UTF-8", standalone=True)
    data.update(new_parts)

    with zipfile.ZipFile(pptx_path, "w", zipfile.ZIP_DEFLATED) as z:
        # [Content_Types].xml en premier (convention OPC).
        z.writestr(_CT_PATH, data.pop(_CT_PATH))
        for name, payload in data.items():
            z.writestr(name, payload)
