from .hero_model import HeroPublicWithTeam, HeroPublic
from .team_model import TeamPublicWithHeroes, TeamPublic


for m in [TeamPublicWithHeroes, HeroPublicWithTeam]:
    m.model_rebuild()