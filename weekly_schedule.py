import sqlite3
from database import connect_db

weekday_ints = {
    'Sunday': 0,
    'Monday': 1,
    'Tuesday': 2,
    'Wednesday': 3,
    'Thursday': 4,
    'Friday': 5,
    'Saturday': 6
}

def get_planned_workouts():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT 
            case 
                when t1.weekday_int = 0 then 'Sunday'
                when t1.weekday_int = 1 then 'Monday'
                when t1.weekday_int = 2 then 'Tuesday'
                when t1.weekday_int = 3 then 'Wednesday'
                when t1.weekday_int = 4 then 'Thursday'
                when t1.weekday_int = 5 then 'Friday'
                when t1.weekday_int = 6 then 'Saturday'
                end as weekday_name,
            t2.name, t1.exercise_id, t1.target_sets, t1.target_reps_or_duration
        FROM weekly_schedule t1
        INNER JOIN exercises t2
            ON t1.exercise_id = t2.id
    ''')

    schedule_data = {
        'Monday': [],
        'Tuesday': [],
        'Wednesday': [],
        'Thursday': [],
        'Friday': [],
        'Saturday': [],
        'Sunday': []
    }

    for row in cursor.fetchall():
        weekday_name, exercise_name, exercise_id, target_sets, target_reps_or_duration = row
        schedule_data[weekday_name].append({
            'exercise': exercise_name,
            'exercise_id': exercise_id,
            'sets': target_sets,
            'reps': target_reps_or_duration
        })

    conn.close()
    return schedule_data

def add_exercise_from_library(exercise_id, day_of_week, sets, reps):
    conn = connect_db()
    cursor = conn.cursor()
    print(f"day_of_week: {day_of_week}")
    weekday_int = weekday_ints[day_of_week]

    sets = int(sets) if sets != '' else 0
    sets = max(sets, 0)
    reps = int(reps) if reps != '' else 0
    reps = max(reps, 0)

    cursor.execute('''
        INSERT INTO weekly_schedule (weekday_int, exercise_id, target_sets, target_reps_or_duration)
        VALUES (?, ?, ?, ?)
    ''', (weekday_int, exercise_id, sets, reps))

    conn.commit()
    conn.close()

def delete_exercise_from_schedule(exercise_id, day_of_week):
    conn = connect_db()
    cursor = conn.cursor()
    print(f"day_of_week: {day_of_week}")
    print(f"exercise_id: {exercise_id}")
    weekday_int = weekday_ints[day_of_week]

    cursor.execute('''
        DELETE FROM weekly_schedule
        WHERE weekday_int = ? AND exercise_id = ?
    ''', (weekday_int, exercise_id))

    conn.commit()
    conn.close()