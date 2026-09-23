"""
engine.py - Moteur de rendu deterministe (schema JSON -> .pptx natif charte OZ V2).

Charte V2 (CHARTE_TOZ_DOCUMENTS_V2) : un seul systeme visuel.
  - slides d'analyse & contenu : fond BLANC, bande orange 0,5 cm au bord gauche,
    titre capitales + trait orange 3 pt dessous, pied standardise ;
  - slides evenementielles (couverture, chapitre, fin) : fond ORANGE uni,
    logo principal blanc, chrome blanc.

Coeur reutilisable, sans IA. Appele par le serveur MCP (Cowork) comme par un
serveur Claude SDK. Toute la charte vit dans theme.py.
"""

from __future__ import annotations
import math
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION, XL_TICK_MARK
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor

from .theme import (Brand, Surface, CONTENT, EVENT, tone, glyph_hex_on,
                    CHARTE_VERSION)
from . import icons
from . import logos


# Mode de rendu. master=True quand on rend SUR le masque brande (oz_template_master)
# : fond / bande orange / trait de titre / pied sont HERITES du masque, le titre va
# dans le placeholder natif. master=False = rendu legacy (le moteur dessine tout).
_RENDER = {"master": False}
_CONTENT_LAYOUT = "OZ - Titre seul"   # disposition support des slides de contenu


# ----------------------------- helpers texte -----------------------------

def _no_shadow(shape):
    """Coupe l'ombre portee heritee du style de theme.

    `add_shape` attache un `<p:style>` qui reference les effets du theme Office :
    les cartes, traits et pastilles heritaient donc d'une ombre. La charte
    n'admet aucun effet d'ombre.
    """
    try:
        shape.shadow.inherit = False
    except Exception:
        pass
    return shape


def _shape(slide, kind, left, top, width, height):
    """Autoforme charte : jamais d'ombre portee."""
    return _no_shadow(slide.shapes.add_shape(kind, Inches(left), Inches(top),
                                             Inches(width), Inches(height)))


def _no_line(shape):
    shape.line.fill.background()


def _fill(shape, color):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    _no_line(shape)


def _round_abs(shape, radius_in: float) -> None:
    """Fixe un rayon de coin ABSOLU (pouces) sur un rectangle arrondi."""
    try:
        w = shape.width / 914400.0
        h = shape.height / 914400.0
        half = max(0.01, min(w, h) / 2.0)
        shape.adjustments[0] = max(0.0, min(0.5, radius_in / half))
    except Exception:
        pass


def _rule(slide, left, top, width, color, pt=Brand.RULE_PT):
    """Filet / trait horizontal d'epaisseur donnee en points."""
    ln = _no_shadow(slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left),
                                           Inches(top), Inches(width), Pt(pt)))
    _fill(ln, color)
    return ln


def _running_line(size: float, requested: float, bold: bool = False) -> float:
    """Interlignage effectif d'un paragraphe.

    La charte impose STRICTEMENT 1,3 a 1,4 pour le texte courant. On y ramene donc
    tout paragraphe non gras dont le corps est celui du texte courant, quelle que
    soit la valeur demandee par l'appelant : la regle devient structurelle plutot
    que rappelee a chaque appel. Titres, metriques et labels en gras gardent
    l'interlignage serre qu'on leur demande.
    """
    if bold or size is None or not (Brand.MIN_TEXT <= size <= 15.0):
        return requested
    return min(Brand.LINE_MAX, max(Brand.LINE_MIN, requested))


def _tf(box, line_spacing=Brand.LINE, anchor=MSO_ANCHOR.TOP):
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.line_spacing = line_spacing
    p.alignment = PP_ALIGN.LEFT
    return tf


def _text(slide, txt, left, top, width, height, size, color,
          bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
          line_spacing=Brand.LINE, caps=False, italic=False,
          space_before=None, space_after=None, underline=False):
    """Bloc de texte charte : Quicksand, ferrage a gauche par defaut."""
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = _tf(box, _running_line(size, line_spacing, bold), anchor)
    p = tf.paragraphs[0]
    p.alignment = align
    if space_before is not None:
        p.space_before = Pt(space_before)
    if space_after is not None:
        p.space_after = Pt(space_after)
    r = p.add_run()
    r.text = txt.upper() if caps else txt
    f = r.font
    f.size = Pt(size); f.bold = bold; f.italic = italic; f.underline = underline
    f.name = Brand.FONT; f.color.rgb = color
    return box


def _split_accent(text: str) -> tuple[str, str]:
    """Style editorial : isole le premier mot OU le concept cle a mettre en avant.

    Convention : un concept de plusieurs mots peut etre balise `*ainsi*` en tete
    de chaine. Sinon, c'est le premier mot qui porte l'accent (charte p.10).
    """
    t = (text or "").strip()
    if t.startswith("*") and t.count("*") >= 2:
        end = t.index("*", 1)
        return t[1:end], t[end + 1:]
    parts = t.split(" ", 1)
    return parts[0], (" " + parts[1] if len(parts) > 1 else "")


def _editorial(p, text, size, color, accent):
    """Ecrit un paragraphe au style editorial OZ : 1er mot/concept en gras ET en
    couleur, la suite en Regular (charte p.10)."""
    head, tail = _split_accent(text)
    r1 = p.add_run(); r1.text = head
    r1.font.bold = True; r1.font.size = Pt(size)
    r1.font.name = Brand.FONT; r1.font.color.rgb = accent
    if tail:
        r2 = p.add_run(); r2.text = tail
        r2.font.bold = False; r2.font.size = Pt(size)
        r2.font.name = Brand.FONT; r2.font.color.rgb = color


def _body(slide, text, left, top, width, height, size=Brand.BODY,
          surface: Surface = CONTENT, line_spacing=Brand.LINE, editorial=True,
          color=None, accent=None):
    """Paragraphe de corps de slide, style editorial par defaut."""
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = _tf(box, _running_line(size, line_spacing))
    p = tf.paragraphs[0]
    p.space_after = Pt(Brand.SP_BODY[1])
    col = color or surface.text
    acc = accent or surface.accent
    if editorial:
        _editorial(p, text, size, col, acc)
    else:
        r = p.add_run(); r.text = text
        r.font.size = Pt(size); r.font.name = Brand.FONT; r.font.color.rgb = col
    return box


def _bullets(slide, items, left, top, width, height, size=Brand.BODY,
             surface: Surface = CONTENT, line_spacing=Brand.LINE, marker="\u2022"):
    """Liste a puces ferree a gauche."""
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    line_spacing = _running_line(size, line_spacing)
    tf = _tf(box, line_spacing)
    for j, it in enumerate(items):
        p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
        p.line_spacing = line_spacing
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(Brand.SP_BODY[1])
        r = p.add_run(); r.text = f"{marker} {it}" if marker else str(it)
        r.font.size = Pt(size); r.font.name = Brand.FONT; r.font.color.rgb = surface.text
    return box


# --------------------------- fonds & chrome ---------------------------

_ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
def _logo(slide, left, top, height, surface: Surface, kind="secondaire"):
    """Logo officiel, ferre a gauche sur `left` (encre, marge transparente deduite).

    Charte : orange sur fond clair, blanc sur fond orange/sombre. Le noir est banni.
    Chemins, ratios et compensation d'encre vivent dans `logos.py`, qui les expose
    aussi aux consommateurs hors PowerPoint : une seule declaration.
    Retourne la largeur d'ENCRE, pour enchainer un libelle a la bonne distance.
    """
    width = logos.width_for_height(kind, height)
    ink = logos.ink_offset(kind, width)
    slide.shapes.add_picture(logos.path(kind, surface.logo_variant),
                             Inches(left - ink), Inches(top),
                             Inches(width), Inches(height))
    return width - 2 * ink


_EVENT_BG_PATH = os.path.join(_ASSETS_DIR, Brand.EVENT_BG_IMAGE)


def _event_bg(slide):
    """Slide evenementielle : fond degrade de la charte, en pleine page.

    Retour de relecture : "les pages de chapitres utilisent toutes ce fond
    degrade". Pose en premier, donc derriere tout le contenu ; couvre aussi les
    formes heritees du masque en mode masque. Repli sur l'aplat orange si l'image
    est absente.
    """
    if os.path.exists(_EVENT_BG_PATH):
        slide.shapes.add_picture(_EVENT_BG_PATH, Inches(0), Inches(0),
                                 Inches(Brand.SW), Inches(Brand.SH))
        return
    if _RENDER["master"]:
        _fill(_shape(slide, MSO_SHAPE.RECTANGLE, 0, 0, Brand.SW, Brand.SH), Brand.ORANGE)
        return
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = Brand.ORANGE


def _content_bg(slide):
    """Slide de contenu : fond uni blanc + bande orange 0,5 cm au bord gauche."""
    if _RENDER["master"]:
        return  # fond + bande herites du masque brande
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = Brand.BLANC
    band = _shape(slide, MSO_SHAPE.RECTANGLE, 0, 0, Brand.BAND_W, Brand.SH)
    _fill(band, Brand.ORANGE)


def _footer(slide, surface: Surface, page_no=None, total=None):
    """Pied standardise (charte p.16) : filet 1 pt, logo secondaire + mention a
    gauche en corps 8, type de document + pagination ferres a droite."""
    x0, x1 = Brand.FOOTER_MARGIN, Brand.SW - Brand.FOOTER_MARGIN
    right = Brand.FOOTER_RIGHT
    if page_no is not None:
        right = f"{Brand.FOOTER_RIGHT} - {page_no}"
    logo_y = Brand.FOOTER_TEXT_Y
    # En mode masque, seule la pagination est dessinee : le reste est herite.
    if not (_RENDER["master"] and not surface.on_orange):
        _rule(slide, x0, Brand.FOOTER_LINE_Y, x1 - x0, surface.rule, pt=1.0)
        lw = _logo(slide, x0, logo_y, Brand.FOOTER_LOGO, surface, "secondaire")
        # Libelle centre sur la HAUTEUR du badge (retour : "aligner THE OZ... en
        # hauteur sur le logo").
        _text(slide, Brand.FOOTER_LEFT, x0 + lw + 0.16, logo_y, 5.0,
              Brand.FOOTER_LOGO, Brand.FOOTER, surface.text_muted, caps=True,
              anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.0)
    _text(slide, right, x1 - 5.0, logo_y, 5.0, Brand.FOOTER_LOGO, Brand.FOOTER,
          surface.text_muted, align=PP_ALIGN.RIGHT, caps=True,
          anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.0)


def _title(slide, title, surface: Surface = CONTENT):
    """Titre de slide de contenu : H1 capitales bold + trait orange 3 pt dessous.

    Retour de relecture : pas de second niveau de titre sous le H1 ; le titre et
    le trait sont ferres a gauche sur la MEME verticale (le placeholder natif a
    donc son retrait interne annule dans le masque).
    """
    if _RENDER["master"] and getattr(slide.shapes, "title", None) is not None:
        slide.shapes.title.text = title
    else:
        _text(slide, title, Brand.MARGIN, Brand.TITLE_TOP, Brand.SW - Brand.MARGIN - Brand.MARGIN_R,
              Brand.TITLE_H, Brand.TITLE, surface.text, bold=True, caps=True,
              anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.1,
              space_before=Brand.SP_H1[0], space_after=Brand.SP_H1[1])
        _rule(slide, Brand.MARGIN, Brand.RULE_Y, Brand.RULE_W, Brand.ORANGE)

def _heading(slide, text, left, top, width, surface: Surface = CONTENT,
             size=Brand.HEADING, color=None):
    """H2 : intitule de bloc, bold, couleur d'accent (charte p.10)."""
    return _text(slide, text, left, top, width, 0.32, size, color or surface.accent,
                 bold=True, line_spacing=1.1,
                 space_before=Brand.SP_H2[0], space_after=Brand.SP_H2[1])


def _content_top(c=None) -> float:
    """Ordonnee de depart du contenu. Constante : le H2 sous le titre a ete retire."""
    return Brand.CONTENT_TOP


# --------------------------- composants ---------------------------

def _card(slide, left, top, width, height, fill=Brand.BLANC, border=Brand.FILET,
          radius=0.14, border_pt=1.0):
    """Carte charte (modeles p.19) : fond blanc, contour fin gris, coins arrondis."""
    card = _shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid(); card.fill.fore_color.rgb = fill
    if border is None:
        _no_line(card)
    else:
        card.line.color.rgb = border
        card.line.width = Pt(border_pt)
    _round_abs(card, radius)
    return card


def _icon(slide, left, top, size, name, color: RGBColor):
    """Icone Lucide filaire, monochrome, posee nue (sans carre)."""
    slide.shapes.add_picture(icons.icon_png(name, (color[0], color[1], color[2], 255), 260),
                             Inches(left), Inches(top), Inches(size), Inches(size))


def _icon_square(slide, left, top, size, name, fill=Brand.GRIS_TECH):
    """Carre-icone charte (p.14) : bloc 1:1, coins 4 pt, icone monochrome centree
    occupant 60 % de la surface."""
    sq = _shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, left, top, size, size)
    _fill(sq, fill)
    _round_abs(sq, Brand.ICON_RADIUS_PT / 72.0)
    glyph = icons.hex_to_rgba(glyph_hex_on(fill))
    inner = size * Brand.ICON_FILL_RATIO
    off = (size - inner) / 2
    slide.shapes.add_picture(icons.icon_png(name, glyph, 240),
                             Inches(left + off), Inches(top + off), Inches(inner), Inches(inner))
    return sq


# Pastille numerotee : le chiffre est au corps du texte courant (retour de
# relecture : "chiffre dans les puces corps 14"), la pastille est donc dimensionnee
# pour l'accueillir.
NUM_DIA = 0.38


def _num_circle(slide, left, top, dia, n, color=Brand.RUBIS, size=Brand.BODY):
    """Pastille numerotee (charte p.18) : rond rubis + chiffre blanc corps 14."""
    dia = max(dia, size / 72.0 * 1.9)
    c = _shape(slide, MSO_SHAPE.OVAL, left, top, dia, dia)
    _fill(c, color)
    tf = c.text_frame; tf.word_wrap = False
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = str(n)
    r.font.size = Pt(size); r.font.bold = True
    r.font.name = Brand.FONT; r.font.color.rgb = Brand.BLANC
    return c


def _bordered_box(slide, left, top, width, height, line_color=Brand.ORANGE, radius=0.06):
    """Cartouche a fond blanc + contour colore (callout charte)."""
    return _card(slide, left, top, width, height, fill=Brand.BLANC,
                 border=line_color, radius=radius, border_pt=1.5)


def _tile(slide, left, top, width, height, surface: Surface,
          heading=None, body=None, icon=None, icon_tone=None):
    """Tuile de contenu : carte blanche, intitule orange, corps editorial."""
    _card(slide, left, top, width, height)
    pad = 0.28; y = top + pad
    if icon:
        _icon_square(slide, left + pad, y, 0.52, icon, tone(icon_tone, Brand.GRIS_TECH))
        y += 0.72
    if heading:
        _heading(slide, heading, left + pad, y, width - 2 * pad, surface)
        y += 0.44
    if body:
        _body(slide, body, left + pad, y, width - 2 * pad, height - (y - top) - pad,
              Brand.BODY, surface, line_spacing=Brand.LINE)


def _tag(slide, left, top, width, label, value, surface: Surface, accent=False):
    """Mini colonne label (caps gris) + valeur (bold)."""
    _text(slide, label, left, top, width, 0.24, Brand.MIN_TEXT, surface.text_muted,
          caps=True, line_spacing=1.0)
    _text(slide, value, left, top + 0.26, width, 0.3, Brand.MIN_TEXT,
          Brand.ORANGE if accent else surface.text, bold=True, line_spacing=1.0)


# Les pastilles de niveau ("ELEVE / MOYEN / FAIBLE") ont ete retirees : la charte
# ne comporte pas ce composant. Les constats sont rendus en PUCES NUMEROTEES
# (pastille rubis + chiffre), conformement au modele p.18.


def _vsep(slide, x, top, height, color=Brand.FILET):
    """Separateur vertical fin (colonnes, charte p.20)."""
    ln = _no_shadow(slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x),
                                           Inches(top), Pt(1.0), Inches(height)))
    _fill(ln, color)
    return ln


def _image_ratio(path) -> float | None:
    try:
        from PIL import Image
        with Image.open(path) as im:
            iw, ih = im.size
        return (iw / ih) if ih else None
    except Exception:
        return None


def _fit_box(path, left, top, width, height, halign="center", valign="top"):
    """Rectangle CONTENU dans la boite, ratio preserve, ancre selon halign/valign.

    `add_picture` avec la seule largeur laisse la hauteur suivre le ratio : une
    capture portrait sortait alors de la diapositive. On bride donc par la
    dimension la plus contraignante. L'ancrage sert la regle de charte des
    "reperes geometriques stricts et constants" : on colle l'image au repere de
    marge (bord exterieur + haut du contenu) et on laisse le jeu se reporter sur
    la gouttiere, jamais sur la marge.
    """
    ratio = _image_ratio(path) or (width / height if height else 1.0)
    box_ratio = width / height if height else ratio
    if ratio >= box_ratio:          # plus large que la boite -> bride par la largeur
        w, h = width, width / ratio
    else:                           # plus haute -> bride par la hauteur
        w, h = height * ratio, height
    x = {"left": left,
         "right": left + width - w}.get(halign, left + (width - w) / 2)
    y = {"top": top,
         "bottom": top + height - h}.get(valign, top + (height - h) / 2)
    return x, y, w, h


def _picture(slide, path, rect):
    x, y, w, h = rect
    slide.shapes.add_picture(path, Inches(x), Inches(y), Inches(w), Inches(h))
    return rect


def _fit_picture(slide, path, left, top, width, height, halign="center", valign="top"):
    """Pose une image contenue dans sa boite et ancree. Retourne son rectangle."""
    return _picture(slide, path, _fit_box(path, left, top, width, height, halign, valign))


def _visual_split(img, top, bottom, zone_w):
    """Repartit la largeur entre colonne texte (a gauche) et visuel (a droite).

    Cale le visuel sur la marge droite et sur le haut du contenu, puis rend a la
    colonne texte la largeur que l'image n'utilise pas - une capture verticale ne
    laisse plus une poche de blanc au milieu de la slide. Retourne
    (rect_visuel, x_texte, largeur_texte).
    """
    zone_x = Brand.SW - Brand.MARGIN_R - zone_w
    if img and os.path.exists(img):
        rect = _fit_box(img, zone_x, top, zone_w, bottom - top,
                        halign="right", valign="top")
    else:
        rect = (zone_x, top, zone_w, bottom - top)
    text_w = min(Brand.MEASURE_MAX, rect[0] - Brand.MARGIN - Brand.GUTTER)
    return rect, Brand.MARGIN, max(2.0, text_w)


def _placeholder_visual(slide, left, top, width, height, label="[ VISUEL ]"):
    ph = _card(slide, left, top, width, height, fill=Brand.GRIS_TECH, border=Brand.FILET,
               radius=0.1)
    _text(slide, label, left, top + height / 2 - 0.16, width, 0.32, Brand.SMALL,
          Brand.GRIS, align=PP_ALIGN.CENTER)
    return ph


# ----------------------------- graphiques -----------------------------

def _chart_in(slide, spec, left, top, width, height, surface: Surface = CONTENT):
    """Graphique NATIF (editable) aux couleurs du camaieu utilitaire (charte p.7/8)."""
    kind = spec.get("chart_type", "bar")
    ctype = {"bar": XL_CHART_TYPE.COLUMN_CLUSTERED, "line": XL_CHART_TYPE.LINE_MARKERS,
             "pie": XL_CHART_TYPE.PIE}.get(kind, XL_CHART_TYPE.COLUMN_CLUSTERED)
    data = CategoryChartData(); data.categories = spec["categories"]
    for serie in spec["series"]:
        data.add_series(serie["name"], serie["values"])
    gframe = slide.shapes.add_chart(ctype, Inches(left), Inches(top), Inches(width),
                                    Inches(height), data)
    chart = gframe.chart
    chart.has_title = False
    try:
        chart.font.name = Brand.FONT
        chart.font.size = Pt(Brand.CHART_LABEL)
        chart.font.color.rgb = surface.text
    except Exception:
        pass

    # A 2 series comparees, la charte utilitaire demande un contraste fort :
    # moutarde + orange logo plutot que deux tons voisins du camaieu.
    palette = (Brand.CHART_PAIR if len(spec["series"]) == 2 and kind != "pie"
               else Brand.CHART_PALETTE)
    labels = spec.get("labels", True)
    for idx, ser in enumerate(chart.series):
        col = palette[idx % len(palette)]
        try:
            if kind == "line":
                ser.format.line.color.rgb = col
                ser.format.line.width = Pt(2.25)
                ser.smooth = False
                mk = ser.marker
                mk.format.fill.solid(); mk.format.fill.fore_color.rgb = col
                mk.format.line.color.rgb = col
            else:
                ser.format.fill.solid(); ser.format.fill.fore_color.rgb = col
                ser.format.line.fill.background()
        except Exception:
            pass
        if labels:
            try:
                dl = ser.data_labels
                dl.show_value = True
                # Pas de numFmt impose : `formatCode` est obligatoire des qu'on
                # ecrit l'element, et le format source convient.
                dl.font.size = Pt(Brand.CHART_LABEL)
                dl.font.name = Brand.FONT
                dl.font.bold = True
                if kind == "pie":
                    # Chiffres corps 18, CENTRES dans leur part (retour).
                    dl.font.size = Pt(Brand.PIE_LABEL)
                    dl.font.color.rgb = Brand.BLANC
                    dl.position = XL_LABEL_POSITION.CENTER
                else:
                    dl.font.color.rgb = col
                    dl.position = (XL_LABEL_POSITION.ABOVE if kind == "line"
                                   else XL_LABEL_POSITION.OUTSIDE_END)
            except Exception:
                pass

    # Camaieu par point pour un camembert monoserie (charte p.8).
    if kind == "pie":
        try:
            for i, pt_ in enumerate(chart.plots[0].series[0].points):
                pt_.format.fill.solid()
                pt_.format.fill.fore_color.rgb = palette[i % len(palette)]
                pt_.format.line.color.rgb = Brand.BLANC
                pt_.format.line.width = Pt(1.0)
        except Exception:
            pass

    show_legend = spec.get("legend", kind == "pie" or len(spec["series"]) > 1)
    chart.has_legend = bool(show_legend)
    if chart.has_legend:
        chart.legend.position = (XL_LEGEND_POSITION.RIGHT if kind == "pie"
                                 else XL_LEGEND_POSITION.BOTTOM)
        chart.legend.include_in_layout = False
        chart.legend.font.color.rgb = surface.text
        chart.legend.font.size = Pt(Brand.CHART_LEGEND)
        chart.legend.font.name = Brand.FONT

    if kind != "pie":
        try:
            cax = chart.category_axis
            cax.tick_labels.font.color.rgb = surface.text
            cax.tick_labels.font.size = Pt(Brand.CHART_LABEL)
            cax.tick_labels.font.name = Brand.FONT
            cax.format.line.color.rgb = Brand.GRIS
            cax.has_major_gridlines = False
            cax.major_tick_mark = XL_TICK_MARK.NONE
        except Exception:
            pass
        try:
            vax = chart.value_axis
            vax.tick_labels.font.color.rgb = surface.text_muted
            vax.tick_labels.font.size = Pt(Brand.CHART_LABEL)
            vax.tick_labels.font.name = Brand.FONT
            vax.has_major_gridlines = True
            vax.major_gridlines.format.line.color.rgb = Brand.FILET
            vax.major_gridlines.format.line.width = Pt(0.75)
            vax.format.line.fill.background()
            vax.major_tick_mark = XL_TICK_MARK.NONE
        except Exception:
            pass
    return chart


# ----------------------------- tableaux -----------------------------

def _table_cell(tbl, i, j, txt, *, bold, color, band, align_right, caps=False,
                size=Brand.SMALL, pad=0.08):
    cell = tbl.cell(i, j)
    cell.fill.solid(); cell.fill.fore_color.rgb = band
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    cell.margin_left = cell.margin_right = Inches(pad)
    cell.margin_top = cell.margin_bottom = 0
    p = cell.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.RIGHT if align_right else PP_ALIGN.LEFT
    r = p.add_run(); r.text = str(txt).upper() if caps else str(txt)
    r.font.size = Pt(size); r.font.name = Brand.FONT
    r.font.bold = bold; r.font.color.rgb = color


def _table(slide, headers, rows, left, top, width, *, row_h=0.34,
           size=Brand.TABLE_CELL, left_align=False, first_frac=None):
    """Tableau charte : en-tete noir/blanc capitales, bandes alternees, chiffres
    ferres a droite. Prefixe '!' = alerte rubis ; 1re cellule 'TOTAL' = gras."""
    nrows = len(rows) + 1; ncols = len(headers)
    tbl = slide.shapes.add_table(nrows, ncols, Inches(left), Inches(top),
                                 Inches(width), Inches(row_h * nrows)).table
    tbl.first_row = False; tbl.horz_banding = False
    if first_frac is None:
        first_frac = 0.24 if ncols > 3 else 0.34
    tbl.columns[0].width = Inches(width * first_frac)
    rest = Inches(width * (1 - first_frac) / max(1, ncols - 1))
    for j in range(1, ncols):
        tbl.columns[j].width = rest
    for i in range(nrows):
        tbl.rows[i].height = Inches(row_h)

    for j, h in enumerate(headers):
        _table_cell(tbl, 0, j, h, bold=True, color=Brand.BLANC, band=Brand.NOIR,
                    align_right=(not left_align and j > 0), caps=True,
                    size=Brand.TABLE_HEAD)
    for i, row in enumerate(rows):
        is_total = str(row[0]).strip().upper() == "TOTAL"
        band = Brand.GRIS_TECH if (is_total or i % 2) else Brand.BLANC
        for j, val in enumerate(row):
            txt = str(val)
            right = (not left_align) and j > 0
            if txt.startswith("!"):
                _table_cell(tbl, i + 1, j, txt[1:], bold=True, color=Brand.RUBIS,
                            band=band, align_right=right, size=size)
            elif txt.startswith("+") and right:
                _table_cell(tbl, i + 1, j, txt, bold=True, color=Brand.VERT,
                            band=band, align_right=right, size=size)
            else:
                _table_cell(tbl, i + 1, j, txt, bold=is_total, color=Brand.NOIR,
                            band=band, align_right=right, size=size)
    return row_h * nrows


def _section_band(slide, left, top, width, label, icon, h=0.4):
    """Bandeau de section noir (icone orange + intitule blanc), facon tableur."""
    bar = _shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, h)
    _fill(bar, Brand.NOIR); _round_abs(bar, 0.05)
    isz = h * 0.5
    if icon:
        # Icone en BLANC sur le bandeau noir (retour : lisibilite).
        _icon(slide, left + 0.16, top + (h - isz) / 2, isz, icon, Brand.BLANC)
    _text(slide, label, left + (0.16 + isz + 0.14 if icon else 0.2), top, width - 0.8, h,
          Brand.HEADING, Brand.BLANC, bold=True, caps=True, anchor=MSO_ANCHOR.MIDDLE,
          line_spacing=1.0)
    return h


# ----------------------------- layouts -----------------------------

def _blank(prs, event=False):
    """Nouvelle slide. En mode masque, sur la disposition 'OZ - Titre seul' ;
    les slides evenementielles perdent leurs placeholders (chrome redessine)."""
    slide = None
    if _RENDER["master"]:
        for L in prs.slide_masters[0].slide_layouts:
            if L.name == _CONTENT_LAYOUT:
                slide = prs.slides.add_slide(L)
                break
    if slide is None:
        slide = prs.slides.add_slide(prs.slide_layouts[6])
    if event:
        for ph in list(slide.placeholders):
            ph._element.getparent().remove(ph._element)
    return slide


def _event_slide(prs):
    s = _blank(prs, event=True)
    _event_bg(s)
    return s


def _content_slide(prs, c, subtitle=True):
    s = _blank(prs)
    _content_bg(s)
    _title(s, c["title"], CONTENT)
    return s


# --- slides evenementielles (fond orange) ---

# Titre de couverture / chapitre : 2 lignes maximum (retour de relecture).
_TITLE_MAX_LINES = 2


def _display_title(slide, text, top, size, accent, height=None, width=None):
    """Titre de page evenementielle : capitales, 1er mot (ou concept `*balise*`)
    dans la couleur d'accent, le reste en blanc. Retourne l'ordonnee du bas."""
    width = width or Brand.SW - Brand.MARGIN - Brand.MARGIN_R
    line_h = size * 1.12 / 72.0
    height = height or line_h * _TITLE_MAX_LINES
    box = slide.shapes.add_textbox(Inches(Brand.MARGIN), Inches(top),
                                   Inches(width), Inches(height))
    tf = _tf(box, 1.12)
    _editorial(tf.paragraphs[0], (text or "").upper(), size, Brand.BLANC, accent)
    return top, line_h


def layout_cover(prs, c, th=None):
    """Couverture : fond degrade, titre capitales corps 44 dont le 1er mot en noir,
    puis trait blanc et UN seul niveau de sous-titre juste dessous.

    Retours de relecture : pas de logo (il est au pied de page), pas de sur-titre,
    un seul niveau de sous-titre en corps 15, sous-titre et trait places sous le
    titre general.
    """
    s = _event_slide(prs)
    top = 2.55
    _, line_h = _display_title(s, c["title"], top, Brand.COVER, Brand.NOIR)
    lines = 2 if len(str(c.get("title", ""))) > 34 else 1
    y = top + line_h * lines + 0.22
    _rule(s, Brand.MARGIN, y, Brand.RULE_W, Brand.BLANC)
    if c.get("subtitle"):
        _text(s, c["subtitle"], Brand.MARGIN, y + 0.20, 11.0, 0.5, Brand.COVER_SUB,
              Brand.BLANC, line_spacing=Brand.LINE)
    return s


def layout_report_cover(prs, c, th=None):
    """Couverture de rapport : meme socle que la couverture, plus une tagline."""
    s = layout_cover(prs, c, th)
    _text(s, c.get("tagline", "Expertise, performance, croissance"),
          Brand.MARGIN, Brand.SH - 1.15, 8, 0.32, Brand.MIN_TEXT, Brand.BLANC, caps=True)
    return s


def layout_section(prs, c, th=None):
    """Intercalaire de chapitre : fond degrade, titre corps 44 dont le 1er mot en
    noir, 2e ligne optionnelle en blanc, filet blanc, legende discrete.

    `number` reste OPTIONNEL (retour : "on peut en effet ajouter une numerotation").
    """
    s = _event_slide(prs)
    line_h = Brand.SECTION * 1.12 / 72.0
    y = 2.35
    if c.get("number"):
        _text(s, str(c["number"]), Brand.MARGIN, y - 0.62, 3, 0.55, Brand.PHASE,
              Brand.NOIR, bold=True)
    _display_title(s, c["title"], y, Brand.SECTION, Brand.NOIR, height=line_h * 1.2)
    y += line_h
    if c.get("subtitle"):
        _text(s, c["subtitle"], Brand.MARGIN, y, 11.5, line_h * 1.2, Brand.SECTION,
              Brand.BLANC, bold=True, caps=True, line_spacing=1.12)
        y += line_h
    _rule(s, Brand.MARGIN, y + 0.16, Brand.RULE_W, Brand.BLANC)
    if c.get("caption"):
        _text(s, c["caption"], Brand.MARGIN, y + 0.36, 10.5, 0.36, Brand.BODY,
              Brand.BLANC)
    return s


def layout_closing(prs, c, th=None):
    """Slide de fin (charte p.23) : fond degrade, logo principal blanc, filet, URL.

    Retours de relecture : logo ET trait ferres a gauche sur la meme verticale
    (la marge transparente du PNG est compensee), et pas d'accroche au-dessus de
    l'URL. Un `headline` fourni est donc ignore.
    """
    s = _event_slide(prs)
    _logo(s, Brand.MARGIN, 2.75, 1.25, EVENT, "principal")
    _rule(s, Brand.MARGIN, 4.28, Brand.RULE_W, Brand.BLANC)
    _text(s, c.get("url", "www.the-oz.com"), Brand.MARGIN, 4.48, 6, 0.38, Brand.BODY,
          Brand.BLANC, underline=True)
    return s


# --- slides de contenu (fond blanc) ---

def layout_content(prs, c, th=None):
    """1 a 3 blocs : intitule H2 orange + corps editorial."""
    s = _content_slide(prs, c)
    y = _content_top(c)
    blocks = c.get("blocks", [])
    avail = Brand.FOOTER_LINE_Y - 0.25 - y
    per = avail / max(1, len(blocks))
    for b in blocks:
        _heading(s, b["heading"], Brand.MARGIN, y, Brand.SW - Brand.MARGIN - Brand.MARGIN_R, CONTENT)
        _body(s, b["body"], Brand.MARGIN, y + 0.4,
              Brand.SW - Brand.MARGIN - Brand.MARGIN_R, per - 0.45, Brand.BODY, CONTENT)
        y += per
    return s


def layout_tiles(prs, c, th=None):
    """2 a 4 tuiles cote a cote."""
    s = _content_slide(prs, c)
    tiles = c.get("tiles", []); n = max(1, len(tiles)); gap = 0.35
    top = _content_top(c) + 0.35
    total_w = Brand.SW - Brand.MARGIN - Brand.MARGIN_R
    tw = (total_w - gap * (n - 1)) / n
    height = Brand.FOOTER_LINE_Y - 0.3 - top
    for i, t in enumerate(tiles):
        _tile(s, Brand.MARGIN + i * (tw + gap), top, tw, height, CONTENT,
              t.get("heading"), t.get("body"), t.get("icon"), t.get("tone"))
    return s


def layout_grid(prs, c, th=None):
    """Grille de 4 a 6 tuiles courtes (2 ou 3 colonnes)."""
    s = _content_slide(prs, c)
    items = c.get("items", []); n = max(1, len(items))
    top0 = _content_top(c)
    if c.get("intro"):
        _body(s, c["intro"], Brand.MARGIN, top0, Brand.SW - Brand.MARGIN - Brand.MARGIN_R,
              0.4, Brand.BODY, CONTENT)
        top0 += 0.55
    cols = 3 if n > 4 else 2
    rows = math.ceil(n / cols)
    gap = 0.3
    total_w = Brand.SW - Brand.MARGIN - Brand.MARGIN_R
    tw = (total_w - gap * (cols - 1)) / cols
    bottom = Brand.FOOTER_LINE_Y - 0.25
    ch = (bottom - top0 - gap * (rows - 1)) / rows
    for i, it in enumerate(items):
        r, col = divmod(i, cols)
        _tile(s, Brand.MARGIN + col * (tw + gap), top0 + r * (ch + gap), tw, ch, CONTENT,
              it.get("heading"), it.get("body"), it.get("icon"), it.get("tone"))
    return s


def _kpi_tone(k) -> RGBColor:
    """Couleur d'une metrique : vert sauge (positif), rubis (negatif/alerte),
    orange (accent identitaire), noir (neutre)."""
    if k.get("tone"):
        return tone(k["tone"], Brand.NOIR)
    if k.get("accent"):
        return Brand.ORANGE
    if "positive" in k:
        return Brand.VERT if k["positive"] else Brand.RUBIS
    return Brand.NOIR


def layout_kpi(prs, c, th=None):
    """Cartes indicateurs (charte p.19) : carte blanche a contour fin, icone
    filaire coloree, metrique en grand, libelle en corps de texte."""
    s = _content_slide(prs, c)
    kpis = c.get("kpis", []); n = max(1, len(kpis)); gap = 0.4
    total_w = Brand.SW - Brand.MARGIN - Brand.MARGIN_R
    cw = (total_w - gap * (n - 1)) / n
    top = _content_top(c) + 0.45
    ch = min(3.15, Brand.FOOTER_LINE_Y - 0.45 - top)
    for i, k in enumerate(kpis):
        left = Brand.MARGIN + i * (cw + gap)
        _card(s, left, top, cw, ch)
        col = _kpi_tone(k)
        pad = 0.42
        _icon(s, left + pad, top + pad, 0.46, k.get("icon", "chart-column"), col)
        _text(s, k.get("value", ""), left + pad, top + 1.10, cw - 2 * pad, 0.95,
              Brand.KPI_VALUE, col, bold=True, line_spacing=1.0)
        _text(s, k.get("label", ""), left + pad, top + 2.18, cw - 2 * pad,
              max(0.44, ch - 2.4), Brand.KPI_LABEL, Brand.NOIR, line_spacing=Brand.LINE)
        if k.get("delta"):
            pos = k.get("positive", True)
            _text(s, k["delta"], left + pad, top + ch - 0.52, cw - 2 * pad, 0.32,
                  Brand.DELTA, Brand.VERT if pos else Brand.RUBIS, bold=True)
    return s


def layout_table(prs, c, th=None):
    """Tableau charte, CENTRE verticalement dans la zone de contenu (retour)."""
    s = _content_slide(prs, c)
    zone_top = _content_top(c)
    zone_bottom = Brand.FOOTER_LINE_Y - 0.3
    rows = c["rows"]
    nrows = len(rows) + 1
    row_h = max(0.32, min(0.46, (zone_bottom - zone_top) / nrows))
    height = row_h * nrows
    top = zone_top + max(0.0, (zone_bottom - zone_top - height) / 2)
    _table(s, c["headers"], rows, Brand.MARGIN, top,
           Brand.SW - Brand.MARGIN - Brand.MARGIN_R, row_h=row_h,
           left_align=c.get("left_align", False))
    return s


def layout_chart(prs, c, th=None):
    s = _content_slide(prs, c)
    top = _content_top(c) + 0.2
    _chart_in(s, c, Brand.MARGIN, top, Brand.SW - Brand.MARGIN - Brand.MARGIN_R,
              Brand.FOOTER_LINE_Y - 0.3 - top)
    return s


def layout_verbatim(prs, c, th=None):
    """Verbatim utilisateur (charte p.21) : citation en grand, concept cle en gras
    et en cuivre, source en gris."""
    s = _content_slide(prs, c)
    top = _content_top(c) + 0.5
    box = s.shapes.add_textbox(Inches(Brand.MARGIN), Inches(top),
                               Inches(Brand.SW - Brand.MARGIN - Brand.MARGIN_R), Inches(2.9))
    tf = _tf(box, Brand.QUOTE_LINE)
    _editorial(tf.paragraphs[0], c.get("quote", ""), Brand.QUOTE, Brand.NOIR, Brand.CUIVRE)
    if c.get("source"):
        _text(s, c["source"], Brand.MARGIN, top + 3.1,
              Brand.SW - Brand.MARGIN - Brand.MARGIN_R, 0.4, Brand.QUOTE_SOURCE,
              Brand.GRIS)
    return s


def layout_roadmap(prs, c, th=None):
    """Feuille de route (charte p.20) : colonnes de phases separees par un filet,
    intitule et soulignement pris dans le camaieu utilitaire."""
    s = _content_slide(prs, c)
    phases = c.get("phases", []); n = max(1, len(phases))
    top = _content_top(c) + 0.45
    bottom = Brand.FOOTER_LINE_Y - 0.3
    total_w = Brand.SW - Brand.MARGIN - Brand.MARGIN_R
    gap = 0.5
    cw = (total_w - gap * (n - 1)) / n
    for i, ph in enumerate(phases):
        left = Brand.MARGIN + i * (cw + gap)
        col = tone(ph.get("tone"), Brand.CHART_PALETTE[i % len(Brand.CHART_PALETTE)])
        _text(s, ph.get("heading", ""), left, top, cw, 0.44, Brand.PHASE, col,
              bold=True, caps=True, align=PP_ALIGN.CENTER, line_spacing=1.1)
        _rule(s, left, top + 0.52, cw, col, pt=2.0)
        _bullets(s, ph.get("items", []), left + 0.1, top + 0.92, cw - 0.1,
                 bottom - top - 0.92, Brand.BODY, CONTENT, line_spacing=Brand.LINE)
        if i < n - 1:
            _vsep(s, left + cw + gap / 2, top, bottom - top)
    return s


def _blocks_in(slide, blocks, left, top, width, height, surface=CONTENT,
               numbered=False):
    """Blocs heading + body empiles. `numbered` prefixe chaque bloc d'une pastille
    numerotee rubis, comme les constats du modele p.18 de la charte."""
    n = max(1, len(blocks)); per = height / n
    dia = NUM_DIA
    indent = (dia + 0.24) if numbered else 0.0
    y = top
    for i, b in enumerate(blocks):
        if numbered:
            _num_circle(slide, left, y + 0.02, dia, i + 1)
        _heading(slide, b["heading"], left + indent, y, width - indent, surface)
        _body(slide, b["body"], left + indent, y + 0.40, width - indent, per - 0.48,
              Brand.BODY, surface)
        y += per


def _cards_in(slide, cards, left, top, width, height, surface=CONTENT):
    n = max(1, len(cards)); gap = 0.2
    ch = (height - gap * (n - 1)) / n; y = top
    for cd in cards:
        _card(slide, left, y, width, ch, radius=0.1)
        pad = 0.22; yy = y + pad * 0.8
        if cd.get("heading"):
            _heading(slide, cd["heading"], left + pad, yy, width - 2 * pad, surface)
            yy += 0.34
        if cd.get("body"):
            _body(slide, cd["body"], left + pad, yy, width - 2 * pad,
                  y + ch - yy - pad * 0.5, Brand.MIN_TEXT, surface,
                  line_spacing=Brand.LINE)
        y += ch + gap


_RATIO = {"half": 0.5, "third": 0.34, "two-thirds": 0.64}


def layout_split(prs, c, th=None):
    """Colonne visuelle (graphique / capture) + colonne texte."""
    s = _content_slide(prs, c)
    top = _content_top(c) + 0.2
    bottom = Brand.FOOTER_LINE_Y - 0.3
    height = bottom - top
    total_w = Brand.SW - Brand.MARGIN - Brand.MARGIN_R
    gutter = 0.5
    frac = _RATIO.get(c.get("ratio", "half"), 0.5)
    left = c.get("left", {}); right = c.get("right", {})
    vis_w = total_w * frac - gutter / 2
    txt_w = total_w - vis_w - gutter
    if not c.get("swap", False):
        vis_x = Brand.MARGIN; txt_x = Brand.MARGIN + vis_w + gutter
    else:
        txt_x = Brand.MARGIN; vis_x = Brand.MARGIN + txt_w + gutter

    if "chart" in left:
        _chart_in(s, left["chart"], vis_x, top, vis_w, height)
    elif left.get("image") and os.path.exists(left["image"]):
        # bord exterieur : marge gauche si le visuel est a gauche, marge droite sinon
        _fit_picture(s, left["image"], vis_x, top, vis_w, height,
                     halign=("right" if c.get("swap", False) else "left"),
                     valign="top")
    else:
        _placeholder_visual(s, vis_x, top, vis_w, height)

    if "cards" in right:
        _cards_in(s, right["cards"], txt_x, top, txt_w, height)
    elif "blocks" in right:
        _blocks_in(s, right["blocks"], txt_x, top, txt_w, height,
                   numbered=c.get("numbered", False))
    return s


def layout_capture(prs, c, th=None):
    """Analyse de capture (charte p.18) : constats numerotes a gauche (pastilles
    rubis), capture client a droite."""
    s = _content_slide(prs, c)
    top = _content_top(c)
    bottom = Brand.FOOTER_LINE_Y - 0.3
    img = c.get("image")
    rect, lx, lw = _visual_split(img, top, bottom, 6.4)
    if img and os.path.exists(img):
        _picture(s, img, rect)
    else:
        _placeholder_visual(s, *rect, "[ CAPTURE CLIENT ]")
    y = top + 0.5
    _heading(s, c.get("intro", "Points de blocage identifies"), lx, y, lw, CONTENT)
    y += 0.6
    frictions = c.get("frictions", [])
    n = max(1, len(frictions))
    per = min(1.15, (bottom - y) / n)
    dia = NUM_DIA
    for i, fr in enumerate(frictions):
        _num_circle(s, lx, y + 0.05, dia, i + 1)
        _body(s, fr["label"], lx + dia + 0.24, y, lw - dia - 0.24, per - 0.15,
              Brand.BODY, CONTENT, line_spacing=1.4, editorial=False)
        y += per
    return s


def layout_recommendations(prs, c, th=None):
    """Recommandations : rangees carre-icone + titre + impact/effort/priorite +
    actions, plus une ligne 'objectif global' optionnelle."""
    number = c.get("number")
    heading = f"{number}  {c['title']}" if number else c["title"]
    s = _content_slide(prs, {"title": heading, "subtitle": c.get("subtitle")})
    items = c.get("items", [])
    objective = c.get("objective")
    top0 = _content_top(c)
    bottom = Brand.FOOTER_LINE_Y - 0.25
    n = max(1, len(items)); gap = 0.22
    rows_total = n + (1 if objective else 0)
    rowh = (bottom - top0 - gap * (rows_total - 1)) / rows_total
    total_w = Brand.SW - Brand.MARGIN - Brand.MARGIN_R
    y = top0
    for it in items:
        _card(s, Brand.MARGIN, y, total_w, rowh, radius=0.08)
        pad = 0.26
        isz = min(0.66, rowh * 0.5)
        fill = tone(it.get("tone"), Brand.ORANGE if it.get("accent") else Brand.NOIR)
        _icon_square(s, Brand.MARGIN + pad, y + (rowh - isz) / 2, isz,
                     it.get("icon", "circle-check-big"), fill)
        title_x = Brand.MARGIN + pad + isz + 0.25
        _text(s, it.get("title", ""), title_x, y, 3.3, rowh, Brand.MIN_HEADING,
              Brand.NOIR, bold=True, anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.15)
        tags_x = title_x + 3.45
        tw = 1.15
        ty = y + (rowh - 0.52) / 2
        cols = [("IMPACT", it.get("impact", "-"), False),
                ("EFFORT", it.get("effort", "-"), False),
                ("PRIORITE", str(it.get("priority", "-")), True)]
        for k, (lab, val, acc) in enumerate(cols):
            _tag(s, tags_x + k * tw, ty, tw, lab, val, CONTENT, accent=acc)
        act_x = tags_x + 3 * tw + 0.25
        act_w = Brand.SW - Brand.MARGIN_R - pad - act_x
        box = s.shapes.add_textbox(Inches(act_x), Inches(y + pad * 0.5), Inches(act_w),
                                   Inches(rowh - pad))
        act_ls = _running_line(Brand.MIN_TEXT, 1.2)
        tf = _tf(box, act_ls, MSO_ANCHOR.MIDDLE)
        for j, a in enumerate(it.get("actions", [])):
            p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
            p.line_spacing = act_ls; p.alignment = PP_ALIGN.LEFT
            r = p.add_run(); r.text = "\u2022 " + a
            r.font.size = Pt(Brand.MIN_TEXT); r.font.name = Brand.FONT
            r.font.color.rgb = Brand.NOIR
        y += rowh + gap
    if objective:
        obj = objective if isinstance(objective, dict) else {"body": str(objective)}
        isz = min(0.6, rowh * 0.55)
        _icon(s, Brand.MARGIN + 0.06, y + (rowh - isz) / 2, isz,
              obj.get("icon", "circle-check-big"), Brand.VERT)
        lx2 = Brand.MARGIN + 0.06 + isz + 0.3
        _text(s, obj.get("label", "Objectif global"), lx2, y, 2.6, rowh,
              Brand.MIN_HEADING, Brand.NOIR, bold=True, caps=True,
              anchor=MSO_ANCHOR.MIDDLE)
        _text(s, obj.get("body", ""), lx2 + 2.7, y,
              total_w - (lx2 - Brand.MARGIN) - 2.8, rowh, Brand.MIN_HEADING,
              Brand.NOIR, anchor=MSO_ANCHOR.MIDDLE, line_spacing=Brand.LINE)
    return s


def layout_audit(prs, c, th=None):
    """Audit CRO complet : resume + impact chiffre + frictions a gauche, capture
    annotee a droite."""
    s = _content_slide(prs, c)
    top = _content_top(c)
    bottom = Brand.FOOTER_LINE_Y - 0.25
    img = c.get("image")
    zone, lx, lw = _visual_split(img, top, bottom, 5.8)
    if img and os.path.exists(img):
        _picture(s, img, zone)
    else:
        _placeholder_visual(s, *zone, "[ CAPTURE CLIENT ]")
    zx, zy, zw, zh = zone
    for a in c.get("annotations", []):
        dia = NUM_DIA
        ax = zx + float(a.get("x", 0.5)) * zw - dia / 2
        ay = zy + float(a.get("y", 0.5)) * zh - dia / 2
        _num_circle(s, ax, ay, dia, a.get("n", "1"))
    y = top
    if c.get("summary"):
        _card(s, lx, y, lw, 1.15, radius=0.1)
        _icon_square(s, lx + 0.22, y + 0.2, 0.42, "trending-up", Brand.GRIS_TECH)
        _text(s, "Resume executif", lx + 0.78, y + 0.18, lw - 1.0, 0.26,
              Brand.MIN_HEADING, Brand.GRIS, caps=True, bold=True)
        _body(s, c["summary"], lx + 0.78, y + 0.48, lw - 1.0, 0.64, Brand.SMALL,
              CONTENT, line_spacing=Brand.LINE, editorial=False)
        y += 1.4
    impacts = c.get("impact", [])
    if impacts:
        _card(s, lx, y, lw, 1.3, radius=0.1)
        _text(s, "Impact estime", lx + 0.25, y + 0.14, lw - 0.5, 0.26,
              Brand.MIN_HEADING, Brand.GRIS, caps=True, bold=True)
        m = len(impacts); iw = (lw - 0.5) / m
        for k, imp in enumerate(impacts):
            ix = lx + 0.25 + k * iw
            _text(s, imp.get("label", ""), ix, y + 0.46, iw - 0.12, 0.3, Brand.MIN_TEXT,
                  Brand.GRIS, caps=True, line_spacing=1.05)
            _text(s, imp.get("value", ""), ix, y + 0.76, iw - 0.12, 0.44, Brand.PHASE,
                  tone(imp.get("tone"), Brand.VERT), bold=True, line_spacing=1.0)
        y += 1.5
    _heading(s, "Principales frictions identifiees", lx, y, lw, CONTENT)
    y += 0.42
    frictions = c.get("frictions", [])
    if frictions:
        n = len(frictions)
        per = min(0.82, (bottom - y) / n)
        dia = NUM_DIA
        for i, fr in enumerate(frictions):
            _num_circle(s, lx, y + 0.04, dia, i + 1)
            _text(s, fr["label"], lx + dia + 0.24, y, lw - dia - 0.24, per - 0.1,
                  Brand.BODY, Brand.NOIR, line_spacing=1.35)
            y += per
    return s


# `_meta_box` (cartouche Client/Periode) et `_tabs` (barre d'onglets) ont ete
# retires : la relecture les juge hors charte et sans apport.


def layout_dashboard(prs, c, th=None):
    """Tableau de bord dense : sections a bandeau noir + tables charte."""
    s = _content_slide(prs, c)
    sections = c.get("sections", [])
    top0 = _content_top(c)
    bottom = Brand.FOOTER_LINE_Y - 0.2
    band_h = 0.42; band_gap = 0.14; sec_gap = 0.3
    total_datarows = sum(len(sec.get("rows", [])) + 1 for sec in sections) or 1
    fixed = len(sections) * (band_h + band_gap) + max(0, len(sections) - 1) * sec_gap
    row_h = max(0.28, min(0.36, (bottom - top0 - fixed) / total_datarows))
    total_w = Brand.SW - Brand.MARGIN - Brand.MARGIN_R
    y = top0
    for sec in sections:
        _section_band(s, Brand.MARGIN, y, total_w, sec.get("heading", ""), sec.get("icon"),
                      h=band_h)
        y += band_h + band_gap
        y += _table(s, sec.get("headers", []), sec.get("rows", []), Brand.MARGIN, y,
                    total_w, row_h=row_h) + sec_gap
    return s


def _attention(slide, att, top, height):
    """Callout d'attention : cartouche a contour rubis (alerte)."""
    _bordered_box(slide, Brand.MARGIN, top, Brand.SW - Brand.MARGIN - Brand.MARGIN_R,
                  height, line_color=Brand.RUBIS, radius=0.06)
    _text(slide, att.get("title", "Points d'attention prioritaires"),
          Brand.MARGIN + 0.3, top + 0.14, Brand.SW - Brand.MARGIN - Brand.MARGIN_R - 0.6,
          0.3, Brand.MIN_HEADING, Brand.RUBIS, bold=True, caps=True)
    _bullets(slide, att.get("items", []), Brand.MARGIN + 0.3, top + 0.52,
             Brand.SW - Brand.MARGIN - Brand.MARGIN_R - 0.6, height - 0.6,
             Brand.MIN_TEXT, CONTENT, line_spacing=Brand.LINE)


def layout_summary(prs, c, th=None):
    """Synthese executive : blocs editoriaux + callout d'attention."""
    number = c.get("number")
    heading = f"{number}  {c['title']}" if number else c["title"]
    s = _content_slide(prs, {"title": heading, "subtitle": c.get("subtitle")})
    top0 = _content_top(c)
    bottom = Brand.FOOTER_LINE_Y - 0.25
    att = c.get("attention")
    att_h = (0.62 + 0.3 * max(1, len(att.get("items", [])))) if att else 0.0
    blocks = c.get("blocks", [])
    area_bottom = bottom - (att_h + 0.3 if att else 0)
    n = max(1, len(blocks)); per = (area_bottom - top0) / n
    y = top0
    for b in blocks:
        _heading(s, b["heading"], Brand.MARGIN, y, Brand.SW - Brand.MARGIN - Brand.MARGIN_R, CONTENT)
        _body(s, b["body"], Brand.MARGIN, y + 0.42,
              Brand.SW - Brand.MARGIN - Brand.MARGIN_R, per - 0.48, Brand.BODY, CONTENT)
        y += per
    if att:
        _attention(s, att, bottom - att_h, att_h)
    return s


def _perf_card(slide, left, top, w, h, k):
    """Carte KPI compacte.

    Retour de relecture : pas de tuile pleine ; c'est le CONTENU qui se colorise
    (comme les cartes indicateurs). `accent: true` colore donc la metrique en
    orange au lieu de remplir la carte.
    """
    _card(slide, left, top, w, h, radius=0.12)
    val_col = _kpi_tone(k)
    pad = 0.26
    _icon(slide, left + pad, top + pad, 0.42, k.get("icon", "chart-column"), val_col)
    _text(slide, k.get("value", ""), left + pad, top + 0.78, w - 2 * pad, 0.66,
          Brand.KPI_VALUE - 12, val_col, bold=True, line_spacing=1.0)
    _text(slide, k.get("label", ""), left + pad, top + 1.46, w - 2 * pad, 0.44,
          Brand.KPI_LABEL, Brand.NOIR, line_spacing=1.25)
    if k.get("delta"):
        pos = k.get("positive", True)
        _text(slide, k["delta"], left + pad, top + h - 0.38, w - 2 * pad, 0.3,
              Brand.DELTA, Brand.VERT if pos else Brand.RUBIS, bold=True)


def layout_performance(prs, c, th=None):
    """Indicateurs cles : rangee de cartes KPI compactes + tableau charte."""
    number = c.get("number")
    heading = f"{number}  {c['title']}" if number else c["title"]
    s = _content_slide(prs, {"title": heading, "subtitle": c.get("subtitle")})
    top0 = _content_top(c)
    total_w = Brand.SW - Brand.MARGIN - Brand.MARGIN_R
    y = top0
    kpis = c.get("kpis", [])
    if kpis:
        ch = 2.3; gap = 0.35; n = len(kpis)
        cw = (total_w - gap * (n - 1)) / n
        for i, k in enumerate(kpis):
            _perf_card(s, Brand.MARGIN + i * (cw + gap), top0, cw, ch, k)
        y = top0 + ch + 0.4
    if c.get("headers") and c.get("rows") is not None:
        rows = c["rows"]
        row_h = min(0.36, (Brand.FOOTER_LINE_Y - 0.25 - y) / max(1, len(rows) + 1))
        _table(s, c["headers"], rows, Brand.MARGIN, y, total_w,
               row_h=max(0.28, row_h))
    return s


def layout_analysis(prs, c, th=None):
    """Analyse detaillee : constats a carre-icone (gauche) + graphique (droite)
    + callout d'attention."""
    number = c.get("number")
    heading = f"{number}  {c['title']}" if number else c["title"]
    s = _content_slide(prs, {"title": heading, "subtitle": c.get("subtitle")})
    top0 = _content_top(c)
    bottom = Brand.FOOTER_LINE_Y - 0.25
    att = c.get("attention")
    att_h = (0.6 + 0.3 * max(1, len(att.get("items", [])))) if att else 0.0
    body_bottom = bottom - (att_h + 0.28 if att else 0)
    gutter = 0.5
    left_w = (Brand.SW - Brand.MARGIN - Brand.MARGIN_R) * 0.42
    right_x = Brand.MARGIN + left_w + gutter
    right_w = Brand.SW - Brand.MARGIN_R - right_x
    _section_band(s, Brand.MARGIN, top0, left_w,
                  c.get("summary_label", "Executive summary"), None, h=0.4)
    fy0 = top0 + 0.62
    findings = c.get("findings", [])
    n = max(1, len(findings)); per = (body_bottom - fy0) / n
    y = fy0
    for f in findings:
        isz = min(0.5, per * 0.42)
        fill = tone(f.get("tone"), Brand.ORANGE if f.get("accent") else Brand.NOIR)
        _icon_square(s, Brand.MARGIN, y, isz, f.get("icon", "search"), fill)
        _text(s, f.get("label", ""), Brand.MARGIN + isz + 0.22, y, left_w - isz - 0.22,
              0.3, Brand.MIN_HEADING, Brand.ORANGE, bold=True, caps=True)
        _body(s, f.get("body", ""), Brand.MARGIN + isz + 0.22, y + 0.34,
              left_w - isz - 0.22, per - 0.44, Brand.MIN_TEXT, CONTENT,
              line_spacing=Brand.LINE)
        y += per
    if c.get("chart"):
        _chart_in(s, c["chart"], right_x, top0, right_w, body_bottom - top0)
    if att:
        _attention(s, att, bottom - att_h, att_h)
    return s


LAYOUTS = {
    "cover": layout_cover, "section": layout_section, "content": layout_content,
    "tiles": layout_tiles, "grid": layout_grid, "kpi": layout_kpi, "table": layout_table,
    "chart": layout_chart, "split": layout_split, "capture": layout_capture,
    "recommendations": layout_recommendations, "audit": layout_audit,
    "closing": layout_closing, "dashboard": layout_dashboard, "summary": layout_summary,
    "report-cover": layout_report_cover, "performance": layout_performance,
    "analysis": layout_analysis, "roadmap": layout_roadmap, "verbatim": layout_verbatim,
}

# Slides evenementielles : fond orange, chrome blanc, pas de pagination.
_EVENT_LAYOUTS = {"cover", "section", "closing", "report-cover"}


# ----------------------------- build -----------------------------

def resolve_images(schema: dict, base_dir: str) -> dict:
    """Rend absolus les chemins d'images RELATIFS d'un plan, depuis `base_dir`.

    Le moteur ne teste que `os.path.exists` : un plan versionne qui reference
    `dev/samples/images/x.png` ne se rendrait donc que depuis la racine du depot.
    Les adaptateurs (CLI, preview, tests) appellent ceci pour s'affranchir du
    repertoire courant. Le champ `image` vit au premier niveau du slide pour
    `capture` / `audit`, mais sous `left` pour `split` : on descend partout.
    """
    def walk(node):
        if isinstance(node, dict):
            for key, val in node.items():
                if (key == "image" and isinstance(val, str) and val
                        and not val.startswith(("asset://", "http://", "https://"))
                        and not os.path.isabs(val)):
                    node[key] = os.path.normpath(os.path.join(base_dir, val))
                else:
                    walk(val)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(schema.get("slides", []))
    return schema


_TEMPLATE_MASTER = os.path.join(_ASSETS_DIR, "oz_template_master.pptx")
_TEMPLATE_THEME = os.path.join(_ASSETS_DIR, "oz_template.pptx")


def build(schema: dict, output_path: str, template: str | None = None) -> str:
    """Point d'entree : schema dict -> fichier .pptx charte V2.

    Si le masque brande `oz_template_master.pptx` est present, le deck herite du
    masque (fond blanc, bande orange, trait de titre, pied) et les titres vont
    dans les placeholders natifs. Sinon le moteur dessine tout (mode legacy),
    rendu identique.

    Cle racine `embed_fonts` (defaut FAUX) : embarquer Quicksand dans le .pptx.
    PowerPoint pour le WEB (Teams, Office en ligne) ne sait pas traiter les
    polices embarquees et REFUSE D'OUVRIR un fichier qui en contient - verifie par
    bisection : toutes nos variantes avec police echouent, toutes celles sans
    s'ouvrent. Le defaut est donc l'ouvrabilite partout ; l'embarquement reste
    disponible pour un deck distribue uniquement en client lourd, ou la fidelite
    typographique prime.
    """
    if template:                                       # template explicite -> legacy
        tpl, master = template, False
    elif os.path.exists(_TEMPLATE_MASTER):
        tpl, master = _TEMPLATE_MASTER, True
    elif os.path.exists(_TEMPLATE_THEME):
        tpl, master = _TEMPLATE_THEME, False
    else:
        tpl, master = None, False
    _RENDER["master"] = master
    try:
        prs = Presentation(tpl) if tpl else Presentation()
        prs.slide_width = Inches(Brand.SW); prs.slide_height = Inches(Brand.SH)
        slides = schema.get("slides", [])
        total = len(slides)
        for idx, sl in enumerate(slides, start=1):
            layout = sl.get("layout")
            fn = LAYOUTS.get(layout)
            if fn is None:
                raise ValueError(f"Layout inconnu : {layout!r}")
            s = fn(prs, sl, None)
            # Pagination sur TOUTES les slides, y compris evenementielles
            # (retour de relecture : "integrer la pagination").
            surface = EVENT if layout in _EVENT_LAYOUTS else CONTENT
            _footer(s, surface, page_no=idx, total=total)
        prs.save(output_path)
    finally:
        _RENDER["master"] = False
    if schema.get("embed_fonts", False):
        _embed_charter_font(output_path)
    _stamp_charter(output_path)
    return output_path


def _stamp_charter(output_path: str) -> None:
    """Tamponne la version de charte et celle du moteur dans le .pptx.

    Permet de rattacher un livrable a une charte precise, et de detecter une
    divergence entre deux consommateurs du moteur. Aucun horodatage : le rendu
    doit rester reproductible octet pour octet.
    """
    from . import docprops
    from . import __version__ as engine_version
    docprops.stamp(output_path, {
        "OzCharteVersion": CHARTE_VERSION,
        "OzEngineVersion": engine_version,
    })


_FONT_DIR = os.path.join(_ASSETS_DIR, "fonts")


def _embed_charter_font(output_path: str) -> None:
    """Embarque Quicksand (Regular + Bold) dans le .pptx si les fontes sont la.

    Garantit la charte chez un destinataire qui n'a pas la police installee, MAIS
    rend le fichier inouvrable en PowerPoint web (voir `build`). N'est appele que
    si le plan porte `"embed_fonts": true`.
    Silencieux si les .ttf sont absents : le deck reste valide."""
    reg = os.path.join(_FONT_DIR, "Quicksand-Regular.ttf")
    bold = os.path.join(_FONT_DIR, "Quicksand-Bold.ttf")
    if not (os.path.exists(reg) and os.path.exists(bold)):
        return
    try:
        from . import fontembed
        fontembed.embed_fonts(output_path, [
            {"typeface": Brand.FONT, "regular": reg, "bold": bold},
        ])
    except Exception:
        pass
