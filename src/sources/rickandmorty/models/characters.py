from sqlmodel import Field, SQLModel


class RickAndMortyCharacters(SQLModel, table=True):
    id: int = Field(primary_key=True, alias="root.id")
    name: str = Field(alias="root.name")
    status: str = Field(alias="root.status")
    species: str = Field(alias="root.species")
