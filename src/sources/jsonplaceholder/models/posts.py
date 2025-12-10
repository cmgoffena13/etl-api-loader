from pydantic import BaseModel, Field


class JSONPlaceholderPost(BaseModel):
    id: int = Field(alias="root[*].id")
    title: str = Field(alias="root[*].title")
    body: str = Field(alias="root[*].body")
    userId: int = Field(alias="root[*].userId")
