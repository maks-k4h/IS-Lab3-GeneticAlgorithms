import argparse
from pathlib import Path

import modules


def main(args: argparse.Namespace) -> None:
    p_rooms = args.rooms
    p_groups = args.groups
    p_teachers = args.teachers
    p_schedule_dest = args.schedule_dest

    rooms = modules.filesystem.utils.import_rooms(p_rooms)
    groups = modules.filesystem.utils.import_groups(p_groups)
    teachers = modules.filesystem.utils.import_teachers(p_teachers)

    scheduler = modules.scheduler.Scheduler(
        population_size=100,
        n_generations=100,
        selection_strategy=modules.scheduler.SelectionStrategy.GREEDY,
    )
    schedule = scheduler.run(groups, rooms, teachers)
    modules.filesystem.utils.export_schedule(schedule, p_schedule_dest)
    print('Done!')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--teachers', type=Path, required=True)
    parser.add_argument('--groups', type=Path, required=True)
    parser.add_argument('--rooms', type=Path, required=True)
    parser.add_argument('schedule_dest', type=Path)
    return parser.parse_args()


if __name__ == '__main__':
    main(parse_args())
