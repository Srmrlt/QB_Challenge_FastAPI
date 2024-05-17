import datetime
from pydantic import BaseModel, conint


class Payload(BaseModel):
    instrument: str
    exchange: str
    iid: int
    storage_type: str


class IsinExistsFilterSchema(BaseModel):
    date: datetime.date
    instrument: str | None = None
    exchange: str | None = None


class IsinExistsIntervalFilterSchema(BaseModel):
    date_from: datetime.date
    date_to: datetime.date
    instrument: str
    exchange: str


class IidToIsinFilterSchema(BaseModel):
    date: datetime.date
    iid: int


class StreamSchema(BaseModel):
    date: datetime.date
    filename: str
    chunk: conint(gt=4*1024, le=512*1024) = 32*1024
