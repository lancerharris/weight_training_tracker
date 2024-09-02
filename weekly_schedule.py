import sqlite3

def get_planned_workouts():
    conn = sqlite3.connect('weight_training_tracker.db')
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
            t2.name, t1.target_sets, t1.target_reps_or_duration
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
        weekday_name, exercise_name, target_sets, target_reps_or_duration = row
        schedule_data[weekday_name].append({
            'exercise': exercise_name,
            'sets': target_sets,
            'reps': target_reps_or_duration
        })

    conn.close()
    return schedule_data