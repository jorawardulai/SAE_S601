from PIL import Image

#Résultat du diagramme de Voronoï
diagram = {}

#Conversion du diagramme de Voronoï en image SVG
def diagram_to_svg(diagram: dict) -> Image:
    svg_diagram = Image.fromarray(diagram).convert("RGB")
    return svg_diagram

#Exportation de l'image du diagramme de Voronoï à un format voulu
def export_diagram(svg_diagram: Image, format: str):
    if format == "svg":
        pass
    elif format == "jpg":
        pass
    elif format == "png":
        pass
    else:
        raise ValueError("Format non supporté.")
    