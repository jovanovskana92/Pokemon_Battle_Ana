from pydantic import BaseModel


class Pokemon(BaseModel):
    name: str
    id: int
    stats: dict
