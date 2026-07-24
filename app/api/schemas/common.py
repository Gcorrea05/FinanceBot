from pydantic import BaseModel


class StatusResponse(BaseModel):
    status: str


class MessageResponse(BaseModel):
    message: str
