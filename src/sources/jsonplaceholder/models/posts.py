from sqlmodel import Field, SQLModel


class JSONPlaceholderPosts(SQLModel, table=True):
    id: int = Field(primary_key=True, alias="root[*].id")
    title: str = Field(alias="root[*].title")
    body: str = Field(alias="root[*].body")
    userId: int = Field(alias="root[*].userId")
