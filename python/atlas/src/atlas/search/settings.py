from pydantic_settings import BaseSettings

class GlobalSearchSettings(BaseSettings):
    default_limit: int = 20
    max_limit: int = 50
    max_query_characters: int = 256
    fuzzy_min_characters: int = 3
    minimum_trigram_similarity: float = 0.35
    exact_prefix_candidate_limit: int = 50
    fuzzy_candidate_limit: int = 150
