import ast
import itertools
import json
import locale
from time import sleep
from typing import Dict, List, Optional, Annotated, Any

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
    allowed_hosts=["*"]
)

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
        query: Optional[str] = None,
        category: Dict = Depends(get_categories),
        vacancies: Dict = Depends(get_vacancies),
        types: List = Depends(get_types_list),
        schedule: Dict = Depends(get_schedule),
        experience: Dict = Depends(get_experience),
):

    context = {
        "request": request,
        "vacancies": vacancies,
        "categories": category,
        "types": types,
        'schedule_dict': schedule,
        'experience_dict': experience,
    }
    print('@@@@@@@@@@@@@@@@@@/catalog?query={query} = ', query)
    # if query:
    #     q = query.lower().strip()
    #     vacancies = dict((k, v) for k, v in vacancies.items() if q in v['vacancy'].lower())
    #     context.update({"vacancies": vacancies, 'message': f'вакансии по запросу "{q}"'})
    return templates.TemplateResponse(
        "catalog.html",
        context=context
    )


# @app.get("/catalogs?query={query}", response_class=HTMLResponse)
# async def catalogs(
#         request: Request,
#         query: Optional[str] = None,
#         category: Dict = Depends(get_categories),
#         vacancies: Dict = Depends(get_vacancies),
#         types: Dict = Depends(get_types),
#         schedule: Dict = Depends(get_schedule)
# ):
#
#     context = {
#         "request": request,
#         "vacancies": vacancies,
#         "categories": category,
#         "types": types,
#         'schedule_dict': schedule,
#     }
#     return templates.TemplateResponse("catalog.html", context=context)


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
async def vacancy(query: str) -> Dict[str, List]:
    q = query.lower().strip()
    res = [
        (v['vacancy'], v['slug'], v['salary'])
        for k, v in vacancies_list.items()
        if q in v['vacancy'].lower() or q in [tag for tag in v['hashtags']]
    ]
    return {'vacancy': res}


@app.get("/filter/", response_class=JSONResponse)
async def filter_catalog(
        params: Optional[str] = None,
        category: Dict = Depends(get_categories),
        vacancies: Dict = Depends(get_vacancies),
        schedule: Dict = Depends(get_schedule),
        types: Dict = Depends(get_types),
        experience: Dict = Depends(get_experience),
        response: Response = None,
        request: Request = None,
        title: str = 'Каталог'
):
    vacancies_list_base = [vac_val for vac_val in vacancies.values()]

    if params[0] != '':
        params_dict = ast.literal_eval(params)
        params = [*params_dict.values()]
        if params_dict.get("search"):
            search_string = params_dict.get("search")
            vacancies_list_base = [
                vacancies
                for vacancies in vacancies_list_base
                for key, value in vacancies.items()
                if key == "vacancy" and search_string[0] in value
            ]
        if params_dict.get("types"):
            types_string = params_dict.get("types")
            vacancies_list_base = [
                vacancies
                for vacancies in vacancies_list_base
                for key, value in vacancies.items()
                if key == "types" and value in types_string
            ]
        if params_dict.get("schedule"):
            schedule_string = params_dict.get("schedule")
            vacancies_list_base = [
                vacancies
                for vacancies in vacancies_list_base
                for key, value in vacancies.items()
                if key == "schedule" and value in schedule_string
            ]
        if params_dict.get("experience"):
            experience_string = params_dict.get("experience")
            vacancies_list_base = [
                vacancies
                for vacancies in vacancies_list_base
                for key, value in vacancies.items()
                if key == "experience" and value in experience_string
            ]

    if len(params) > 1:

        params_list = list(itertools.chain.from_iterable(params))
    else:
        params_list = params
    # if len(params_list) >= 2:
    #     all_vacancy = [
    #         vac_val
    #         for vac_val in vacancy_list
    #         for name, value in vac_val.items()
    #         if value in params_list
    #     ]
    #     count_vacancy = len(vacancies)
    #     title = f'Найдено - {count_vacancy} вакансий'
    #     # sleep(2)
    # elif 0 < len(params_list) < 2:
    #     params_list = params_list[0]
    #     all_vacancy = [
    #         vac_val
    #         for vac_val in vacancy_list
    #         for name, value in vac_val.items()
    #         if params_list in value
    #     ]
    #     count_vacancy = len(vacancies)
    #     title = f'Найдено - {count_vacancy} вакансий'
    # else:
    #     all_vacancy = [vac_val for vac_slug, vac_val in vacancies.items()]
    # search_param = request.cookies.get('search_param')
    # print('search_param = ', search_param.decode())
    # param_dict = json.loads(params)
    # params_list = [v for k, v in param_dict.items()]
    # print(params_list)
    # if search_param:
    #     prev_param = json.load(search_param)
    #     print("\nprev_param = ", type(prev_param))

    # sleep(1.2)
    # response.set_cookie(key="search_param", value=encode_param, httponly=True)
    # if params_dict.get("search"):
    #     vacancy_list = [
    #         vac_val
    #         for k, vac_val in vacancies.items()
    #         for name, value in vac_val.items()
    #         if params_dict.get("search")[0] in value]
    # else:
    #     vacancy_list = vacancies
    return {
        'result': vacancies_list_base,
        "categories": category,
        'schedule_dict': schedule,
        'experience_dict': experience,
        'types': types,
        'title': title,
        'params': params_list,
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
