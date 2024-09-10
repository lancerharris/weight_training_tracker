from flask import Flask, render_template, request, redirect, url_for
from database import create_tables, get_exercises_and_muscle_groups, load_data_from_folder
import os
from datetime import date

from weekly_schedule import add_exercise_from_library, delete_exercise_from_schedule, get_planned_workouts
from log_workouts import check_current_workout_exists, delete_curr_muscle_group, delete_curr_overall_workout, delete_curr_workout_exercise, get_curr_workout_data, get_secondary_muscle_groups, get_weekday_exercises, save_curr_workout_data

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

@app.route('/delete_scheduled_exercise', methods=['POST'])
def delete_scheduled_exercise():
    delete_exercise_from_schedule(request.form.get('exercise_id'), request.form.get('day_of_week'))
    return redirect(url_for('schedule'))

@app.route('/log-workout')
def log_workout():
    curr_workout_exists = check_current_workout_exists()
    if not curr_workout_exists:
        print('hello world, no current workout exists')
        workout_date = date.today().strftime("%Y-%m-%d")
        weekday = date.today().strftime("%A")
        weekday_exercises = get_weekday_exercises(weekday)
        exercise_ids = [exercise['exercise_id'] for exercise in weekday_exercises]
        primary_muscle_groups = [exercise['primary_muscle_group'] for exercise in weekday_exercises]
        secondary_muscle_groups = get_secondary_muscle_groups(exercise_ids)
        muscle_group_names = list(set(primary_muscle_groups).union(secondary_muscle_groups))
        
        exercises = [(exercise['exercise_name'], None, None, exercise['target_sets'], None, exercise['target_reps'], 3, '') for exercise in weekday_exercises]
        muscle_groups = [(muscle_group, 3, 1, 5, '') for muscle_group in muscle_group_names]
        overall_workout_data = [(None, "Push", 4, 3, '', None)]

        exercise_save_data = [(exercise[0], exercise[1], exercise[2], exercise[4], exercise[6], exercise[7]) for exercise in exercises]
        save_curr_workout_data(workout_date, exercise_save_data, muscle_groups, overall_workout_data)

    curr_workout_dict = get_curr_workout_data()
    workout_date = curr_workout_dict['workout_date']
    exercises = curr_workout_dict['exercises']
    # TODO look to see if there are target sets and reps on the weekly schedule and pull in if so
    muscle_groups = curr_workout_dict['muscle_groups']
    if not curr_workout_dict['overall_workout_data']:
        overall_workout_data = [(None, "Push", 4, 3, '', None)]
        # TODO: save overall workout data need to get exercise data situated correctly first
    overall_workout_data = curr_workout_dict['overall_workout_data']

    return render_template(
        'log_workout.html',
        workout_date=workout_date,
        exercises=exercises,
        muscle_groups=muscle_groups,
        overall=overall_workout_data
    )

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