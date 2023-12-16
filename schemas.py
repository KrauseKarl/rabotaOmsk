from fastapi import Form
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


class ResponsibilityBase(BaseModel):
    body: str


    @classmethod
    def as_form(cls, body: str = Form(...), ):
        return cls(body=body)


class ResponsibilityModel(ResponsibilityBase):
    id: int

    class Config:
        orm_mode = True


class AdvantagesBase(BaseModel):
    body: str
    vacancy_id: int


class AdvantagesModel(AdvantagesBase):
    id: int

    class Config:
        orm_mode = True


class RequirementsBase(BaseModel):
    body: str
    vacancy_id: int


class RequirementsModel(RequirementsBase):
    id: int

    class Config:
        orm_mode = True


class VacancyBase(BaseModel):
    title: str
    name: str
    salary: str
    description: str
    speciality: str
    categories: str
    employer: str
    employer_site: str
    employer_vk: str
    employer_instagram: str
    # created_at: datetime
    is_active: bool
    types: str
    experience: str
    schedule: str
    responsibility: list[ResponsibilityModel] = None

    # advantages: list[AdvantagesModel] = None
    # requirements: list[RequirementsModel] = None
    # tags: list[TagModel] = []

    @classmethod
    def as_form(cls,
                title: str = Form(...),
                name: str = Form(...),
                salary: str = Form(...),
                description: str = Form(...),
                speciality: str = Form(...),
                categories: str = Form(...),
                is_active: bool = Form(...),
                types: str = Form(...),
                experience: str = Form(...),
                schedule: str = Form(...),
                employer: str = Form(...),
                employer_site: str = Form(...),
                employer_vk: str = Form(...),
                employer_instagram: str = Form(...),
                responsibility: list[ResponsibilityModel] = Form(...),
                ):
        return cls(
            title=title,
            name=name,
            salary=salary,
            description=description,
            speciality=speciality,
            categories=categories,
            is_active=is_active,
            types=types,
            experience=experience,
            schedule=schedule,
            employer=employer,
            employer_site=employer_site,
            employer_vk=employer_vk,
            employer_instagram=employer_instagram,
            responsibility=responsibility
        )


class VacancyModel(VacancyBase):
    id: int

    class Config:
        orm_mode = True
