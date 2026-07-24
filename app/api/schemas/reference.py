from pydantic import BaseModel


class ReferenceItemResponse(BaseModel):
    name: str


class ReferenceListResponse(BaseModel):
    items: list[ReferenceItemResponse]
