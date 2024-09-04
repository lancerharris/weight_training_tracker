from flask import Flask, render_template, request, redirect, url_for
from database import create_tables, get_exercises_and_muscle_groups, load_data_from_folder
import os
from datetime import date

from weekly_schedule import add_exercise_from_library, delete_exercise_from_schedule, get_planned_workouts, get_weekday_exercises

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
    print(request.form)
    delete_exercise_from_schedule(request.form.get('exercise_id'), request.form.get('day_of_week'))
    return redirect(url_for('schedule'))

@app.route('/log-workout')
def log_workout():
    todays_date = date.today().strftime("%Y-%m-%d")
    weekday = date.today().strftime("%A")
    starter_exercises = get_weekday_exercises(weekday)
    return render_template('log_workout.html', todays_date=todays_date, weekday_exercises=starter_exercises)

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
    if not os.path.exists('weight_training_tracker.db'):
        create_tables()
        load_data_from_folder('baseline_data')
    app.run(debug=True)