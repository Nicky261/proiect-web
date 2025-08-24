from fastapi import Depends
from .auth import require_roles

# Alias pentru a fi folosit in rute
is_admin = require_roles(["admin"])
