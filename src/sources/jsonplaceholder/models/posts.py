from pydantic import BaseModel


class JSONPlaceholderPost(BaseModel):
    id: int
    title: str
    body: str
    userId: int
