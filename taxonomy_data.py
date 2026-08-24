"""Small project-specific taxonomies not sourced from DATAtourisme OWL."""

import networkx as nx

from taxonomy import Taxonomy


def build_theme_taxonomy() -> Taxonomy[str]:
    graph = nx.DiGraph(
        [
            ("All", "CulturalTheme"),
            ("All", "ParkAndGardenTheme"),
            ("All", "HealthTheme"),
            ("All", "FoodEstablishementTheme"),
            ("All", "FoodProduct"),
            ("All", "SpatialEnvironmentTheme"),
            ("All", "SportsTheme"),
            ("All", "EntertainmentAndEventTheme"),
            ("All", "CuisineCategory"),
            ("All", "RouteTheme"),
            ("RouteTheme", "CycleRouteTheme"),
            ("RouteTheme", "MTBRouteTheme"),
            ("All", "CommonAmenity"),
        ]
    )
    return Taxonomy(graph, root="All")


def build_historical_period_taxonomy() -> Taxonomy[str]:
    graph = nx.DiGraph(
        [
            ("All", "AD"),
            ("All", "BC"),
            ("AD", "Médiéval"),
            ("Médiéval", "Gothique"),
            ("Médiéval", "Roman"),
            ("AD", "Renaissance"),
            ("BC", "Antiquité"),
            ("Antiquité", "Gallo-romain"),
            ("AD", "XVII/XVIII"),
            ("XVII/XVIII", "Classique"),
            ("XVII/XVIII", "Néo-Classique"),
            ("AD", "Moderne"),
            ("Moderne", "Contemporain"),
            ("Moderne", "Xixe siècle"),
            ("Moderne", "Xxe siècle"),
        ]
    )
    return Taxonomy(graph, root="All")


THEME_TAXONOMY = build_theme_taxonomy()
HISTORICAL_PERIOD_TAXONOMY = build_historical_period_taxonomy()

__all__ = [
    "HISTORICAL_PERIOD_TAXONOMY",
    "THEME_TAXONOMY",
    "build_historical_period_taxonomy",
    "build_theme_taxonomy",
]
