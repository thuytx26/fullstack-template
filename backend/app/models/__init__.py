from .user_model import UserPublicWithTeam, UserPublic
from .team_model import TeamPublicWithUsers, TeamPublic


for m in [TeamPublicWithUsers, UserPublicWithTeam]:
    m.model_rebuild()