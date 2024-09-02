from flask import Flask, render_template, request, redirect, url_for
from database import create_tables, load_data_from_folder
import os

from weekly_schedule import get_planned_workouts

app = Flask(__name__)

@app.route('/')
def home():
    return redirect(url_for('schedule'))

@app.route('/schedule')
def schedule():
    schedule_data = get_planned_workouts()
    return render_template('schedule.html', schedule=schedule_data)

@app.route('/log-workout')
def log_workout():
    return render_template('log_workout.html')

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