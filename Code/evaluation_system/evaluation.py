import streamlit as st
import contextlib
import io
import json

# Problem statements for coding challenge
questions = [
    {
        'statement': 'Missing number in array: Given an array of size N-1 such that it only contains distinct integers in the range of 1 to N. Find the missing element.',
        'examples': [{'N': 5, 'A': [1, 2, 3, 5], 'Output': 4}, {'N': 6, 'A': [1, 2, 3, 4, 5, 7], 'Output': 6}],
    },
    {
        'statement': 'Number of pairs: Given two arrays X and Y of positive integers, find the number of pairs such that xy > yx (raised to power of) where x is an element from X and y is an element from Y.',
        'examples': [{'M': 3, 'X': [2, 1, 6], 'N': 2, 'Y': [1, 5], 'Output': 3}, {'M': 2, 'X': [2, 3], 'N': 2, 'Y': [1, 4], 'Output': 3}],
    },
    {
        'statement': 'Minimum Platforms: Given arrival and departure times of all trains that reach a railway station. Find the minimum number of platforms required for the railway station so that no train is kept waiting. Consider that all the trains arrive on the same day and leave on the same day. Arrival and departure time can never be the same for a train but we can have arrival time of one train equal to departure time of the other. At any given instance of time, same platform can not be used for both departure of a train and arrival of another train. In such cases, we need different platforms.',
        'examples': [
            {'n': 6, 'arr': [900, 940, 950, 1100, 1500, 1800], 'dep': [910, 1200, 1120, 1130, 1900, 2000], 'Output': 3},
            {'n': 4, 'arr': [800, 820, 850, 900], 'dep': [810, 830, 840, 920], 'Output': 2},
        ],
    },
]

# Initialize session state
if 'user_data' not in st.session_state:
    st.session_state.user_data = []

# Streamlit UI
st.title('Doodle Coding Challenge')

# Display questions and text areas for user code input
for i, q in enumerate(questions):
    st.write(f"Question {i + 1}: {q['statement']}")
    st.write(f"Examples: {q['examples']}")
    user_code = st.text_area(f"Enter your Python code for Question {i + 1}:", height=300)

    # Button to evaluate the code
    if st.button(f'Run Code for Question {i + 1}'):
        st.write("Executing your code...")

        # Create a function to encapsulate the user's code
        def execute_user_code():
            try:
                exec(user_code)
            except Exception as e:
                st.error(f"Error during execution: {str(e)}")

        # Capture the standard output
        captured_output = io.StringIO()
        with contextlib.redirect_stdout(captured_output):
            execute_user_code()

        # Check each example
        for example in q['examples']:
            expected_output = str(example['Output']).strip()

            # Compare the output with the expected output
            if captured_output.getvalue().strip() == expected_output:
                st.success(f"Correct Answer for Example {q['examples'].index(example) + 1}!")
                is_correct = True
            else:
                st.error(f"Incorrect Answer for Example {q['examples'].index(example) + 1}. Expected: {expected_output}, Got: {captured_output.getvalue().strip()}")
                is_correct = False

            # Save user data
            st.session_state.user_data.append({
                'question': q['statement'],
                'user_code': user_code,
                'example': example,
                'is_correct': is_correct
            })
        
# st.success("Submitted successfully! Your solutions are under review.")
if st.button("Submit Coding Assessment"):
    st.write("Submitted successfully! Your solutions are under review..")

    # Save to JSON file
    with open('solutions12.json', 'w') as file:
        json.dump(st.session_state.user_data, file, indent=4)


