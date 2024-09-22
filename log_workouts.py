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
    result = cursor.fetchone()
    count = result[0] if result else 0

    conn.close()
    return count > 0

def get_curr_workout_data():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM current_workout_date')
    result = cursor.fetchone()
    workout_date = result[0] if result else None

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
    for row in cursor.fetchall():
        workout_id, duration, workout_type, performance, fatigue_induced, workout_note = row
        overall_workout_data.append((workout_id, duration, workout_type, performance, fatigue_induced, workout_note))

    conn.close()
    return {
        'workout_date': workout_date,
        'exercises': exercises,
        'muscle_groups': muscle_groups,
        'overall_workout_data': overall_workout_data
    }

def save_curr_workout_data(workout_date, exercises, muscle_groups, overall_workout_data):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO current_workout_date
        VALUES (?)
    ''', (workout_date,))

    for exercise in exercises:
        cursor.execute('''
            INSERT INTO current_workout_exercises
            VALUES (?, ?, ?, ?, ?, ?)
        ''', exercise)
    
    for muscle_group in muscle_groups:
        cursor.execute('''
            INSERT INTO current_workout_muscle_groups
            VALUES (?, ?, ?, ?, ?)
        ''', muscle_group)
    
    for overall_data in overall_workout_data:
        cursor.execute('''
            INSERT INTO current_workout_overall
            VALUES (NULL, ?, ?, ?, ?, ?)
        ''', overall_data)
    
    conn.commit()
    conn.close()

def delete_curr_workout_exercise(exercise_name):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('''
        DELETE FROM current_workout_exercises
        WHERE exercise_name = ?
    ''', (exercise_name,))

    conn.commit()
    conn.close()

def delete_curr_muscle_group(muscle_group):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('''
        DELETE FROM current_workout_muscle_groups
        WHERE muscle_group = ?
    ''', (muscle_group,))

    conn.commit()
    conn.close()

def delete_curr_overall_workout(workout_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('''
        DELETE FROM current_workout_overall
        WHERE workout_id = ?
    ''', (workout_id,))

    conn.commit()
    conn.close()

def update_curr_workout_date(workout_date):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE current_workout_date
        SET date = ?
    ''', (workout_date,))

    conn.commit()
    conn.close()

def update_curr_workout_exercise(exercise_name, weight, sets, reps, difficulty, note):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE current_workout_exercises
        SET weight = ?, sets = ?, reps = ?, difficulty = ?, note = ?
        WHERE exercise_name = ?
    ''', (weight, sets, reps, difficulty, note, exercise_name))

    conn.commit()
    conn.close()

def update_curr_workout_muscle_group(muscle_group, pump, soreness_before_workout, recovery_before_workout, note):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE current_workout_muscle_groups
        SET pump = ?, soreness_before_workout = ?, recovery_before_workout = ?, note = ?
        WHERE muscle_group = ?
    ''', (pump, soreness_before_workout, recovery_before_workout, note, muscle_group))

    conn.commit()
    conn.close()

def update_curr_workout_overall(workout_id, duration, type, performance, fatigue, note):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE current_workout_overall
        SET duration_in_minutes = ?, workout_type = ?, performance = ?, fatigue_induced = ?, note = ?
        WHERE workout_id = ?
    ''', (duration, type, performance, fatigue, note, workout_id))

    conn.commit()
    conn.close()

def clear_curr_workout():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM current_workout_date')
    cursor.execute('DELETE FROM current_workout_exercises')
    cursor.execute('DELETE FROM current_workout_muscle_groups')
    cursor.execute('DELETE FROM current_workout_overall')

    conn.commit()
    conn.close()