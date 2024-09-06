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

def get_secondary_muscle_groups(exercise_ids):
    conn = connect_db()
    cursor = conn.cursor()

    placeholders = ', '.join(['?'] * len(exercise_ids))

    sql = f"""
        SELECT t1.muscle_group
        FROM muscle_groups t1
        INNER JOIN exercise_secondary_muscle_groups t2
            ON t1.id = t2.secondary_muscle_group_id
        WHERE t2.exercise_id IN ({placeholders})
    """

    cursor.execute(sql, exercise_ids)

    muscle_groups = []
    for row in cursor.fetchall():
        muscle_groups.append(row[0])
    conn.close()
    return muscle_groups

def get_weekday_exercises(weekday):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT 
            t1.exercise_id, t2.name, t1.target_sets,
            t1.target_reps_or_duration, t3.muscle_group
        FROM weekly_schedule t1
        INNER JOIN exercises t2
            ON t1.exercise_id = t2.id
        INNER JOIN muscle_groups t3
            ON t2.primary_muscle_group_id = t3.id
        WHERE t1.weekday_int = ?
    ''', (weekday_ints[weekday],))

    exercises = []

    for row in cursor.fetchall():
        exercise_id, exercise_name, target_sets, target_reps_or_duration, primary_muscle_group = row
        exercises.append({
            'exercise_name': exercise_name,
            'exercise_id': exercise_id,
            'target_sets': target_sets,
            'target_reps': target_reps_or_duration,
            'primary_muscle_group': primary_muscle_group
        })

    conn.close()
    return exercises

def check_current_workout_exists():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM current_workout_date')

    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

def get_curr_workout_data():
    conn = connect_db
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM current_workout_date')
    workout_date = cursor.fetchone()[0]

    exercises = []
    cursor.execute('SELECT * FROM current_workout_exercises')
    for row in cursor.fetchall():
        exercise_name, weight, sets, reps, difficulty, exercise_note = row
        exercises.append((exercise_name, weight, sets, None, reps, None, difficulty, exercise_note))
    
    muscle_groups = []
    cursor.execute('SELECT * FROM current_workout_muscle_groups')
    for row in cursor.fetchall():
        muscle_group, pump, soreness_before_workout, recovery_before_workout, muscle_group_note = row
        muscle_groups.append((muscle_group, pump, soreness_before_workout, recovery_before_workout, muscle_group_note))
    
    overall_workout_data = []
    cursor.execute('SELECT * FROM current_workout_overall')
    for row in cursor.fetchone():
        duration, workout_type, performance, fatigue_induced, workout_note = row
        overall_workout_data.append(duration, workout_type, performance, fatigue_induced, workout_note)

    conn.close()
    return {
        'workout_date': workout_date,
        'exercises': exercises,
        'muscle_groups': muscle_groups,
        'overall_workout_data': overall_workout_data
    }