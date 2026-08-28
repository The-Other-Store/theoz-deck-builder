"""
docprops.py - Tampon de tracabilite dans les proprietes personnalisees du .pptx.

Ecrit `docProps/custom.xml` (proprietes personnalisees OOXML) :

    OzCharteVersion = version de la charte appliquee au rendu
    OzEngineVersion = version du moteur qui a rendu le fichier

Pourquoi custom.xml et pas ailleurs :
  - `docProps/app.xml` est REECRIT par PowerPoint a chaque enregistrement
    (Application, AppVersion, TitlesOfParts) : le tampon disparaitrait des qu'un
    destinataire ouvre et sauve le deck ;
  - `docProps/core.xml` survit, mais `category` et `keywords` sont exposes a
    l'utilisateur (Fichier > Informations) : legitimement editables ;
  - une slide de colophon serait visible dans un livrable client, hors charte, et
    finirait supprimee a la main - la tracabilite disparaitrait exactement quand
    elle sert.

Les proprietes personnalisees, elles, sont preservees a l'enregistrement et
invisibles dans l'interface courante.

AUCUN horodatage n'est ecrit : le rendu doit rester reproductible octet pour octet,
sinon toute comparaison de decks de reference devient impossible.

Dependances : stdlib (zipfile) + lxml (fourni par python-pptx).
"""

from __future__ import annotations
import zipfile
from lxml import etree

_CP = "http://schemas.openxmlformats.org/officeDocument/2006/custom-properties"
_VT = "http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"
_CT = "http://schemas.openxmlformats.org/package/2006/content-types"
_PR = "http://schemas.openxmlformats.org/package/2006/relationships"
_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

_PART = "docProps/custom.xml"
_CT_PATH = "[Content_Types].xml"
_ROOT_RELS = "_rels/.rels"
_CT_CUSTOM = ("application/vnd.openxmlformats-officedocument.custom-properties+xml")
# fmtid impose par la specification pour les proprietes personnalisees.
_FMTID = "{D5CDD505-2E9C-101B-9397-08002B2CF9AE}"


def _build_custom_xml(props: dict[str, str], existing: bytes | None = None) -> bytes:
    """Construit (ou met a jour) la part des proprietes personnalisees."""
    if existing:
        root = etree.fromstring(existing)
    else:
        root = etree.Element(f"{{{_CP}}}Properties", nsmap={None: _CP, "vt": _VT})

    for name, value in props.items():
        # remplace une propriete de meme nom plutot que de la dupliquer
        for prop in root.findall(f"{{{_CP}}}property"):
            if prop.get("name") == name:
                root.remove(prop)
        # pid : 0 et 1 sont reserves, on numerote a la suite
        used = {int(p.get("pid", "1")) for p in root.findall(f"{{{_CP}}}property")}
        pid = max(used | {1}) + 1
        prop = etree.SubElement(root, f"{{{_CP}}}property",
                                {"fmtid": _FMTID, "pid": str(pid), "name": name})
        etree.SubElement(prop, f"{{{_VT}}}lpwstr").text = str(value)

    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def _ensure_content_type(ct_root) -> bool:
    for ov in ct_root.findall(f"{{{_CT}}}Override"):
        if ov.get("PartName") == "/" + _PART:
            return False
    ov = etree.SubElement(ct_root, f"{{{_CT}}}Override")
    ov.set("PartName", "/" + _PART)
    ov.set("ContentType", _CT_CUSTOM)
    return True


def _ensure_relationship(rels_root) -> bool:
    for rel in rels_root:
        if (rel.get("Target") or "").lstrip("/") == _PART:
            return False
    ids = [int(r.get("Id")[3:]) for r in rels_root
           if (r.get("Id") or "").startswith("rId") and r.get("Id")[3:].isdigit()]
    rel = etree.SubElement(rels_root, f"{{{_PR}}}Relationship")
    rel.set("Id", f"rId{(max(ids) + 1) if ids else 1}")
    rel.set("Type", f"{_REL}/custom-properties")
    rel.set("Target", _PART)
    return True


def stamp(pptx_path: str, props: dict[str, str]) -> None:
    """Ecrit `props` dans les proprietes personnalisees du .pptx (en place).

    Silencieux en cas d'echec : un tampon manquant ne doit jamais empecher la
    livraison d'un deck valide.
    """
    if not props:
        return
    try:
        with zipfile.ZipFile(pptx_path, "r") as z:
            data = {n: z.read(n) for n in z.namelist()}

        parser = etree.XMLParser(remove_blank_text=False)
        data[_PART] = _build_custom_xml(props, data.get(_PART))

        ct_root = etree.fromstring(data[_CT_PATH], parser)
        if _ensure_content_type(ct_root):
            data[_CT_PATH] = etree.tostring(ct_root, xml_declaration=True,
                                            encoding="UTF-8", standalone=True)

        rels_root = etree.fromstring(data[_ROOT_RELS], parser)
        if _ensure_relationship(rels_root):
            data[_ROOT_RELS] = etree.tostring(rels_root, xml_declaration=True,
                                              encoding="UTF-8", standalone=True)

        with zipfile.ZipFile(pptx_path, "w", zipfile.ZIP_DEFLATED) as z:
            # [Content_Types].xml en premier (convention OPC).
            z.writestr(_CT_PATH, data.pop(_CT_PATH))
            for name, payload in data.items():
                z.writestr(name, payload)
    except Exception:
        pass


def read(pptx_path: str) -> dict[str, str]:
    """Relit les proprietes personnalisees d'un .pptx. {} si absentes."""
    try:
        with zipfile.ZipFile(pptx_path) as z:
            if _PART not in z.namelist():
                return {}
            root = etree.fromstring(z.read(_PART))
    except Exception:
        return {}
    out = {}
    for prop in root.findall(f"{{{_CP}}}property"):
        name = prop.get("name")
        val = prop.find(f"{{{_VT}}}lpwstr")
        if name and val is not None:
            out[name] = val.text or ""
    return out
