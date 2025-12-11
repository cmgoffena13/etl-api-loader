from sqlmodel import Field, SQLModel


class TestItem(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
