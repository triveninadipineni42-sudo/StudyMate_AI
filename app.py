
import streamlit as st
import pandas as pd
from datetime import date

from database import (
    create_tables,
    add_note,
    get_notes,
    delete_note,
    add_study_plan,
    get_study_plans,
    add_quiz_result,
    get_quiz_results
)

from ai_helper import (
    generate_ai_response,
    generate_quiz
)


# ---------------- CONFIGURATION ----------------

st.set_page_config(
    page_title="StudyMate AI",
    page_icon="📚",
    layout="wide"
)

create_tables()

if "ai_questions" not in st.session_state:
    st.session_state.ai_questions = []

if "ai_quiz_submitted" not in st.session_state:
    st.session_state.ai_quiz_submitted = False

if "ai_quiz_config" not in st.session_state:
    st.session_state.ai_quiz_config = {}


# ---------------- HEADER ----------------

st.title("📚 StudyMate AI")
st.subheader("Your Personal AI Study Assistant")

st.write(
    "Plan your studies, manage notes and improve your learning with AI."
)


# ---------------- SIDEBAR ----------------

st.sidebar.title("📚 StudyMate AI")

menu = st.sidebar.radio(
    "Choose a section",
    [
        "Dashboard",
        "Study Timetable",
        "My Notes",
        "Quiz Generator",
        "AI Study Assistant",
        "Progress Tracker"
    ]
)


# ---------------- DASHBOARD ----------------

if menu == "Dashboard":

    st.header("🏠 Dashboard")

    plans = get_study_plans()
    notes = get_notes()
    results = get_quiz_results()

    subjects = set(plan[1] for plan in plans)

    total_hours = sum(plan[3] for plan in plans)

    total_quizzes = len(results)

    average_score = (
        sum(result[4] for result in results) / total_quizzes
        if total_quizzes else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Subjects", len(subjects))
    col2.metric("Study Hours", total_hours)
    col3.metric("Total Notes", len(notes))
    col4.metric("Average Quiz Score", f"{average_score:.1f}%")

    st.info("Welcome to your StudyMate AI dashboard!")

    st.subheader("📅 Your Study Plans")

    if plans:
        for plan in plans:
            st.write(
                f"📚 **{plan[1]}** | {plan[2]} | {plan[3]} hours"
            )
    else:
        st.info("No study plans added yet.")

    st.subheader("🧠 Quiz Performance")

    if results:
        col1, col2 = st.columns(2)

        col1.metric("Total Quizzes", total_quizzes)

        col2.metric(
            "Best Score",
            f"{max(result[4] for result in results):.1f}%"
        )
    else:
        st.info("No quiz results yet.")


# ---------------- STUDY TIMETABLE ----------------

elif menu == "Study Timetable":

    st.header("📅 Study Timetable")

    with st.form("study_plan_form"):

        subject = st.text_input("Enter Subject")

        study_date = st.date_input(
            "Select Date",
            date.today()
        )

        hours = st.number_input(
            "Study Hours",
            min_value=1,
            max_value=12,
            value=1
        )

        submitted = st.form_submit_button("Add Study Plan")

    if submitted:

        if subject.strip():

            add_study_plan(
                subject.strip(),
                study_date,
                int(hours)
            )

            st.success("Study plan saved!")
            st.rerun()

        else:
            st.warning("Please enter a subject.")

    st.subheader("📋 Your Saved Study Plans")

    plans = get_study_plans()

    if plans:

        for plan in plans:
            st.write(
                f"**{plan[0]}. {plan[1]}** - "
                f"{plan[2]} - {plan[3]} hours"
            )

    else:
        st.info("No study plans available.")


# ---------------- MY NOTES ----------------

elif menu == "My Notes":

    st.header("📝 My Notes")

    with st.form("notes_form"):

        title = st.text_input("Note Title")

        content = st.text_area(
            "Write your notes here",
            height=180
        )

        submitted = st.form_submit_button("Save Note")

    if submitted:

        if title.strip() and content.strip():

            add_note(title.strip(), content.strip())

            st.success("Your note has been saved!")
            st.rerun()

        else:
            st.warning("Please enter title and notes.")

    st.subheader("📚 Saved Notes")

    notes = get_notes()

    if notes:

        for note in notes:

            with st.expander(note[1]):

                st.write(note[2])

                if st.button(
                    "Delete Note",
                    key=f"delete_{note[0]}"
                ):

                    delete_note(note[0])
                    st.success("Note deleted!")
                    st.rerun()

    else:
        st.info("No notes saved yet.")


# ---------------- AI QUIZ GENERATOR ----------------

elif menu == "Quiz Generator":

    st.header("🧠 AI Quiz Generator")

    st.write(
        "Choose any subject and topic. AI will create an interactive quiz."
    )

    subjects = [
        "Python",
        "Java",
        "C Programming",
        "C++",
        "JavaScript",
        "HTML & CSS",
        "DBMS",
        "Data Structures",
        "Computer Networks",
        "Operating Systems",
        "Mathematics",
        "Physics",
        "Chemistry",
        "Biology",
        "General Knowledge",
        "Other"
    ]

    with st.form("ai_quiz_settings"):

        subject = st.selectbox(
            "Choose Subject",
            subjects
        )

        custom_subject = ""

        if subject == "Other":
            custom_subject = st.text_input("Enter your subject")

        topic = st.text_input(
            "Enter Quiz Topic",
            placeholder="Example: Python Loops, SQL Joins, Java Classes"
        )

        difficulty = st.selectbox(
            "Choose Difficulty",
            ["Easy", "Medium", "Hard"]
        )

        number_questions = st.selectbox(
            "Number of Questions",
            [5, 10, 15]
        )

        generate = st.form_submit_button(
            "🚀 Generate AI Quiz"
        )

    if generate:

        final_subject = (
            custom_subject.strip()
            if subject == "Other"
            else subject
        )

        if not final_subject:
            st.error("Please enter a subject.")

        elif not topic.strip():
            st.warning("Please enter a quiz topic.")

        else:

            try:

                with st.spinner(
                    "🤖 AI is preparing your quiz. Please wait..."
                ):

                    questions = generate_quiz(
                        f"{final_subject}: {topic}",
                        difficulty,
                        number_questions
                    )

                st.session_state.ai_questions = questions

                st.session_state.ai_quiz_submitted = False

                st.session_state.ai_quiz_config = {
                    "topic": f"{final_subject}: {topic}",
                    "difficulty": difficulty
                }

                st.success("Your AI quiz is ready!")

            except Exception as e:

                st.error(f"Unable to generate quiz: {e}")

    # DISPLAY INTERACTIVE QUIZ

    if st.session_state.ai_questions:

        questions = st.session_state.ai_questions

        config = st.session_state.ai_quiz_config

        st.divider()

        st.subheader("📝 Your Interactive Quiz")

        st.write(
            f"**Topic:** {config['topic']} | "
            f"**Difficulty:** {config['difficulty']}"
        )

        if not st.session_state.ai_quiz_submitted:

            with st.form("interactive_ai_quiz"):

                answers = []

                for i, question in enumerate(questions):

                    st.markdown(
                        f"### Question {i+1}"
                    )

                    st.write(question["question"])

                    answer = st.radio(
                        "Select your answer:",
                        question["options"],
                        index=None,
                        key=f"ai_answer_{i}"
                    )

                    answers.append(answer)

                    st.divider()

                submitted = st.form_submit_button(
                    "✅ Submit Quiz",
                    use_container_width=True
                )

            if submitted:

                if any(answer is None for answer in answers):

                    st.warning(
                        "Please answer all questions before submitting."
                    )

                else:

                    score = sum(
                        answers[i] == question["answer"]
                        for i, question in enumerate(questions)
                    )

                    percentage = (
                        score / len(questions)
                    ) * 100

                    add_quiz_result(
                        config["topic"],
                        score,
                        len(questions),
                        percentage
                    )

                    st.session_state.ai_quiz_answers = answers

                    st.session_state.ai_quiz_score = score

                    st.session_state.ai_quiz_percentage = percentage

                    st.session_state.ai_quiz_submitted = True

                    st.rerun()

        # QUIZ RESULTS

        if st.session_state.ai_quiz_submitted:

            score = st.session_state.ai_quiz_score

            percentage = st.session_state.ai_quiz_percentage

            answers = st.session_state.ai_quiz_answers

            st.subheader("📊 Your Quiz Results")

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Your Score",
                f"{score}/{len(questions)}"
            )

            col2.metric(
                "Accuracy",
                f"{percentage:.1f}%"
            )

            col3.metric(
                "Correct Answers",
                score
            )

            st.progress(int(percentage))

            if percentage == 100:
                st.balloons()
                st.success("Excellent! Perfect score! 🎉")

            elif percentage >= 60:
                st.success("Great job! Keep practicing! 👏")

            else:
                st.info("Keep learning. You can improve! 💪")

            st.subheader("📖 Answer Review")

            for i, question in enumerate(questions):

                st.markdown(
                    f"### Question {i+1}"
                )

                st.write(question["question"])

                if answers[i] == question["answer"]:

                    st.success(
                        f"Correct answer: {question['answer']}"
                    )

                else:

                    st.error(
                        f"Your answer: {answers[i]}"
                    )

                    st.info(
                        f"Correct answer: {question['answer']}"
                    )

                st.write(
                    f"**Explanation:** {question['explanation']}"
                )

                st.divider()

            if st.button("🔄 Generate Another Quiz"):

                st.session_state.ai_questions = []

                st.session_state.ai_quiz_submitted = False

                st.rerun()


# ---------------- AI STUDY ASSISTANT ----------------

elif menu == "AI Study Assistant":

    st.header("🤖 AI Study Assistant")

    st.write(
        "Summarize notes, extract important points and create study plans."
    )

    tab1, tab2, tab3 = st.tabs([
        "📝 Notes Summary",
        "⭐ Important Points",
        "📅 AI Study Plan"
    ])

    with tab1:

        st.subheader("AI Notes Summarizer")

        notes_text = st.text_area(
            "Paste your study notes",
            height=200
        )

        if st.button("Generate Summary"):

            if notes_text.strip():

                try:

                    with st.spinner("AI is summarizing..."):

                        result = generate_ai_response(
                            f"Summarize these student notes in simple language "
                            f"with headings and key definitions:\n{notes_text}"
                        )

                    st.success("Summary generated!")

                    st.markdown(result)

                except Exception as e:
                    st.error(f"AI Error: {e}")

            else:
                st.warning("Please paste your notes.")

    with tab2:

        st.subheader("Important Points Generator")

        material = st.text_area(
            "Paste your study material",
            height=200
        )

        if st.button("Extract Important Points"):

            if material.strip():

                try:

                    with st.spinner("Finding important points..."):

                        result = generate_ai_response(
                            f"Extract exam-important concepts, definitions, "
                            f"facts and revision points from these notes:\n{material}"
                        )

                    st.success("Important points generated!")

                    st.markdown(result)

                except Exception as e:
                    st.error(f"AI Error: {e}")

            else:
                st.warning("Please enter study material.")

    with tab3:

        st.subheader("AI Personalized Study Plan")

        study_subject = st.text_input(
            "Enter Subject",
            placeholder="Python Programming"
        )

        days = st.number_input(
            "Number of Days",
            min_value=1,
            max_value=90,
            value=7
        )

        daily_hours = st.number_input(
            "Study Hours Per Day",
            min_value=1,
            max_value=12,
            value=2
        )

        level = st.selectbox(
            "Knowledge Level",
            ["Beginner", "Intermediate", "Advanced"]
        )

        if st.button("Create AI Study Plan"):

            if study_subject.strip():

                try:

                    with st.spinner("Creating your study plan..."):

                        result = generate_ai_response(
                            f"Create a {days}-day study plan for "
                            f"{study_subject}. Student level: {level}. "
                            f"Available hours per day: {daily_hours}. "
                            f"Include daily topics, exercises and revision."
                        )

                    st.success("Your personalized plan is ready!")

                    st.markdown(result)

                except Exception as e:
                    st.error(f"AI Error: {e}")

            else:
                st.warning("Please enter a subject.")


# ---------------- PROGRESS TRACKER ----------------

elif menu == "Progress Tracker":

    st.header("📊 Progress Tracker")

    progress = st.slider(
        "Your study progress",
        0,
        100,
        0
    )

    st.progress(progress)

    st.write(f"Your study progress: {progress}%")

    if progress == 100:
        st.success("Congratulations! Goal completed!")

    elif progress >= 50:
        st.info("Great progress! Keep going.")

    else:
        st.warning("Keep studying. You can do it!")

    st.divider()

    st.subheader("🧠 Quiz Performance Analysis")

    results = get_quiz_results()

    if results:

        total_quizzes = len(results)

        average_score = sum(
            result[4] for result in results
        ) / total_quizzes

        best_score = max(
            result[4] for result in results
        )

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Quizzes", total_quizzes)

        col2.metric("Average Score", f"{average_score:.1f}%")

        col3.metric("Best Score", f"{best_score:.1f}%")

        chart_data = pd.DataFrame({
            "Quiz": [
                f"Quiz {i+1}"
                for i in range(total_quizzes)
            ],
            "Percentage": [
                result[4]
                for result in reversed(results)
            ]
        })

        st.subheader("📈 Quiz Performance Graph")

        st.bar_chart(
            chart_data,
            x="Quiz",
            y="Percentage"
        )

        st.subheader("📋 Previous Quiz Results")

        history_data = []

        for result in results:

            history_data.append({
                "Topic": result[1],
                "Score": f"{result[2]}/{result[3]}",
                "Percentage": f"{result[4]:.1f}%",
                "Date": result[5]
            })

        st.dataframe(
            pd.DataFrame(history_data),
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No quiz results yet.")
