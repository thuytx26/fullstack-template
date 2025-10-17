from .team_model import TeamPublic, TeamPublicWithUsers  # noqa: F401
from .user_model import UserPublic, UserPublicWithTeam  # noqa: F401

for m in [TeamPublicWithUsers, UserPublicWithTeam]:
    m.model_rebuild()
