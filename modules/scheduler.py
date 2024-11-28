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
                parent_a, parent_b = random.choices(population, k=2)
                child_a, child_b = self._crossover(parent_a, parent_b)
                child_a, child_b = self._mutate(child_a), self._mutate(child_b)
                for c in [child_a, child_b]:
                    if self._check_hard_constraints(c):
                        new_population.append(c)

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

        return best_schedule

    def _check_hard_constraints(self, schedule: entities.schedule.Schedule) -> bool:
        return True

    def _get_score(self, schedule: entities.schedule.Schedule) -> float:
        return random.random()

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
                    room_candidates = [r for r in rooms if r.capacity >= group.size]
                    random.shuffle(teacher_candidates)
                    random.shuffle(time_candidates)
                    random.shuffle(day_candidates)
                    random.shuffle(room_candidates)
                    session = None
                    for teacher, room, day, time in self._all_combinations_helper(teacher_candidates, room_candidates, day_candidates, time_candidates):
                        # Check if interferes with any other session
                        interferes = False
                        for session in schedule.sessions:
                            if not (session.time_slot.day == day and session.time_slot == time):
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

    @staticmethod
    def _crossover(
            parent_a: entities.schedule.Schedule,
            parent_b: entities.schedule.Schedule
    ) -> tuple[entities.schedule.Schedule, entities.schedule.Schedule]:
        return parent_a, parent_b

    @staticmethod
    def _mutate(schedule: entities.schedule.Schedule) -> entities.schedule.Schedule:
        return schedule
