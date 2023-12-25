import ast
import itertools
import json
import locale
import urllib
from time import sleep
from typing import Dict, List, Optional, Annotated, Any
from urllib.parse import unquote, urlencode, urlparse, urlsplit, parse_qs

import uvicorn
from fastapi import FastAPI, Request, Depends, Form, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.templating import Jinja2Templates

import models
import schemas as sch
from dependencies import *

locale.setlocale(category=locale.LC_ALL, locale="ru_RU.UTF-8")
db_dependency = Annotated[Session, Depends(get_db)]
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
# app.include_router(catalog.router)
templates = Jinja2Templates(directory="templates")

app.mount("/assets", StaticFiles(directory="assets"), name="assets")
app.add_middleware(
    SessionMiddleware,
    secret_key="some-random-string",
    max_age=31536000
)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "*"
    ]
)
# app.add_middleware(
#     TrustedHostMiddleware,
#     allowed_hosts=[
#         "xn--80aac1bjkblpg.xn--p1ai",
#         "www.xn--80aac1bjkblpg.xn--p1ai",
#         "localhost",
#         "127.0.0.1"
#     ]
# )
origins = [
    "http://localhost:8000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


# @app.middleware('http')
# async def some_middleware(request: Request, call_next):
#     # update request query parameters
#     q_params = dict(request.query_params)
#     q_params['search'] = 'Водитель'
#     request.scope['query_string'] = urlencode(q_params).encode('utf-8')
#
#     return await call_next(request)


@app.get("/", response_class=HTMLResponse)
async def index(
        request: Request,
        categories: Dict = Depends(get_5_categories),
        vacancies: Dict = Depends(get_5_vacancies),
        tags: Dict = Depends(get_tags_list),
        types: List = Depends(get_types_list)
):
    context = {
        "request": request,
        "vacancies": vacancies,
        "categories": categories,
        "types": types,
        'tags': sorted(tags),
    }

    return templates.TemplateResponse(
        "index.html",
        context=context
    )


@app.get("/categories", response_class=HTMLResponse)
async def categories(
        request: Request,
        categories: Dict = Depends(get_categories),
):
    context = {
        "request": request,
        "categories": categories,
    }
    return templates.TemplateResponse(
        "categories.html",
        context=context
    )


@app.get("/catalog", response_class=HTMLResponse)
async def catalog(
        request: Request,
        params: Dict = Depends(get_param_dict),
        category: Dict = Depends(get_categories),
        vacancies: Dict = Depends(get_vacancy_list),
        types: List = Depends(get_types),
        schedule: Dict = Depends(get_schedule),
        experience: Dict = Depends(get_experience),
        pagination: dict = Depends(get_pagination_params),
        title=""
):

    if params.get("search"):
        search_string = params.get("search")[0].strip()
        print('search_string =', search_string)
        vacancies = [
            vac
            for vac in vacancies
            if vac["vacancy"].lower() == search_string.lower()
        ]
    if params.get("types"):
        type_list = params.get("types")
        vacancies = [
            vac
            for vac in vacancies
            if vac["types"] in type_list
        ]
    if params.get("schedule"):
        schedule_list = params.get("schedule")
        vacancies = [
            vac
            for vac in vacancies
            if vac["schedule"] in schedule_list
        ]
    if params.get("experience"):
        experience_list = params.get("experience")
        vacancies = [
            vac
            for vac in vacancies
            if vac["experience"] in experience_list
        ]

    limit = pagination["limit"]
    offset = pagination["offset"]
    start = (limit - 1) * offset
    end = start + limit
    try:
        number_vacancy = len(vacancies)
        if number_vacancy > 0 and params.get("search")[0] != '':
            title = f"Найдено вакансий - {number_vacancy}"
        if number_vacancy < 1:
            title = f"Найдено 0 вакансий"
    except Exception:
        title = ""
    context = {
        "request": request,
        "vacancies": vacancies[start:end],
        "categories": category,
        "types": types,
        'schedule_dict': schedule,
        'experience_dict': experience,
        "title": title,
    }
    return templates.TemplateResponse(
        "catalog.html",
        context=context
    )


@app.get("/vacancy/{slug}/", response_class=HTMLResponse)
async def vacancy(
        request: Request,
        slug: str,
        category: Dict = Depends(get_categories),
):
    vacancies = vacancies_list[slug]
    context = {
        "request": request,
        "vacancy": vacancies,
        "categories": category,
    }
    return templates.TemplateResponse(
        "vacancy.html",
        context=context
    )


@app.get("/search/", response_class=JSONResponse)
async def vacancy(
        search: str,
        categories: Dict = Depends(get_categories)
) -> Dict[str, List]:
    q = search.lower().strip()
    print("q =", q)
    sorted_vacancy = [
        (v['vacancy'], v['slug'], v['salary'])
        for k, v in vacancies_list.items()
        if q in v['vacancy'].lower() or q in [tag for tag in v['hashtags']]
    ]
    sorted_category = [
                        sub_dict[sub_code]
                        for code, title_dict in categories.items()
                        for name, sub_dict in title_dict.items()
                        for sub_code, sum_name in sub_dict.items()
                        if sub_dict[sub_code].lower() == q
                    ]
    return {
        "vacancy": sorted_vacancy[:5],
        "category": list(set(sorted_category))
    }


@app.get("/filter/", response_class=JSONResponse)
async def filter_catalog(
        params: Optional[str] = None,
        category: Dict = Depends(get_categories),
        vacancies_list_base: Dict = Depends(get_vacancy_list),
        schedule: Dict = Depends(get_schedule),
        types: Dict = Depends(get_types),
        experience: Dict = Depends(get_experience),
        request: Request = None,
        title: str = '',
        pagination: dict = Depends(get_pagination_params)
):
    # url = "http://foo.bar?a=1&b=2&c=true"  # actually get this from your http request header
    # import urlparse
    # split_result = urlparse.urlsplit(url)
    # request_params = dict(urlparse.parse_qsl(split_result.query))
    # base_url = request.query_params.get("search")
    # base_url = unquote(base_url)
    # print("base_url =", base_url)
    # q_params = dict(request.query_params)
    # print("q_params ", q_params)
    # print("q_params ", q_params.get("url"))
    # print('\nurl = ', url, type(url), '\n')
    # de_url = url.decode("utf-8")
    # # print('\nde_url = ', de_url, type(de_url), '\n')
    # # .split("?")[0]
    # params_dict = parse_qs(de_url)
    #
    # print('\nparams     ', params.split("?")[1], type(params), '\n')
    # print('\nparams_dict        ', params_dict, type(params_dict), '\n')
    params_dict_from_ajax = parse_qs(params)

    if params != '':
        if params_dict_from_ajax.get("search"):
            search_string = params_dict_from_ajax.get("search")[0].strip()
            request.scope['query_string'] = urlencode(params_dict_from_ajax).encode('utf-8')
            if isinstance(search_string, list):
                search_string = search_string[0].strip().lower()
            if isinstance(search_string, str):
                search_string = search_string.strip().lower()
            vacancies_list_base = [
                vacancies
                for vacancies in vacancies_list_base
                if search_string in vacancies["vacancy"].lower()
            ]
        if params_dict_from_ajax.get("types"):
            types_string = params_dict_from_ajax.get("types")
            vacancies_list_base = [
                vacancies
                for vacancies in vacancies_list_base
                for key, value in vacancies.items()
                if key == "types" and value in types_string
            ]
        if params_dict_from_ajax.get("schedule"):
            schedule_string = params_dict_from_ajax.get("schedule")
            vacancies_list_base = [
                vacancies
                for vacancies in vacancies_list_base
                for key, value in vacancies.items()
                if key == "schedule" and value in schedule_string
            ]
        if params_dict_from_ajax.get("experience"):
            experience_string = params_dict_from_ajax.get("experience")
            vacancies_list_base = [
                vacancies
                for vacancies in vacancies_list_base
                for key, value in vacancies.items()
                if key == "experience" and value in experience_string
            ]
    try:
        if len(list(params_dict_from_ajax.values())) > 1:
            params_list = list(itertools.chain.from_iterable(params_dict_from_ajax.values()))
        else:
            params_list = list(params_dict_from_ajax.values())[0]
    except Exception:
        params_list = []
    print('fil', len(vacancies_list_base))
    if len(vacancies_list_base) == 0:
        title = f"Найдено 0 вакансий"
    try:
        number_vacancy = len(vacancies_list_base)
        if number_vacancy > 0:
            title = f"Найдено вакансий - {number_vacancy}"
        if number_vacancy < 1:
            title = f"Найдено 0 вакансий"
    except Exception:
        title = ""

    limit = pagination["limit"]
    offset = pagination["offset"]
    start = (limit - 1) * offset
    end = start + limit
    return {
        'result': vacancies_list_base[start:end],
        "categories": category,
        'schedule_dict': schedule,
        'experience_dict': experience,
        'types': types,
        'title': title,
        'params': params_list,
        "url": params
    }


# , vac: VacancyModel, db: db_dependency
@app.get("/add_vacancies/", response_model=sch.VacancyModel)
async def create_transaction(
        request: Request,
        category: Dict = Depends(get_categories),
):
    return templates.TemplateResponse(
        "add_vacancy.html",
        context={
            'request': request,
            "categories": category,
        }
    )


@app.post("/add/", response_class=JSONResponse)
async def create_vacancies(
        db: db_dependency,
        data: sch.VacancyBase = Depends(sch.VacancyBase.as_form),
        res: sch.ResponsibilityBase = Depends(sch.ResponsibilityBase.as_form)

):
    new_vacancy = models.Vacancy(**data.model_dump())
    res_list = [models.Responsibility(body=r, vacancy_id=new_vacancy.id) for r in res]

    db.add(new_vacancy)
    db.add_all(res_list)
    db.commit()
    new_vacancy.responsibility.append(res_list)
    db.refresh(new_vacancy)

    return {"msg": new_vacancy}


@app.get("/vacancies/", response_model=List[sch.VacancyModel,])
async def read_transaction(db: db_dependency, skip: int = 0, limit: int = 100):
    vacancies = db.query(models.Vacancy).offset(skip).limit(limit).all()
    return vacancies


if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
