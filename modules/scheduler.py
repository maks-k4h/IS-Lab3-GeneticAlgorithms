import copy
import enum
import random
from typing import Optional

from modules import entities


class SelectionStrategy(enum.Enum):
    GREEDY = 0
    RAIN = 1


class Scheduler:
    def __init__(
            self,
            population_size: int,
            n_generations: int,
            selection_strategy: SelectionStrategy,
    ) -> None:
        self._population_size = population_size
        self._n_generations = n_generations
        self._selection_strategy = selection_strategy

        self._mutation_probability = 0.3

    def run(
            self,
            groups: list[entities.group.Group],
            rooms: list[entities.room.Room],
            teachers: list[entities.teacher.Teacher],
    ) -> entities.schedule.Schedule:
        population = self._generate_initial_population(groups=groups, rooms=rooms, teachers=teachers)
        assert len(population) > 0, 'Empty initial population'
        best_schedule = population[0]
        generations_without_improvement = 0

        for generation in range(self._n_generations):
            new_population = []
            while len(new_population) < self._population_size:
                parent = random.choice(population)
                child = self._mutate(parent, teachers, rooms)
                if self._check_hard_constraints(child):
                    new_population.append(child)

            if self._selection_strategy == SelectionStrategy.GREEDY:
                population = list(sorted(population + new_population, reverse=True, key=lambda x: self._get_score(x)))[:self._population_size]
            elif self._selection_strategy == SelectionStrategy.RAIN:
                elite = list(sorted(population + new_population, reverse=True, key=lambda x: self._get_score(x)))[:self._population_size * 0.2]
                population = elite + random.choices(population + new_population)[:self._population_size - len(elite)]
            else:
                raise NotImplementedError()

            population.sort(key=lambda x: self._get_score(x), reverse=True)
            if self._get_score(population[0]) > self._get_score(best_schedule):
                best_schedule = population[0]
            else:
                generations_without_improvement = generations_without_improvement + 1
            current_score = self._get_score(best_schedule)
            print('Best score after {} generations: {}'.format(generations_without_improvement,
                                                               current_score))
        return best_schedule

    @staticmethod
    def _check_hard_constraints(schedule: entities.schedule.Schedule) -> bool:
        for s1 in schedule.sessions:
            for s2 in schedule.sessions:
                if s1 is s2:
                    continue
                if s1.time_slot.time != s2.time_slot.time:
                    continue
                if s1.time_slot.day != s2.time_slot.day:
                    continue
                if s1.group.name == s2.group.name or s1.room.identifier == s2.room.identifier or s1.teacher.fullname == s2.teacher.fullname:
                    return False
        return True

    @staticmethod
    def _get_score(schedule: entities.schedule.Schedule) -> float:
        # Calculate the number of "windows"
        groups = set()
        teachers = set()
        for s in schedule.sessions:
            groups.add(s.group.name)
            teachers.add(s.teacher.fullname)
        total_groups_windows = 0
        for group in groups:
            slots = []
            for session in schedule.sessions:
                if session.group.name == group:
                    slots.append(session.time_slot)
            total_groups_windows += Scheduler._calculate_windows_number(slots)
        total_teachers_windows = 0
        for teacher in teachers:
            slots = []
            for session in schedule.sessions:
                if session.teacher.fullname == teacher:
                    slots.append(session.time_slot)
            total_teachers_windows += Scheduler._calculate_windows_number(slots)

        # Calculate the total number of seats lacking
        seats_lacking = 0
        for session in schedule.sessions:
            seats_lacking += max(session.group.size - session.room.capacity, 0)

        return 1 / (1 + total_groups_windows + total_teachers_windows + seats_lacking)

    @staticmethod
    def _calculate_windows_number(time_slots: list[entities.time_slot.TimeSlot]) -> int:
        res = 0
        for day in [
            entities.time_slot.TimeSlotDay.MONDAY,
            entities.time_slot.TimeSlotDay.TUESDAY,
            entities.time_slot.TimeSlotDay.WEDNESDAY,
            entities.time_slot.TimeSlotDay.THURSDAY,
            entities.time_slot.TimeSlotDay.FRIDAY,
        ]:
            slots = [s for s in time_slots if s.day == day]
            if len(slots) > 1:
                s0 = min(slots, key=lambda s: s.time.value)
                s1 = max(slots, key=lambda s: s.time.value)
                res += (s1.time.value - s0.time.value) - len(slots) + 1
        return res

    def _generate_initial_population(
            self,
            groups: list[entities.group.Group],
            rooms: list[entities.room.Room],
            teachers: list[entities.teacher.Teacher],
    ) -> list[entities.schedule.Schedule]:
        population = []
        attempts = 0
        while len(population) < self._population_size and attempts < self._population_size * 100:
            attempts += 1
            schedule = self._try_generate_valid_schedule(groups=groups, rooms=rooms, teachers=teachers)
            if schedule is not None:
                population.append(schedule)
        return population

    def _try_generate_valid_schedule(
            self,
            groups: list[entities.group.Group],
            rooms: list[entities.room.Room],
            teachers: list[entities.teacher.Teacher],
    ) -> Optional[entities.schedule.Schedule]:
        schedule = entities.schedule.Schedule([])
        for group in groups:
            for n_sessions, subject in group.required_subjects:
                for i in range(n_sessions):
                    # We need to create a session at this group on this subject
                    teacher_candidates = [t for t in teachers if subject.name in [s.name for s in t.teachable_subjects]]
                    day_candidates = [
                        entities.time_slot.TimeSlotDay.MONDAY,
                        entities.time_slot.TimeSlotDay.TUESDAY,
                        entities.time_slot.TimeSlotDay.WEDNESDAY,
                        entities.time_slot.TimeSlotDay.THURSDAY,
                        entities.time_slot.TimeSlotDay.FRIDAY,
                    ]
                    time_candidates = [
                        entities.time_slot.TimeSlotTime.FIRST,
                        entities.time_slot.TimeSlotTime.SECOND,
                        entities.time_slot.TimeSlotTime.THIRD,
                        entities.time_slot.TimeSlotTime.FOURTH,
                        entities.time_slot.TimeSlotTime.FIFTH,
                        entities.time_slot.TimeSlotTime.SIXTH,
                    ]
                    room_candidates = rooms.copy()
                    random.shuffle(teacher_candidates)
                    random.shuffle(time_candidates)
                    random.shuffle(day_candidates)
                    random.shuffle(room_candidates)
                    session = None
                    for teacher, room, day, time in self._all_combinations_helper(teacher_candidates, room_candidates, day_candidates, time_candidates):
                        # Check if interferes with any other session
                        interferes = False
                        for session in schedule.sessions:
                            if not (session.time_slot.day == day and session.time_slot.time == time):
                                continue
                            if session.room.identifier != room.identifier and session.teacher.fullname != teacher.fullname and session.group.name != group.name:
                                continue
                            interferes = True
                            break
                        if interferes:
                            continue
                        session = entities.session.Session(room=room, group=group, teacher=teacher, subject=subject, time_slot=entities.time_slot.TimeSlot(day=day, time=time))
                        break
                    if session is None:
                        return None
                    schedule.sessions.append(session)
        assert self._check_hard_constraints(schedule)
        return schedule

    @staticmethod
    def _all_combinations_helper(*iterables):
        other_iterables = iterables[1:]
        for v in iterables[0]:
            if len(other_iterables) == 0:
                yield (v,)
            else:
                for vs in Scheduler._all_combinations_helper(*other_iterables):
                    yield v, *vs

    def _mutate(
            self,
            schedule: entities.schedule.Schedule,
            teachers: list[entities.teacher.Teacher],
            rooms: list[entities.room.Room],
    ) -> entities.schedule.Schedule:
        if random.random() < self._mutation_probability:
            return schedule

        schedule = copy.deepcopy(schedule)

        class MutationType(enum.Enum):
            CHANGE_TIME_SLOT = 0
            CHANGE_TEACHER = 1
            CHANGE_ROOM = 3
            SWAP = 4

        mutation = random.choice([MutationType.CHANGE_TIME_SLOT, MutationType.CHANGE_TEACHER, MutationType.CHANGE_ROOM, MutationType.SWAP])
        if mutation == MutationType.CHANGE_TIME_SLOT:
            session = random.choice(schedule.sessions)
            session.time_slot = entities.time_slot.TimeSlot(
                time=random.choice([
                    entities.time_slot.TimeSlotTime.FIRST,
                    entities.time_slot.TimeSlotTime.SECOND,
                    entities.time_slot.TimeSlotTime.THIRD,
                    entities.time_slot.TimeSlotTime.FOURTH,
                    entities.time_slot.TimeSlotTime.FIFTH,
                    entities.time_slot.TimeSlotTime.SIXTH,
                ]),
                day=random.choice([
                    entities.time_slot.TimeSlotDay.MONDAY,
                    entities.time_slot.TimeSlotDay.TUESDAY,
                    entities.time_slot.TimeSlotDay.WEDNESDAY,
                    entities.time_slot.TimeSlotDay.THURSDAY,
                    entities.time_slot.TimeSlotDay.FRIDAY,
                ])
            )
        elif mutation == MutationType.CHANGE_TEACHER:
            session = random.choice(schedule.sessions)
            teacher_candidates = [t for t in teachers if session.subject.name in [s.name for s in t.teachable_subjects]]
            session.teacher = random.choice(teacher_candidates)
        elif mutation == MutationType.CHANGE_ROOM:
            session = random.choice(schedule.sessions)
            session.room = random.choice(rooms)
        elif mutation == MutationType.SWAP:
            i1, i2 = random.choices(list(range(len(schedule.sessions))), k=2)
            schedule.sessions[i2].time_slot = schedule.sessions[i1].time_slot
            schedule.sessions[i1].time_slot = schedule.sessions[i2].time_slot
        else:
            raise NotImplementedError()

        return schedule
