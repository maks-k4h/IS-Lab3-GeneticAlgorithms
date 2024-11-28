from pandas import pd
from pathlib import Path

from ..entities.group import Group
from ..entities.room import Room
from ..entities.teacher import Teacher
from ..entities.subject import Subject


def import_groups(p_groups: Path) -> list[Group]:
    # .csv spec:
    #   name — group name
    #   size — number of students
    #   subject_requirements — coma-separated subjects and required lessons per week, e.g.
    #   'math:4, science:2, linguistics:2, pe:1'
    df_groups = pd.read(p_groups)
    groups = []
    for i, row in df_groups.iterrows():
        name = row.name
        size = int(row.size)
        subject_requirements = []
        s_subject_requirements = row.subject_requirements
        for requirement in s_subject_requirements.split(','):
            subject, n_required = requirement.strip().split(':')
            n_required = int(n_required)
            subject_requirements.append((n_required, Subject(subject)))
        groups.append(Group(name, size, subject_requirements))
    return groups


def import_rooms(p_rooms: Path) -> list[Room]:
    # .csv spec:
    #   identifier — integer
    #   capacity — integer

    df_rooms = pd.read_csv(p_rooms)
    rooms = []
    for i, row in df_rooms.iterrows():
        identifier = int(row.identifier)
        capacity = int(row.capacity)
        rooms.append(Room(identifier=identifier, capacity=capacity))
    return rooms


def import_teachers(p_teachers: Path) -> list[Teacher]:
    # .csv spec:
    #   fullname — string
    #   subjects — coma-separated subjects, e.g.
    #   'math, programming, data science'
    df_teachers = pd.read_csv(p_teachers)
    teachers = []
    for i, row in df_teachers.iterrows():
        fullname = row.fullname
        teachable_subjects = []
        for s_subject in row.subjects.split(','):
            teachable_subjects.append(Subject(s_subject.strip()))
        teachers.append(Teacher(fullname, teachable_subjects))
    return teachers
