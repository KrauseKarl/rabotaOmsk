import itertools
import locale
from typing import Dict, List, Optional, Annotated

import uvicorn
from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.templating import Jinja2Templates

import models
from database import Base, engine, SessionLocal
import schemas as sch

locale.setlocale(category=locale.LC_ALL, locale="ru_RU.UTF-8")
vacancies_list = {
    "parikmaher": {
        "slug": "parikmaher",
        "title": "Парикмахер",
        "vacancy": "Парикмахер",
        "salary": " от 40 до 70 тыс.",
        "experience": "full_time",
        "type": "no_matter",
        "schedule": "week",
        "description":
            """
            Парикмахер Парикмахер-универсал
            Ищу работу в Туле парикмахером? хочу новую работу?
            ты опытный мастер? тебе нужны клиенты? хочешь работать в
            красивом салоне красоты? надоела аренда рабочего
            места мастера парикмахера? хочешь стабильный доход и
            не заниматься поиском клиентской базы? Приходи,
            остальные преимущества ты увидишь на месте?
            """,
        "hashtags": [
            "работа парикмахером",
            "работа парикмахером в туле",
            "работа в салоне тула",
            "салоны красоты тула подработка",
            "парикмахер",
            "парикмахер-универсал ",
        ],
    },
    "master-manikyura": {
        "slug": "master-manikyura",
        "vacancy": "Вакансия мастер маникюра",
        "title": "Мастер маникюра",
        "salary": " от 40 до 70 тыс.",
        "experience": "full_time",
        "type": "no_matter",
        "schedule": "shifts",
        "shift": None,
        "employer": "NikeNagel",
        "contacts": ["+7(900) 800-70-69", "emploer@mai.com", ],
        "advantages": ['advantage 1', 'advantage 2', 'advantage 3'],
        "responsibility": ['responsibility 1', 'responsibility 2', 'responsibility 3'],
        "requirements": ['requirements 1', 'requirements 2', 'requirements 3'],
        "description":
            """
            Мастер маникюра работа для nail master в сети салонов Nika Nagel
            всегда найдется так, как у нас наработанная
            клиентская база за 22 года работы в Туле,
            вакансия мастера маникюра в Туле всегда открыты потому,
            что мы растем и развиваемся вместе с вами.
            """,
        "hashtags": [
            'вакансия мастер маникюра тула',
            'бьюти мастер тула',
            'мастер маникюра тула',
            'nail master',
            'неил мастер обучение',
            'бесплатное обучение маникюру в туле',
            'ученик мастера маникюра',
        ],
    },
    "administrator": {
        "slug": "administrator",
        "vacancy": "Администратор",
        "title": "Администратор",
        "salary": " от 30 до 60 тыс.",
        "experience": "full_time",
        "type": "no_matter",
        "schedule": "week",
        "shift": " сменный график",
        "description":
            """
        Работа администратором салона красоты в Туле
        или администратор учебного центра Nika Nagel даст Вам
        возможность управлять салоном красоты,
        иметь стабильный доход, расширить круг знакомств,
        находиться в невероятной ауре красоты, проявить
        творческие способности, быть нужной
        частичкой компании.Возьмем  кандидата без опыта работы и всему научим.
        """,
        "hashtags": [
            "работа администратором тула",
            "работа в туле",
            "подработка в туле",
            "вакансии тула",
            "вакансии в туле",
            "вакансии администраторо тула",
            "трудоустройство тула",
            "поиск работы тула",
        ],
    },
    "master-po-narashchivaniyu-resnic": {
        "slug": "master-po-narashchivaniyu-resnic",
        "title": "Мастер по наращиванию ресниц",
        "vacancy": "Мастер по наращиванию ресниц",
        "salary": " от 30 до 60 тыс.",
        "experience": "for_teenager",
        "type": "one_to_three",
        "schedule": "flexible",
        "shift": " сменный график",
        "description":
            """
            Мастер по наращиванию ресниц вакансия начинающего
            мастера наращивания ресниц или другими словами
            работа лешмейкером в Туле возможна даже без опыта
            работы в сети салонов Nika Nagel. Мы знаем,
            как организовать работу Lashmaker, так что бы
            Вы росли в своем доходе вместе с нами,
            мы проводим бесплатное обучение лешмейкеров в Туле
            """,
        "hashtags": [
            "мастер по наращиванию ресниц",
            "наращивание ресниц Тула",
            "бесплатное обучение наращиванию ресниц",
            "обучение нащивание ресниц в Туле",
            "вакансия мастера по наращиванию ресниц в Туле",
            "lashmaker Тула",
            "лашмейкер Тула",
            "курсы наращивания ресниц Тула",
        ],
    },
    "master-epilyacii-LPG-massazh-sovmeshchennyj": {
        "slug": "master-epilyacii-LPG-massazh-sovmeshchennyj",
        "vacancy": "Мастер эпиляции-LPG массаж совмещенный",
        "title": "Мастер эпиляции-LPG массаж совмещенный",
        "salary": " от 30 до 60 тыс.",
        "experience": "3",
        "type": "1",
        "schedule": "1",
        "shift": " сменный график",
        "description":
            """
            Мастер эпиляции-lPG массаж бесплатное обучение
            для работы мастером эпиляции в Туле без опыта работы,
            подходит тебе если, у тебя сильные руки и ты готов к
            тактильному контакту с нашими замечательными клиентами,
            наработанная клиентская база тебя уже ждет,
            а так же стабильный доход, дружный коллектив,
            красивое место.
            """,
        "hashtags": [
            "мастер эпиляции",
            "LPG массаж тула",
            "LPG массажист тула",
            "LPG в туле работа",
            "LPG тула подработка",
            "LPG массаж работа тула",
            "LPG в туле",
            "эпиляция тула работа",
            "работа мастером эпиляции тула",
            "работа восковая эпиляция тула",
            "эпиляция воском подработка тула",
        ],
    },
    "nyanya": {
        "slug": "nyanya",
        "title": "Няня",
        "vacancy": "Няня",
        "salary": " от 20 до 50 тыс.",
        "experience": "",
        "type": "",
        "schedule": "",
        "shift": "гибкий график",
        "description":
            """
       Няня вакансия для человека исполняющего самый
       разнообразный спектр услуг
       (подбирается индивидуально под каждую семью и няню)
       таких как, присмотр и уход, воспитание, кормление,
       обучение, посещение дополнительного образования,
       кружков и секций, подготовка домашнего задания,
       приготовления пищи, стирка и глажка одежды ребенку,
       сопровождение в учебное заведение,
       забор ребенка из садика или школы, прогулка,
       чтение книг, походы в развлекательные места,
       совместные путешествия и
       командировки с предоставлением жилья и без.
        """,
        "hashtags": [
            "няня",
            "няня тула",
            "работа няней в туле",
            "студент педколледжа тула",
            "воспитатель тула",
            "работа воспитателем тула",
            "работа воспитателем",
        ],
    },
    "promouter": {
        "slug": "promouter",
        "vacancy": "Промоутер",
        "title": "Промоутер",
        "salary": " 200 - 400 час",
        "experience": "for_teenager",
        "type": "one_to_three",
        "schedule": "flexible",
        "shift": "гибкий график",
        "description":
            """
            Раздача листовок, консультация посетителей салона красоты,
            распространие листовок по почтовым ящикам,
            расклейка объвлений.
            Работа подходит для школьников,
            студентам, пенсионеров на не полный день.
            """,
        "hashtags": [
            "работа промоутер тула",
            "частичная занятость",
            "побработка тула",
            "работа для студентов",
            "работа без опыта тула",
            "раздача листовок тула",
            "листовки тула",
            "промо тула",
            "вакансия для студентов",
            "распространение листовок тула",
            "консультанты тула",
            "работа ведущего тула",
            "btl тула",
        ],
    },
    "torgovye-predstavitel": {
        "slug": "torgovye-predstavitel",
        "vacancy": "Торговые представитель",
        "title": "Торговые представитель",
        "salary": " от 60 до 120 тыс.",
        # "experience": "без опыта",
        "experience": "partly_time",
        "type": "one_to_three",
        "schedule": "week",
        "description":
            """
            Продвижение бренда  Nika Nagel,
            увеличение продаж, выполнение плана продаж.
            Работа подходит для тех, кто ищет работу
            менеджером по продажам,
            специалист по развитию территории.
            """,
        "hashtags": [
            "торговый представитель тула",
            "вакансия торговый представитель тула",
            "работа торговым представителем",
            "менеджер по продажам тула",
            "вакансия менеджера тула",
            "менеджер работа тула",
            "вакансия торговый агент тула",
            "продажник тула",
        ],
    },
    "uborshchica": {
        "slug": "uborshchica",
        "title": "Уборщица",
        "vacancy": "Уборщица",
        "salary": "договорная",
        "experience": "partly_time",
        "type": "one_to_three",
        "schedule": "week",
        "shift": "график 5/2",
        "description":
            """
            Ищете работу: Уборка  в офисных помещениях,
            вынос мусора, клиненговые услуги, работа техничкой,
            уборка дома, помощница по дому, работа домохозяйкой,
            помощница по хозяйству, подработку для студентов
            в Туле или работа для пенсионеров в Туле.
            """,
        "hashtags": [
            "уборщица тула",
            "горничная тула",
            "домработница тула",
            "работауборщицей тула",
            "уборка тула",
            "работа без опыта тула",
            "подработка в туле",
            "подработка уборщицей",
            "клининг тула",
            "работа клинером тула",
        ],
    },
    "uchenik-mastera-manikyura": {
        "slug": "uchenik-mastera-manikyura",
        "vacancy": "Ученик мастера маникюра",
        "title": "Ученик мастера маникюра",
        "salary": " от 30 до 60 тыс.",
        "experience": "partly_time",
        "type": "one_to_three",
        "schedule": "week",
        "shift": " сменный график",
        "description":
            """
        Работа администратором салона красоты в Туле
        или администратор учебного центра Nika Nagel даст Вам
        возможность управлять салоном красоты,
        иметь стабильный доход, расширить круг знакомств,
        находиться в невероятной ауре красоты, проявить
        творческие способности, быть нужной
        частичкой компании.Возьмем  кандидата без опыта работы и всему научим.
        """,
        "hashtags": [
            "обучение",
            "бесплатное",
            "мастре маникюра",
        ],
    },
}
types_dict = {
    "full_time": "Полная занятость",
    "partly_time": "Частичная занятость",
    "for_teenager": "Стажировка",
    "for_student": "Проектная работа",
    "for_mam": "Волонтерство",
}

categories_dict = {
    "1": "менеджер по продажам",
    "2": "строитель",
    "3": "курьер",
    "4": "промоутер",
    "5": "администратор",
    "6": "дизайнер, художник"
}
experience_dict = {
    "no_matter": "Не имеет значения",
    "without": "Нет опыта",
    "one_to_three": "От 1 года до 3 лет",
    "three_to_six": "От 3 до 6 лет",
    "above_six": "Более 6 лет",
}
schedule_dict = {
    "shifts": "Сменный график  (2/2)",
    "week": "Полный день (5/2)",
    "flexible": "Гибкий график",
    "remote": "Удаленная работа",
    "rotations": "Вахтовый метод"
}


def create_tables():
    print("Creating Tables..")
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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


def get_categories_list():
    try:
        return dict(itertools.islice(categories_dict.items(), 5))
    except (KeyError, IsADirectoryError):
        return {}


def get_vacancies_list():
    try:
        return dict(itertools.islice(vacancies_list.items(), 5))
    except (KeyError, IsADirectoryError):
        return {}


def get_typies_list():
    try:
        return dict(itertools.islice(types_dict.items(), 5))
    except (KeyError, IsADirectoryError):
        return {}


def get_tags_list():
    try:
        return [t for vac in vacancies_list.values() for t in vac['hashtags']]
    except (KeyError, IsADirectoryError):
        return {}


def get_categories():
    try:
        return categories_dict
    except Exception:
        return {}


def get_schedule():
    try:
        return schedule_dict
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


@app.get("/", response_class=HTMLResponse)
async def index(
        request: Request,
        category: Dict = Depends(get_categories),
        vacancies: Dict = Depends(get_vacancies),
        tags: Dict = Depends(get_tags_list),
        types: List = Depends(get_types)
):
    context = {
        "request": request,
        "vacancies": vacancies,
        "categories": category,
        "types": types,
        'tags': sorted(tags),
    }

    return templates.TemplateResponse(
        "index.html",
        context=context
    )


@app.get("/catalog", response_class=HTMLResponse)
async def catalog(
        request: Request,
        query: Optional[str] = None,
        category: Dict = Depends(get_categories_list),
        vacancies: Dict = Depends(get_vacancies_list),
        tags: Dict = Depends(get_tags_list),
        types: List = Depends(get_typies_list),
        schedule: Dict = Depends(get_schedule)
):
    context = {
        "request": request,
        "vacancies": vacancies,
        "categories": category,
        "types": types,
        'tags': sorted(tags[:5]),
        'schedule_dict': schedule,
    }
    if query:
        q = query.lower().strip()
        vacancies = dict((k, v) for k, v in vacancies.items() if q in v['vacancy'].lower())
        context.update({"vacancies": vacancies, 'message': f'вакансии по запросу "{q}"'})
    return templates.TemplateResponse(
        "catalog.html",
        context=context
    )


@app.get("/catalog/?category={category}", response_class=HTMLResponse)
async def catalog(
        request: Request,
        category: Dict = Depends(get_categories_list),
        vacancies: Dict = Depends(get_vacancies_list),
        tags: Dict = Depends(get_tags_list),
        types: Dict = Depends(get_types),
        schedule: Dict = Depends(get_schedule)
):
    context = {
        "request": request,
        "vacancies": vacancies,
        "categories": category,
        "types": types,
        'tags': sorted(tags[:5]),
        'schedule_dict': schedule,
    }

    return templates.TemplateResponse(
        "catalog.html",
        context=context
    )


@app.get("/vacancy/{slug}/", response_class=HTMLResponse)
async def vacancy(
        request: Request,
        slug: str,
        category: Dict = Depends(get_categories_list),
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


# , vac: VacancyModel, db: db_dependency
@app.get("/add_vacancies/", response_model=sch.VacancyModel)
async def create_transaction(
        request: Request,
        category: Dict = Depends(get_categories_list),
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
    print('***** res', res)
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


@app.get("/filter/", response_class=JSONResponse)
async def filter_catalog(
        param: Optional[str] = None,
        category: Dict = Depends(get_categories_list),
        vacancies: Dict = Depends(get_vacancies_list),
        schedule: Dict = Depends(get_schedule),
        types: Dict = Depends(get_types),

):
    print(param)
    if param:
        vacancies = [val for key, val in vacancies.items() for k, i in val.items() if param == i]
    return {
        'result': vacancies,
        "categories": category,
        'schedule_dict': schedule,
        'types': types
    }


if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
