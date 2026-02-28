import pytest
import sys
import os

# Ajout du chemin racine pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from domain.models import Point

@pytest.fixture
def sample_points():
    """Fournit un set de points de base pour les tests."""
    return [
        Point(0, 0), Point(10, 0), Point(10, 10), 
        Point(0, 10), Point(5, 5)
    ]