from pydantic import BaseModel


class TestItem(BaseModel):
    id: int
    name: str
