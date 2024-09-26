from flask import Flask, jsonify, render_template, request, redirect, url_for
from database import create_tables, get_exercises_and_muscle_groups, get_muscle_groups, load_data_from_folder
import os
from datetime import date

from weekly_schedule import add_exercise_from_library, delete_exercise_from_schedule, get_planned_workouts
from log_workouts import add_exercise_to_log, add_muscle_group_to_log, add_overall_workout_to_log, check_current_workout_exists, delete_curr_muscle_group, delete_curr_overall_workout, delete_curr_workout, delete_curr_workout_exercise, get_curr_workout_data, get_secondary_muscle_groups, get_weekday_exercises, save_curr_workout_data, update_curr_workout_date, update_curr_workout_exercise, update_curr_workout_muscle_group, update_curr_workout_overall

app = Flask(__name__)

@app.route('/')
def home():
    return redirect(url_for('schedule'))

@app.route('/schedule')
def schedule():
    exercises = get_exercises_and_muscle_groups()
    schedule_data = get_planned_workouts()
    return render_template('schedule.html', schedule=schedule_data, exercises=exercises)

@app.route('/add_exercises_to_schedule', methods=['POST'])
def add_exercises_to_schedule():
    selected_exercises = request.form.getlist('selected_exercises')
    if selected_exercises:
        for exercise_id in selected_exercises:
            add_exercise_from_library(exercise_id, request.form.get('day_of_week'), request.form.get('sets'), request.form.get('reps'))
    return redirect(url_for('schedule'))

@app.route('/add_exercises_to_log', methods=['POST'])
def add_exercises_to_log():
    selected_exercises = sorted(request.form.getlist('selected_exercises'))
    exercise_ids = request.form.getlist('exercise_id')
    weights = request.form.getlist('weight')
    sets = request.form.getlist('sets')
    reps = request.form.getlist('reps')

    selected_exercise_indicators = [False] * len(exercise_ids)

    for i in range(len(exercise_ids)):
        if exercise_ids[i] in selected_exercises:
            selected_exercise_indicators[i] = True
        if selected_exercise_indicators[i] == True or weights[i] != '' or sets[i] != '' or reps[i] != '':
            add_exercise_to_log(exercise_ids[i], weights[i], sets[i], reps[i])

    
    return redirect(url_for('log_workout'))

@app.route('/add_muscle_group_to_log', methods=['POST'])
def add_muscle_groups_to_log():
    selected_muscle_groups = request.form.getlist('selected_muscle_groups')
    if selected_muscle_groups:
        for muscle_group in selected_muscle_groups:
            add_muscle_group_to_log(muscle_group, request.form.get('pump_level_add'), request.form.get('pre_workout_soreness_add'), request.form.get('pre_workout_recovery_add'))
    return redirect(url_for('log_workout'))

@app.route('/delete_scheduled_exercise', methods=['POST'])
def delete_scheduled_exercise():
    delete_exercise_from_schedule(request.form.get('exercise_id'), request.form.get('day_of_week'))
    return redirect(url_for('schedule'))

@app.route('/log-workout')
def log_workout():
    no_overall_workout_data = False
    curr_workout_exists = check_current_workout_exists()
    print(f"curr_workout_exists: {curr_workout_exists}")

    if not curr_workout_exists:
        workout_date = date.today().strftime("%Y-%m-%d")
        weekday = date.today().strftime("%A")
        weekday_exercises = get_weekday_exercises(weekday)
        exercise_ids = [exercise['exercise_id'] for exercise in weekday_exercises]
        primary_muscle_groups = [exercise['primary_muscle_group'] for exercise in weekday_exercises]
        secondary_muscle_groups = get_secondary_muscle_groups(exercise_ids)
        muscle_group_names = list(set(primary_muscle_groups).union(secondary_muscle_groups))
        
        exercises = [(exercise['exercise_name'], None, None, exercise['target_sets'], None, exercise['target_reps'], 3, '') for exercise in weekday_exercises]
        muscle_groups = [(muscle_group, 3, 1, 5, '') for muscle_group in muscle_group_names]
        overall_workout_data = [(None, "Push", 4, 3, '')]

        exercise_save_data = [(exercise[0], exercise[1], exercise[2], exercise[3], exercise[4], exercise[5], exercise[6], exercise[7]) for exercise in exercises]
        save_curr_workout_data(workout_date, exercise_save_data, muscle_groups, overall_workout_data)

    curr_workout_dict = get_curr_workout_data()
    if curr_workout_dict['workout_date'] is None:
        workout_date = date.today().strftime("%Y-%m-%d")
    else:
        workout_date = date.fromisoformat(curr_workout_dict['workout_date'])
    exercises = curr_workout_dict['exercises']
    
    muscle_groups = curr_workout_dict['muscle_groups']
    overall_workout_data = curr_workout_dict['overall_workout_data']
    if len(overall_workout_data) == 0:
        no_overall_workout_data = True
        overall_workout_data = [(0, "Push", 4, 3, '')]
        add_overall_workout_to_log(overall_workout_data[0][0], overall_workout_data[0][1], overall_workout_data[0][2], overall_workout_data[0][3])

    exercises_in_library = [exercise for exercise in get_exercises_and_muscle_groups() if exercise['name'] not in [e[0] for e in exercises]]
    muscle_groups_in_db = [muscle_group['muscle_group'] for muscle_group in get_muscle_groups() if muscle_group['muscle_group'] not in [mg[0] for mg in muscle_groups]]

    return render_template(
        'log_workout.html',
        workout_date=workout_date,
        exercises=exercises,
        muscle_groups=muscle_groups,
        overall=overall_workout_data,
        no_overall_workout_data=no_overall_workout_data,
        exercises_in_library=exercises_in_library,
        muscle_groups_in_db=muscle_groups_in_db
    )

@app.route('/update_curr_workout_date', methods=['POST'])
def update_log_workout_date():
    workout_date = request.json.get('workout_date')
    update_curr_workout_date(workout_date)
    return jsonify({"message": "Workout date updated successfully"}), 200

@app.route('/update_curr_workout_exercise', methods=['POST'])
def update_log_exercise():
    exercise_name = request.json.get('exercise_name')
    weight = request.json.get('weight_used')
    sets = request.json.get('sets_completed')
    reps = request.json.get('reps_completed')
    difficulty = request.json.get('difficulty')
    print(difficulty)
    note = request.json.get('exercise_notes')
    update_curr_workout_exercise(exercise_name, weight, sets, reps, difficulty, note)
    return jsonify({"message": "Exercise updated successfully"}), 200

@app.route('/update_curr_workout_muscle_group', methods=['POST'])
def update_log_muscle_group():
    muscle_group = request.json.get('muscle_group_name')
    pump = request.json.get('pump_level')
    soreness_before_workout = request.json.get('pre_workout_soreness')
    recovery_before_workout = request.json.get('pre_workout_recovery')
    note = request.json.get('muscle_group_notes')
    update_curr_workout_muscle_group(muscle_group, pump, soreness_before_workout, recovery_before_workout, note)
    return jsonify({"message": "Muscle group updated successfully"}), 200

@app.route('/update_curr_workout_overall', methods=['POST'])
def update_log_overall_workout():
    workout_id = request.json.get('workout_id')
    duration = request.json.get('workout_duration')
    type = request.json.get('workout_type')
    performance = request.json.get('performance_rating')
    fatigue = request.json.get('fatigue_induced')
    note = request.json.get('workout_notes')
    update_curr_workout_overall(workout_id, duration, type, performance, fatigue, note)
    return jsonify({"message": "Overall workout updated successfully"}), 200

@app.route('/delete_log_exercise', methods=['POST'])
def delete_log_exercise():
    exercise_name = request.form.get('exercise_name')
    print(f"exercise_name: {exercise_name}")
    delete_curr_workout_exercise(exercise_name)
    return redirect(url_for('log_workout'))

@app.route('/delete_log_muscle_group', methods=['POST'])
def delete_log_muscle_group():
    muscle_group = request.form.get('muscle_group')
    delete_curr_muscle_group(muscle_group)
    return redirect(url_for('log_workout'))

@app.route('/delete_log_overall_workout', methods=['POST'])
def delete_log_overall_workout():
    workout_id = request.form.get('workout_id')
    delete_curr_overall_workout(workout_id)
    return redirect(url_for('log_workout'))

@app.route('/clear_current_workout', methods=['POST'])
def clear_current_workout():
    delete_curr_workout()
    overall_workout_data = [(0, "Push", 4, 3, '')]
    add_overall_workout_to_log(overall_workout_data[0][0], overall_workout_data[0][1], overall_workout_data[0][2], overall_workout_data[0][3])
    return redirect(url_for('log_workout'))

@app.route('/use_scheduled_workout', methods=['POST'])
def use_scheduled_workout():
    delete_curr_workout()
    print('hello    ')
    return redirect(url_for('log_workout'))

@app.route('/exercise-library')
def exercise_library():
    return render_template('exercise_library.html')

@app.route('/logs')
def logs():
    return render_template('logs.html')

@app.route('/progress')
def progress():
    return render_template('progress.html')

if __name__ == '__main__':
    create_tables()
    if not os.path.exists('weight_training_tracker.db'):
        load_data_from_folder('baseline_data')
    app.run(debug=True)