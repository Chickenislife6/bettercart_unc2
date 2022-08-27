from dataclasses import dataclass

@dataclass
class Creds:
    statenum = 1
    user: str
    password: str
    # uid: int
    ICSID = ""
