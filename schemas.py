from pydantic import BaseModel
from datetime import datetime


class TagBase(BaseModel):
    title: str


class TagModel(TagBase):
    id: int

    class Config:
        orm_mode = True


class CategoryBase(BaseModel):
    title: str


class CategoryModel(CategoryBase):
    id: int

    class Config:
        orm_mode = True


class VacancyBase(BaseModel):
    title: str
    name: str
    salary: str
    description: str = None
    employer: str = None
    contacts: str = None
    created_at: datetime
    is_active: bool
    types: str = None
    experience: str = None
    schedule: str = None
    tags: list[TagModel] = []
    categories: list[CategoryModel] = []


class VacancyModel(VacancyBase):
    id: int

    class Config:
        orm_mode = True
