from PIL import Image

#Résultat du diagramme de Voronoï
diagram = {}

#Conversion du diagramme de Voronoï en image PNG
def diagram_to_png(diagram: dict) -> Image:
    png_diagram = Image.fromarray(diagram).convert("RGB")
    return png_diagram

#Exportation de l'image du diagramme de Voronoï à un format voulu
def export_diagram(png_diagram: Image, format: str):
    if format == "png":
        pass
    elif format == "jpg":
        pass
    elif format == "svg":
        pass
    else:
        raise ValueError("Format non supporté.")
    