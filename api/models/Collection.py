from pydantic import BaseModel, ConfigDict, Field


class CollectionBase(BaseModel):
    title: str = Field(..., max_length=60, description="Name of the collection")
    description: str = Field(
        ..., max_length=200, description="Description of the collection"
    )


class CollectionCreate(CollectionBase):
    pass


class Collection(CollectionBase):
    id: int
    user_id: int


class CollectionRead(CollectionBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)
