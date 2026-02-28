# Fichier: presentation/gradients.py
import numpy as np
from typing import List, Tuple
from domain.models import Point

class GradientManager:
    """Gère l'assignation de couleurs aux cellules pour créer un dégradé continu."""
    
    @staticmethod
    def get_color_for_point(point: Point, min_p: Point, max_p: Point) -> Tuple[float, float, float]:
        """Calcule une couleur (R,G,B) basée sur la position du point."""
        
        # Plages de coordonnées (avec sécurité anti-division par zéro)
        range_x = (max_p.x - min_p.x) if (max_p.x - min_p.x) > 0 else 1.0
        range_y = (max_p.y - min_p.y) if (max_p.y - min_p.y) > 0 else 1.0
        
        # Normalisation entre 0.0 et 1.0
        # Canal Rouge (R) = dépend de X
        r = (point.x - min_p.x) / range_x
        # Canal Vert (G) = dépend de Y
        g = (point.y - min_p.y) / range_y
        
        # Canal Bleu (B) = constante (ex: 0.8 pour un côté plus 'frais')
        # On s'assure que r et g sont bien dans [0.0, 1.0] avec clip()
        return (np.clip(r, 0.0, 1.0), np.clip(g, 0.0, 1.0), 0.8)