from flask import Flask, render_template
from database import create_tables, load_data_from_folder
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    if not os.path.exists('weight_training_tracker.db'):
        create_tables()
        load_data_from_folder('baseline_data')
    app.run(debug=True)