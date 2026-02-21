from PIL import Image
from voronoi import calculer_diagramme

#Résultat du diagramme de Voronoï
def get_diagram():
    diagram = calculer_diagramme([(1, 2), (3, 4), (5, 6)])
    return diagram

#Conversion du diagramme de Voronoï en image PNG
def diagram_to_png(diagram: dict) -> Image:
    png_diagram = Image.fromarray(diagram).convert("RGB")
    return png_diagram

#Exportation de l'image du diagramme de Voronoï à un format voulu
def export_diagram(png_diagram: Image, format: str):
    if format == "png":
        png_diagram.save("SAE_Voronoi_idEquipe\Phase_1\src\outputs\diagram.png", "PNG")
    elif format == "jpg":
        png_diagram.save("SAE_Voronoi_idEquipe\Phase_1\src\outputs\diagram.jpg", "JPEG")
    elif format == "svg":
        pass
    else:
        raise ValueError("Format non supporté.")

diagram = get_diagram()
print(diagram)
#image = Image.open("SAE_Voronoi_idEquipe\Phase_1\src\image.png")
#export_diagram(image, "jpg")
