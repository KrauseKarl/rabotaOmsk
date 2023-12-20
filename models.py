from datetime import datetime

from sqlalchemy.orm import relationship
from sqlalchemy_utils import ChoiceType

from database import Base
from sqlalchemy import Column, Integer, Boolean, String, Text, DateTime, Table, ForeignKey, orm

tagging = Table(
    'tagging', Base.metadata,
    Column(
        'tag_id',
        Integer,
        ForeignKey('tag.id', ondelete='CASCADE'),
        primary_key=True
    ),
    Column(
        'vacancy_id',
        Integer,
        ForeignKey('vacancy.id', ondelete='CASCADE'),
        primary_key=True
    )
)
classify = Table(
    'classify', Base.metadata,
    Column(
        'category_id',
        Integer,
        ForeignKey('category.id', ondelete='CASCADE'),
        primary_key=True
    ),
    Column(
        'vacancy_id',
        Integer,
        ForeignKey('vacancy.id', ondelete='CASCADE'),
        primary_key=True
    )
)


class Vacancy(Base):
    __tablename__ = "vacancy"
    TYPES = [
        ('full_time', 'Полная занятость'),
        ('partly_time', 'Частичная занятость'),
        ('for_teenager', 'Работа для школьников'),
        ('for_student', 'Работа для студентов'),
        ('for_mam', 'Работа в декрете')
    ]
    EXPERIENCE = [
        ('no_matter', 'Не имеет значения'),
        ('without', 'Нет опыта'),
        ('one_to_three', 'От 1 года до 3 лет'),
        ('three_to_six', 'От 3 лет до 6 лет'),
        ('above_six', 'Более 6 лет')
    ]
    SCHEDULE = [
        (' ', 'Сменный график (2/2)'),
        (' ', 'Полный день (5/2)'),
        (' ', ' Гибкий график'),
        (' ', 'Удаленная работа'),
        (' ', 'Вахтовый метод')
    ]

    id = Column(Integer, primary_key=True, index=True)
    # GENERAL
    title = Column(String(length=64), comment='полное название вакансии', nullable=False)
    name = Column(String(length=64), comment='название вакансии', nullable=False)
    salary = Column(String(length=64), comment='зарплата', nullable=False)
    speciality = Column(String(length=64), comment='специальность', nullable=False)
    categories = Column(String(length=64), comment='категория', nullable=False)
    description = Column(Text, comment='описание', nullable=True)
    # EMPLOYER
    employer = Column(String(length=64), comment='работодатель', nullable=True)
    employer_site = Column(String(length=64), comment='сайт работодателя', nullable=True)
    employer_vk = Column(String(length=64), comment='VK работодателя', nullable=True)
    employer_instagram = Column(String(length=64), comment='Instagram работодателя', nullable=True)
    # SELECTED
    types = Column(ChoiceType(TYPES), comment='тип занятости', nullable=True)
    experience = Column(ChoiceType(EXPERIENCE), comment='опыт работы', nullable=True)
    schedule = Column(ChoiceType(SCHEDULE), comment='режим работы', nullable=True)
    # ManyToMany
    # tags = relationship('Tag', secondary=tagging, backref='vacancies')
    # categories = relationship('Category', secondary=classify, backref='vacancies')
    # AUTO CREATED
    created_at = Column(DateTime, default=datetime.now, comment='дата публикации')
    # BOOLEAN
    is_active = Column(Boolean, default=True, comment='активная')
    responsibility = orm.relationship("Responsibility", back_populates="vacancy")


class Tag(Base):
    __tablename__ = 'tag'

    id = Column(Integer, primary_key=True)
    title = Column(String(100), unique=True, nullable=False)

    def __init__(self, title=None):
        self.title = title


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    title = Column(String(100), unique=True, nullable=False,comment='сфера деятельности')
    slug = Column(String(100), unique=True, nullable=False)

    def __init__(self, title=None):
        self.title = title


class Responsibility(Base):
    __tablename__ = 'responsibility'

    id = Column(Integer, primary_key=True)
    body = Column(String(255))
    vacancy_id = Column(Integer, ForeignKey('vacancy.id'))

    vacancy = orm.relationship("Vacancy", back_populates="responsibility")


class Advantages(Base):
    __tablename__ = 'advantages'

    id = Column(Integer, primary_key=True)
    body = Column(String(255))
    vacancy_id = Column(Integer, ForeignKey('vacancy.id'))
    vacancy = orm.relationship(Vacancy)


class Requirements(Base):
    __tablename__ = 'requirements'

    id = Column(Integer, primary_key=True)
    body = Column(String(255))
    vacancy_id = Column(Integer, ForeignKey('vacancy.id'))
    vacancy = orm.relationship("Vacancy", backref='requirements')

# class User(Base):
#     TYPES = [
#         ('admin', 'Admin'),
#         ('regular-user', 'Regular user')
#     ]
#     __tablename__ = 'user'
#     id = sa.Column(sa.Integer, primary_key=True)
#     name = sa.Column(sa.Unicode(255))
#     type = sa.Column(ChoiceType(TYPES))
#     name = Column(String(100), unique=True, nullable=False)

# from sqlalchemy_utils import aggregated

# class Thread(Base):
#     __tablename__ = 'thread'
#     id = sa.Column(sa.Integer, primary_key=True)
#     name = sa.Column(sa.Unicode(255))
#
#     @aggregated('comments', sa.Column(sa.Integer))
#     def comment_count(self):
#         return sa.func.count('1')
#
#     comments = sa.orm.relationship(
#         'Comment',
#         backref='thread'
#     )
#
#
# class Comment(Base):
#     __tablename__ = 'comment'
#     id = sa.Column(sa.Integer, primary_key=True)
#     content = sa.Column(sa.UnicodeText)
#     thread_id = sa.Column(sa.Integer, sa.ForeignKey(Thread.id))
#
#
# thread = Thread(name='SQLAlchemy development')
# thread.comments.append(Comment('Going good!'))
# thread.comments.append(Comment('Great new features!'))
#
# session.add(thread)
# session.commit()
#
# thread.comment_count  # 2


# class User(Base):
#     __tablename__ = 'user'
#
#     id = Column(Integer, primary_key=True)
#     name = Column(String(255))
#
#     def __repr__(self):
#         return 'User(name=%r)' % self.name
#
#
# class Parent(Base):
#     __tablename__ = 'parent'
#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#
#     children = orm.relationship("Child", back_populates="parent")
#
#
# class Child(Base):
#     __tablename__ = 'child'

#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#     parent_id = Column(Integer, ForeignKey('parent.id'))
#     parent = orm.relationship("Parent", back_populates="children")
