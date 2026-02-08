from pydantic import BaseModel


class AreaRead(BaseModel):
    area_id: int
    area_name: str

    class Config:
        from_attributes = True
