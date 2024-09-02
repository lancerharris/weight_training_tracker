import sqlite3
import csv
import os

def connect_db():
    return sqlite3.connect('weight_training_tracker.db')

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.executescript('''
    CREATE TABLE IF NOT EXISTS exercises (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        exercise_type TEXT NOT NULL,
        primary_muscle_group_id NOT NULL,
        FOREIGN KEY (primary_muscle_group_id) REFERENCES muscle_groups(id)
    );

    CREATE TABLE IF NOT EXISTS muscle_groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        muscle_group TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS exercise_secondary_muscle_groups (
        exercise_id INTEGER,
        secondary_muscle_group_id INTEGER NOT NULL,
        FOREIGN KEY (exercise_id) REFERENCES exercised(id),
        FOREIGN KEY (secondary_muscle_group_id) REFERENCES muscle_groups(id)
        
    );

    CREATE TABLE IF NOT EXISTS muscle_groups_worked (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pump INTEGER CHECK(pump BETWEEN 1 AND 5),
        soreness_before_workout INTEGER CHECK(soreness_before_workout BETWEEN 1 AND 5),
        recovery_before_workout INTEGER CHECK(recovery_before_workout BETWEEN 1 and 5),
        muscle_group_id INTEGER NOT NULL,
        workout_id INTEGER NOT NULL,
        note_id INTEGER,
        FOREIGN KEY (muscle_group_id) REFERENCES muscle_groups(id),
        FOREIGN KEY (workout_id) REFERENCES workout(id),
        FOREIGN KEY (note_id) REFERENCES notes(id)
    );

    CREATE TABLE IF NOT EXISTS workout_exercises (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        weight REAL NOT NULL,
        sets INTEGER NOT NULL,
        reps INTEGER NOT NULL,
        difficulty INTEGER NOT NULL CHECK(difficulty BETWEEN 1 AND 5),
        exercise_id INTEGER NOT NULL,
        note_id INTEGER,
        FOREIGN KEY (exercise_id) REFERENCES exercises(id),
        FOREIGN KEY (note_id) REFERENCES notes(id)
    );

    CREATE TABLE IF NOT EXISTS workout (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        duration_in_minutes REAL NOT NULL,
        workout_type TEXT NOT NULL,
        performance INTEGER NOT NULL CHECK(performance BETWEEN 1 AND 5),
        fatigue_induced INTEGER NOT NULL CHECK(fatigue_induced BETWEEN 1 AND 5),
        note_id INTEGER,
        FOREIGN KEY (note_id) REFERENCES notes(id)
    );

    CREATE TABLE IF NOT EXISTS weekly_schedule (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        weekday_int INTEGER NOT NULL CHECK(weekday_int BETWEEN 0 and 6),
        exercise_id INTEGER,
        target_sets INTEGER,
        target_reps_or_duration INTEGER,
        FOREIGN KEY (exercise_id) REFERENCES exercises(id)
    );

    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        note TEXT NOT NULL,
        note_type TEXT NOT NULL CHECK(note_type IN ('workout', 'workout exercises', 'muscle groups'))
    );
    ''')

    # Commit and close the connection
    conn.commit()
    conn.close()

    print("Database and tables created successfully!")

def load_data_from_folder(folder_path):
    conn = connect_db()
    cursor = conn.cursor()

    for file_name in os.listdir(folder_path):
        if file_name.endswith('.csv'):
            table_name = file_name.replace('.csv', '')
            file_path = os.path.join(folder_path, file_name)
        
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file)
                fields = reader.fieldnames

                placeholders = ', '.join(['?'] * len(fields))
                insert_query = f'INSERT INTO {table_name} ({",".join(fields)}) VALUES ({placeholders})'

                for row in reader:
                    values = [row[field] for field in fields]
                    cursor.execute(insert_query, values)
                
            print(f"Data loaded successfully from {file_name} into {table_name}")

    conn.commit()
    conn.close()
