import itertools
from typing import Dict
from urllib.parse import parse_qs
from fastapi import Request, Query

from database import SessionLocal, Base, engine
from db.vacancy_db import vacancies_list
from db.experience_db import experience_dict
from db.types_db import types_dict
from db.category_db import categories_dict
from db.schedule_db import schedule_dict


def create_tables():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_5_categories() -> Dict:
    try:
        category = dict(itertools.islice(categories_dict.items(), 5))
    except (KeyError, IsADirectoryError):
        category = {}
    return category


def get_5_vacancies():
    try:
        return dict(itertools.islice(vacancies_list.items(), 5))
    except (KeyError, IsADirectoryError):
        return {}


def get_types_list():
    try:
        return dict(itertools.islice(types_dict.items(), 5))
    except (KeyError, IsADirectoryError):
        return {}


def get_tags_list():
    try:
        return [t for vac in vacancies_list.values() for t in vac['hashtags']][:5]
    except (KeyError, IsADirectoryError):
        return {}


def get_categories():
    try:
        categories = categories_dict
    except Exception:
        categories = {}
    return categories


def get_schedule():
    try:
        return schedule_dict
    except Exception:
        return {}


def get_experience():
    try:
        return experience_dict
    except Exception:
        return {}


def get_vacancy_list():
    try:
        return [vac_val for vac_val in vacancies_list.values()]
    except Exception:
        return {}


def get_vacancies():
    try:
        return vacancies_list
    except Exception:
        return {}


def get_types():
    try:
        return types_dict
    except Exception:
        return {}


def get_pagination_params(
        offset: int = Query(0, ge=0),
        limit: int = Query(10, gt=0)
):
    return {"offset": offset, "limit": limit}


def get_param_dict(request: Request):
    params = parse_qs(str(request.query_params))
    print('params ------', params)
    return params if params else {}
