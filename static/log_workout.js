document.addEventListener('DOMContentLoaded', function() {
    function debounce(func, delay) {
        let debounceTimer;
        return function() {
            const context = this;
            const args = arguments;
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => func.apply(context, args), delay);
        };
    }

    function sendUpdate(endpoint, data) {
        return fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (response.status === 200) {
                return response.json();
            } else {
                throw new Error('Update failed');
            }
        })
    }

    const workoutDateInput = document.getElementById('workout-date');
    if (workoutDateInput) {

        workoutDateInput.addEventListener('input', debounce(function() {
            const oldValue = this.defaultValue;
            sendUpdate('/update_curr_workout_date', {
                workout_date: this.value
            })
            .catch((error) => {
                this.value = oldValue;
                alert(error.message);
                console.error('Error:', error);
                throw error;
            });
        }, 500));
    }


    const exerciseContainers = document.querySelectorAll('.exercise-info');
    exerciseContainers.forEach(container => {
        const exerciseName = container.querySelector('p').innerText.trim();
        const weightInput = container.querySelector('input[name="weight_used"]');
        const setsInput = container.querySelector('input[name="sets_completed"]');
        const repsInput = container.querySelector('input[name="reps_completed"]');
        const difficultySelect = container.querySelector('input[name="difficulty"]');
        const notesTextarea = container.querySelector('textarea[name="exercise_notes"]');
        
        exercise_info = {
            exercise_name: exerciseName,
            weight_used: weightInput ? weightInput.value : null,
            sets_completed: setsInput ? setsInput.value : null,
            reps_completed: repsInput ? repsInput.value : null,
            difficulty: difficultySelect ? difficultySelect.value : null,
            exercise_notes: notesTextarea ? notesTextarea.value : null
        }

        if (weightInput) {
            weightInput.addEventListener('change', debounce(function() {
                exercise_info.weight_used = this.value;
                sendUpdate('/update_curr_workout_exercise', exercise_info);
            }, 500));
        }

        if (setsInput) {
            setsInput.addEventListener('change', debounce(function() {
                exercise_info.sets_completed = this.value;
                sendUpdate('/update_curr_workout_exercise', exercise_info);
            }, 500));
        }
        
        if (repsInput) {
            repsInput.addEventListener('change', debounce(function() {
                exercise_info.reps_completed = this.value;
                sendUpdate('/update_curr_workout_exercise', exercise_info);
            }, 500));
        }
        
        if (difficultySelect) {
            difficultySelect.addEventListener('change', debounce(function() {
                exercise_info.difficulty = this.value;
                sendUpdate('/update_curr_workout_exercise', exercise_info);
            }, 500));
        }
        
        if (notesTextarea) {
            notesTextarea.addEventListener('change', debounce(function() {
                exercise_info.exercise_notes = this.value;
                sendUpdate('/update_curr_workout_exercise', exercise_info);
            }, 500));
        }
    })

    const muscleGroupContainers = document.querySelectorAll('.log-container-muscle');
    muscleGroupContainers.forEach(container => {
        const muscleGroupName = container.querySelector('p').innerText.trim();
        const pumpLevelSelect = container.querySelector('select[name="pump_level"]');
        const sorenessLevelSelect = container.querySelector('select[name="pre_workout_soreness"]');
        const recoveryLevelSelect = container.querySelector('select[name="pre_workout_recovery"]');
        const notesTextarea = container.querySelector('textarea[name="muscle_group_notes"]');

        muscle_info = {
            muscle_group_name: muscleGroupName,
            pump_level: pumpLevelSelect ? pumpLevelSelect.value : null,
            pre_workout_soreness: sorenessLevelSelect ? sorenessLevelSelect.value : null,
            pre_workout_recovery: recoveryLevelSelect ? recoveryLevelSelect.value : null,
            muscle_group_notes: notesTextarea ? notesTextarea.value : null
        }

        if (pumpLevelSelect) {
            pumpLevelSelect.addEventListener('change', debounce(function() {
                muscle_info.pump_level = this.value;
                sendUpdate('/update_curr_workout_muscle_group', muscle_info);
            }, 500));
        }
        
        if (sorenessLevelSelect) {
            sorenessLevelSelect.addEventListener('change', debounce(function() {
                muscle_info.pre_workout_soreness = this.value;
                sendUpdate('/update_curr_workout_muscle_group', muscle_info);
            }, 500));
        }
        
        if (recoveryLevelSelect) {
            recoveryLevelSelect.addEventListener('change', debounce(function() {
                muscle_info.pre_workout_recovery = this.value;
                sendUpdate('/update_curr_workout_muscle_group', muscle_info);
            }, 500));
        }
        
        if (notesTextarea) {
            notesTextarea.addEventListener('change', debounce(function() {
                muscle_info.muscle_group_notes = this.value;
                sendUpdate('/update_curr_workout_muscle_group', muscle_info);
            }, 500));
        }
    })

    const overallWorkoutContainers = document.querySelectorAll('.log-container-overall');
    overallWorkoutContainers.forEach(container => {
        const workoutId = container.querySelector('input[name="workout_id"]')?.value;
        const durationInput = container.querySelector('input[name="workout_duration"]');
        const typeSelect = container.querySelector('select[name="workout_type"]');
        const performanceSelect = container.querySelector('select[name="performance_rating"]');
        const fatigueSelect = container.querySelector('select[name="fatigue_induced"]');
        const notesTextarea = container.querySelector('textarea[name="workout_notes"]');

        workout_info = {
            workout_id: workoutId,
            workout_duration: durationInput ? durationInput.value : null,
            workout_type: typeSelect ? typeSelect.value : null,
            performance_rating: performanceSelect ? performanceSelect.value : null,
            fatigue_induced: fatigueSelect ? fatigueSelect.value : null,
            workout_notes: notesTextarea ? notesTextarea.value : null
        }

        if (durationInput) {
            durationInput.addEventListener('change', debounce(function() {
                workout_info.workout_duration = this.value;
                sendUpdate('/update_curr_workout_overall', workout_info);
            }, 500));
        }
        
        if (typeSelect) {
            typeSelect.addEventListener('change', debounce(function() {
                workout_info.workout_type = this.value;
                sendUpdate('/update_curr_workout_overall', workout_info);
            }, 500));
        }
        
        if (performanceSelect) {
            performanceSelect.addEventListener('change', debounce(function() {
                workout_info.performance_rating = this.value;
                sendUpdate('/update_curr_workout_overall', workout_info);
            }, 500));
        }
        
        if (fatigueSelect) {
            fatigueSelect.addEventListener('change', debounce(function() {
                workout_info.fatigue_induced = this.value;
                sendUpdate('/update_curr_workout_overall', workout_info);
            }, 500));
        }
        
        if (notesTextarea) {
            notesTextarea.addEventListener('change', debounce(function() {
                workout_info.workout_notes = this.value;
                sendUpdate('/update_curr_workout_overall', workout_info);
            }, 500));
        }
    })

})