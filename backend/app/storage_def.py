from ampf.base import CollectionDef
from core.users.user_model import UserInDB

# fmt: off
STORAGE_DEF = [
    CollectionDef("users", UserInDB, "username", subcollections=[
    ])
]
# fmt: on
