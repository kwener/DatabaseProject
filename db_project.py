import mysql.connector
from mysql.connector import Error
import json
import tkinter as tk
from tkinter import ttk

# Establish connection to MySQL database

#you can have same goal code for different degrees
#one evaluation per goal per section


def load_config(filename="db_config.json"):
    try:
        with open(filename, "r") as file:
            config = json.load(file)
        return config
    
    except FileNotFoundError:
        print(f"Error: Configuration file '{filename}' not found.")
        return None
    
    except json.JSONDecodeError:
        print("Error: Configuration file is not a valid JSON format.")
        return None


def connect_to_database():
# Load database configuration
    config = load_config()
    if config is None:
        return None
    # Connect to the database
    try:
        conn = mysql.connector.connect(
            host=config['host'],
            user=config['user'],
            password=config['password'],
            database=config['database']
        )

        if conn.is_connected():
            print("Successfully connected to the database!")
            return conn
    except Error as e:
        print(f"Error: Unable to connect to the database.\n{e}")
        return None

    print('Connected to database')





def create_tables(conn):
    cursor = conn.cursor()
    
    #not sure if i need not null for name 
    create_course= """
            CREATE TABLE IF NOT EXISTS course (
                course_num VARCHAR(10) PRIMARY KEY,
                name VARCHAR(100) NOT NULL
            );
            """
    cursor.execute(create_course)

#i dont know if instructor name should be not null or not, it doesnt matter all that much if instructor has a name or not 
    create_instructor= """
            CREATE TABLE IF NOT EXISTS instructor (
                instructor_id VARCHAR(10) PRIMARY KEY,
                name VARCHAR(100)
            );
            """
    cursor.execute(create_instructor)


#made it so if course_num is deleted in course, the section is delected because section cannot exit without its course
#maybe make it so instructor_id can be added later? a section should prob be able to switch instructors

    create_section= """
        CREATE TABLE IF NOT EXISTS section (
            course_num VARCHAR(10),
            section_num int,
            year int,
            semester VARCHAR(8),
            num_students int,
            instructor_id VARCHAR(10),
            PRIMARY KEY(course_num, section_num, year, semester),
            FOREIGN KEY (course_num) REFERENCES course(course_num) ON DELETE CASCADE,
            FOREIGN KEY (instructor_id) REFERENCES instructor(instructor_id) ON DELETE CASCADE
        );
        """
    
    cursor.execute(create_section)

    cursor.execute("""
        SELECT COUNT(*)
        FROM information_schema.statistics
        WHERE table_name = 'section' AND index_name = 'idx_section_course';
    """)

    index_exists = cursor.fetchone()[0] > 0
    if not index_exists:
        create_index = """
            CREATE INDEX IF NOT EXISTS idx_section_course ON section(section_num, course_num
            );
            """
        cursor.execute(create_index)

    create_degree = """
            CREATE TABLE IF NOT EXISTS degree (
                degree_name VARCHAR(200),
                degree_level VARCHAR(200),
                PRIMARY KEY(degree_name, degree_level)
            );
            """
    cursor.execute(create_degree)

    create_degree_courses = """
            CREATE TABLE IF NOT EXISTS degree_courses (
                degree_name VARCHAR(200),
                degree_level VARCHAR(200),
                course_num VARCHAR(10),
                PRIMARY KEY(course_num, degree_name, degree_level),
                FOREIGN KEY (course_num) REFERENCES course(course_num) ON DELETE CASCADE,
                FOREIGN KEY (degree_name, degree_level) REFERENCES degree(degree_name, degree_level) ON DELETE CASCADE
            );
            """
    cursor.execute(create_degree_courses)

#each goal is assoiciated with a degree, each goal_num is unique to the degree 
#different degrees can have same goal_num

#how do i do delete on cascade if the combo is deleted?
    create_goal = """
            CREATE TABLE IF NOT EXISTS goal (
                goal_num CHAR(4),
                degree_name VARCHAR(200),
                degree_level VARCHAR(200),
                description VARCHAR(500), 
                PRIMARY KEY(goal_num, degree_name, degree_level),
                FOREIGN KEY (degree_name, degree_level) REFERENCES degree(degree_name, degree_level) ON DELETE CASCADE
            );
            """
    cursor.execute(create_goal)


    create_evaluation = """
            CREATE TABLE IF NOT EXISTS evaluation (
                section_num INT,
                course_num VARCHAR(10),
                goal_num CHAR(4),
                degree_name VARCHAR(200),
                degree_level VARCHAR(200),
                goal_type VARCHAR(200),
                suggestions VARCHAR(500),
                numA int,
                numB int,
                numC int,
                numF int,
                PRIMARY KEY(goal_num, degree_name, degree_level, section_num, course_num),
                FOREIGN KEY (degree_name, degree_level) 
                    REFERENCES degree(degree_name, degree_level) ON DELETE CASCADE,
                FOREIGN KEY (goal_num) REFERENCES goal(goal_num) ON DELETE CASCADE,
                FOREIGN KEY (section_num, course_num) 
                    REFERENCES section(section_num, course_num) ON DELETE CASCADE
            );
            """
    cursor.execute(create_evaluation)

    print("Tables created successfully!")

    # maybe make a table for course degree relationship?

def data_entry_window(conn):
    data_entry_window = tk.Toplevel()  # Create a new top-level window
    data_entry_window.title("Data Entry Choices")
    
    # Add buttons for each data type
    tk.Button(data_entry_window, text="Enter Degree", command=lambda: enter_degree(data_entry_window, conn)).pack(pady=10)
    tk.Button(data_entry_window, text="Enter Course", command=lambda: enter_course(data_entry_window, conn)).pack(pady=10)
    tk.Button(data_entry_window, text="Enter Instructor", command=lambda: enter_instructor(data_entry_window, conn)).pack(pady=10)
    tk.Button(data_entry_window, text="Enter Section", command=lambda: enter_section(data_entry_window, conn)).pack(pady=10)
    tk.Button(data_entry_window, text="Enter Goals", command=lambda: enter_goals(data_entry_window, conn)).pack(pady=10)
    tk.Button(data_entry_window, text="Enter Evaluation", command=lambda: enter_evaluation(data_entry_window, conn)).pack(pady=10)


def enter_degree(data_entry_window, conn):
    degree_window = tk.Toplevel()
    degree_window.title("Enter Degree")

    label_deg_name = tk.Label(degree_window, text='Degree Name')
    label_deg_name.grid(row=0, column=0)

    label_deg_level = tk.Label(degree_window, text='Degree Level')
    label_deg_level.grid(row=1, column=0)

    deg_name = tk.Entry(degree_window)  # Entry field for degree name
    deg_name.grid(row=0, column=1)
    
    deg_level = tk.Entry(degree_window)  # Entry field for degree level
    deg_level.grid(row=1, column=1)

    submit_button = tk.Button(degree_window, text="Submit", command=lambda: submit_degree(conn))
    submit_button.grid(row=2, column=1, pady=10)
     
    def submit_degree(conn):
        degree_name = deg_name.get()
        degree_level = deg_level.get()
        cursor = conn.cursor()

        if degree_name and degree_level:
            try: 
                deg_insert_query = "INSERT INTO degree (degree_name, degree_level) VALUES (%s, %s)"
                cursor.execute(deg_insert_query, (degree_name, degree_level))
                conn.commit()
                print("Degree added successfully!")
                degree_window.destroy()
            except mysql.connector.Error as e:
                print(f"Error: {e}")
        else:
            print("Please fill in both degree name and degree level.")

        # submit_button = tk.Button(degree_window, text="Submit", command=lambda: submit_degree(cursor))
        # submit_button.grid(row=2, column=1, pady=10)



def enter_course(data_entry_window, conn):
    course_window = tk.Toplevel()
    course_window.title("Enter Course")

    label_course_num = tk.Label(course_window, text='Course Number')
    label_course_num.grid(row=0, column=0)

    label_course_name = tk.Label(course_window, text='Course Name')
    label_course_name.grid(row=1, column=0)

    course_num_entry = tk.Entry(course_window)  # Entry field for course number
    course_num_entry.grid(row=0, column=1)

    course_name_entry = tk.Entry(course_window)  # Entry field for course name
    course_name_entry.grid(row=1, column=1)

    submit_button = tk.Button(course_window, text="Submit", command=lambda: submit_course(conn))
    submit_button.grid(row=2, column=1, pady=10)

    def submit_course(conn):
        course_num = course_num_entry.get()
        course_name = course_name_entry.get()
        cursor = conn.cursor()

        if course_num and course_name:
            try: 
                course_insert_query = "INSERT INTO course (course_num, name) VALUES (%s, %s)"
                cursor.execute(course_insert_query, (course_num, course_name))
                conn.commit()
                print("Course added successfully!")
                course_window.destroy()
            except mysql.connector.Error as e:
                print(f"Error: {e}")
        else:
            print("Please fill in both course number and course name.")
    

def enter_instructor(data_entry_window, conn):
    instructor_window = tk.Toplevel()
    instructor_window.title("Enter Instructor")

    label_instructor_id = tk.Label(instructor_window, text='Instructor ID')
    label_instructor_id.grid(row=0, column=0)

    label_instructor_name = tk.Label(instructor_window, text='Instructor Name')
    label_instructor_name.grid(row=1, column=0)

    instructor_id_entry = tk.Entry(instructor_window)  # Entry field for instructor ID
    instructor_id_entry.grid(row=0, column=1)

    instructor_name_entry = tk.Entry(instructor_window)  # Entry field for instructor name
    instructor_name_entry.grid(row=1, column=1)

    submit_button = tk.Button(instructor_window, text="Submit", command=lambda: submit_instructor(conn))
    submit_button.grid(row=2, column=1, pady=10)

    def submit_instructor(conn):
        instructor_id = instructor_id_entry.get()
        instructor_name = instructor_name_entry.get()
        cursor = conn.cursor()

        if instructor_id and instructor_name:
            try: 
                instructor_insert_query = "INSERT INTO instructor (instructor_id, name) VALUES (%s, %s)"
                cursor.execute(instructor_insert_query, (instructor_id, instructor_name))
                conn.commit()
                print("Instructor added successfully!")
                instructor_window.destroy()
            except mysql.connector.Error as e:
                print(f"Error: {e}")
        else:
            print("Please fill in both instructor ID and instructor name.")

def enter_section(data_entry_window, conn):
    section_window = tk.Toplevel()
    section_window.title("Enter Section")

    label_course_num = tk.Label(section_window, text='Course Number')
    label_course_num.grid(row=0, column=0)

    label_section_num = tk.Label(section_window, text='Section Number')
    label_section_num.grid(row=1, column=0)

    label_year = tk.Label(section_window, text='Year')
    label_year.grid(row=2, column=0)

    label_semester = tk.Label(section_window, text='Semester')
    label_semester.grid(row=3, column=0)

    label_num_students = tk.Label(section_window, text='Number of Students')
    label_num_students.grid(row=4, column=0)

    label_instructor_id = tk.Label(section_window, text='Instructor ID')
    label_instructor_id.grid(row=5, column=0)

    course_num_entry = tk.Entry(section_window)  # Entry field for course number
    course_num_entry.grid(row=0, column=1)

    section_num_entry = tk.Entry(section_window)  # Entry field for section number
    section_num_entry.grid(row=1, column=1)

    year_entry = tk.Entry(section_window)  # Entry field for year
    year_entry.grid(row=2, column=1)

    semester_entry = tk.Entry(section_window)  # Entry field for semester
    semester_entry.grid(row=3, column=1)

    num_students_entry = tk.Entry(section_window)  # Entry field for number of students
    num_students_entry.grid(row=4, column=1)

    instructor_id_entry = tk.Entry(section_window)  # Entry field for instructor ID
    instructor_id_entry.grid(row=5, column=1)

    submit_button = tk.Button(section_window, text="Submit", command=lambda: submit_section(conn))
    submit_button.grid(row=6, column=1, pady=10)

    def submit_section(conn):
        course_num = course_num_entry.get()
        section_num = section_num_entry.get()
        year = year_entry.get()
        semester = semester_entry.get()
        num_students = num_students_entry.get()
        instructor_id = instructor_id_entry.get()
        cursor = conn.cursor()

        if not section_num.isdigit():
            print("Error: Section number must be an integer.")
            return

        if not len(year) != 4:
            print("Error Year must be a 4-digit integer.")
            return

        if not semester.lower() in ['spring', 'summer', 'fall']:
            print("Error: Semester must be one of 'Spring', 'Summer', or 'Fall'.")
            return

        if not num_students.isdigit():
            print("Error: Number of students must be an integer.")
            return

        if course_num and section_num and year and semester and num_students and instructor_id:
            try: 
                section_insert_query = "INSERT INTO section (course_num, section_num, year, semester, num_students, instructor_id) VALUES (%s, %s, %s, %s, %s, %s)"
                cursor.execute(section_insert_query, (course_num, section_num, year, semester, num_students, instructor_id))
                conn.commit()
                print("Section added successfully!")
                section_window.destroy()
            except mysql.connector.Error as e:
                print(f"Error: {e}")
        else:
            print("Please fill in all fields.")

def enter_goals(data_entry_window, conn):
    goals_window = tk.Toplevel()
    goals_window.title("Enter Goals")

    label_goal_num = tk.Label(goals_window, text='Goal Number')
    label_goal_num.grid(row=0, column=0)

    label_degree_name = tk.Label(goals_window, text='Degree Name')
    label_degree_name.grid(row=1, column=0)

    label_degree_level = tk.Label(goals_window, text='Degree Level')
    label_degree_level.grid(row=2, column=0)

    label_description = tk.Label(goals_window, text='Description')
    label_description.grid(row=3, column=0)

    goal_num_entry = tk.Entry(goals_window)  # Entry field for goal number
    goal_num_entry.grid(row=0, column=1)

    degree_name_entry = tk.Entry(goals_window)  # Entry field for degree name
    degree_name_entry.grid(row=1, column=1)

    degree_level_entry = tk.Entry(goals_window)  # Entry field for degree level
    degree_level_entry.grid(row=2, column=1)

    description_entry = tk.Entry(goals_window)  # Entry field for description
    description_entry.grid(row=3, column=1)

    submit_button = tk.Button(goals_window, text="Submit", command=lambda: submit_goals(conn))
    submit_button.grid(row=4, column=1, pady=10)

    def submit_goals(conn):
        goal_num = goal_num_entry.get()
        degree_name = degree_name_entry.get()
        degree_level = degree_level_entry.get()
        description = description_entry.get()
        cursor = conn.cursor()

        if goal_num and degree_name and degree_level and description:
            try: 
                goals_insert_query = "INSERT INTO goal (goal_num, degree_name, degree_level, description) VALUES (%s, %s, %s, %s)"
                cursor.execute(goals_insert_query, (goal_num, degree_name, degree_level, description))
                conn.commit()
                print("Goal added successfully!")
                goals_window.destroy()
            except mysql.connector.Error as e:
                print(f"Error: {e}")
        else:
            print("Please fill in all fields.")



def enter_evaluation(data_entry_window, conn):
    evaluation_window = tk.Toplevel()
    evaluation_window.title("Evaluation Hub")

    tk.Button(evaluation_window, text="View Sections", command=lambda: view_sections(evaluation_window, conn)).pack(pady=10)



    def view_sections(evaluation_window, conn):
        semester_and_instructor_window = tk.Toplevel()
        semester_and_instructor_window.title("Enter Semester and Instructor ID")

        label_semester = tk.Label(semester_and_instructor_window, text='Semester')
        label_semester.grid(row=0, column=0)

        label_instructor_id = tk.Label(semester_and_instructor_window, text='Instructor ID')
        label_instructor_id.grid(row=1, column=0)

        semester_entry = tk.Entry(semester_and_instructor_window)  # Entry field for semester
        semester_entry.grid(row=0, column=1)

        instructor_id_entry = tk.Entry(semester_and_instructor_window)  # Entry field for instructor ID
        instructor_id_entry.grid(row=1, column=1)
                
        # sections_desc = tk.Label(semester_and_instructor_window, text='Sections:')
        # sections_desc.grid(row=3, column=0, columnspan=2)
        # sections_display = tk.Label(semester_and_instructor_window, text="", width=25, wraplength=300, relief="solid", bg="black", anchor="center", justify="center")
        # sections_display.grid(row=4, column=0, columnspan=2, pady=10)

        sections_var = tk.StringVar()  # Variable to hold selected section
        sections_dropdown = ttk.Combobox(
            semester_and_instructor_window, 
            textvariable=sections_var, 
            state="readonly",  # Prevents direct user input
            width=30
        )
        sections_dropdown.grid(row=3, column=1, pady=5)

        def get_sections():
            semester = semester_entry.get()
            instructor_id = instructor_id_entry.get()
            cursor = conn.cursor()

            if instructor_id and semester:
                cursor.execute("SELECT course_num, section_num FROM section WHERE semester = %s AND instructor_id = %s", (semester, instructor_id))
                sections = cursor.fetchall()
                if sections:
                    print(sections)
                    # sections_text = "\n".join([f"Course: {course}, Section: {section}" for course, section in sections])
                    # sections_display.config(text=sections_text)
                    # semester_and_instructor_window.update_idletasks()
                    section_options = [f"Course: {course}, Section: {section}" for course, section in sections]
                    sections_dropdown["values"] = section_options
                    sections_var.set(section_options[0])
                    return sections
                else:
                    print("No sections found for this semester and instructor.")
                    return None
            else:
                print("Please fill in both semester and instructor ID.")
                return None
        tk.Button(semester_and_instructor_window, text="Submit", command=get_sections).grid(row=2, column=1, pady=10)
        tk.Button(semester_and_instructor_window, text="View Evaluation Info", command=lambda: view_eval_info(semester_and_instructor_window, conn)).grid(row=4, column=1, pady=10)

        def view_eval_info(semester_and_instructor_window, conn):
            section = sections_var.get()
            if not section:
                print("Please select a section.")
                return

            course_num, section_num = section.split(", ")
            course_num = course_num.split(": ")[1]
            section_num = section_num.split(": ")[1]

            eval_info_window = tk.Toplevel()
            eval_info_window.title("Enter Evaluation Info")

            cursor = conn.cursor()
            query = """
                SELECT goal_num, degree_name, degree_level, goal_type, suggestions, numA, numB, numC, numF
                FROM evaluation
                WHERE course_num = %s AND section_num = %s
            """

            cursor.execute(query, (course_num, section_num))
            eval_info = cursor.fetchall()

            if eval_info:
                tk.Label(eval_info_window, text="Evaluation Info:").grid(row=0, column=0)
                for eval in eval_info:
                    eval_text = f"Goal Number: {eval[0]}\nDegree Name: {eval[1]}\nDegree Level: {eval[2]}\nGoal Type: {eval[3]}\nSuggestions: {eval[4]}\nNumber of A Grades: {eval[5]}\nNumber of B Grades: {eval[6]}\nNumber of C Grades: {eval[7]}\nNumber of F Grades: {eval[8]}\n"
                    tk.Label(eval_info_window, text=eval_text).grid(row=eval_info.index(eval) + 1, column=0)
            else:
                tk.Label(eval_info_window, text="No evaluation info found for this section.").grid(row=0, column=0)

            tk.Button(eval_info_window, text="Change/Add Evaluation Info", command=lambda: change_eval_info(eval_info_window, conn)).grid(row=len(eval_info) + 1, column=0, pady=10)

            def change_eval_info(eval_info_window, conn):
                eval_info_window.destroy()
                change_eval_window = tk.Toplevel()
                change_eval_window.title("Change/Add Evaluation Info")

                label_goal_num = tk.Label(change_eval_window, text='Goal Number')
                label_goal_num.grid(row=0, column=0)

                label_degree_name = tk.Label(change_eval_window, text='Degree Name')
                label_degree_name.grid(row=1, column=0)

                label_degree_level = tk.Label(change_eval_window, text='Degree Level')
                label_degree_level.grid(row=2, column=0)

                label_goal_type = tk.Label(change_eval_window, text='Goal Type')
                label_goal_type.grid(row=3, column=0)

                label_suggestions = tk.Label(change_eval_window, text='Suggestions')
                label_suggestions.grid(row=4, column=0)

                label_numA = tk.Label(change_eval_window, text='Number of A Grades')
                label_numA.grid(row=5, column=0)

                label_numB = tk.Label(change_eval_window, text='Number of B Grades')
                label_numB.grid(row=6, column=0)

                label_numC = tk.Label(change_eval_window, text='Number of C Grades')
                label_numC.grid(row=7, column=0)

                label_numF = tk.Label(change_eval_window, text='Number of F Grades')
                label_numF.grid(row=8, column=0)

                goal_num_entry = tk.Entry(change_eval_window)
                goal_num_entry.grid(row=0, column=1)

                degree_name_entry = tk.Entry(change_eval_window)
                degree_name_entry.grid(row=1, column=1)

                degree_level_entry = tk.Entry(change_eval_window)
                degree_level_entry.grid(row=2, column=1)

                goal_type_entry = tk.Entry(change_eval_window)
                goal_type_entry.grid(row=3, column=1)

                suggestions_entry = tk.Entry(change_eval_window)
                suggestions_entry.grid(row=4, column=1)

                numA_entry = tk.Entry(change_eval_window)
                numA_entry.grid(row=5, column=1)

                numB_entry = tk.Entry(change_eval_window)
                numB_entry.grid(row=6, column=1)

                numC_entry = tk.Entry(change_eval_window)
                numC_entry.grid(row=7, column=1)

                numF_entry = tk.Entry(change_eval_window)
                numF_entry.grid(row=8, column=1)

                tk.Button(change_eval_window, text="Submit", command=lambda: submit_eval_info()).grid(row=9, column=1, pady=10)

                def submit_eval_info():
                    goal_num = goal_num_entry.get()
                    degree_name = degree_name_entry.get()
                    degree_level = degree_level_entry.get()
                    goal_type = goal_type_entry.get()
                    suggestions = suggestions_entry.get()
                    numA = numA_entry.get()
                    numB = numB_entry.get()
                    numC = numC_entry.get()
                    numF = numF_entry.get()

                    cursor = conn.cursor()

                    if goal_num and degree_name and degree_level and goal_type and suggestions and numA and numB and numC and numF:
                        try: 
                            eval_insert_query = """
                                INSERT INTO evaluation (section_num, course_num, goal_num, degree_name, degree_level, goal_type, suggestions, numA, numB, numC, numF) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """
                            cursor.execute(eval_insert_query, (section_num, course_num, goal_num, degree_name, degree_level, goal_type, suggestions, numA, numB, numC, numF))
                            conn.commit()
                            print("Evaluation added successfully!")
                            change_eval_window.destroy()
                        except mysql.connector.Error as e:
                            print(f"Error: {e}")
                    else:
                        print("Please fill in all fields.")
        


        


            # label_goal_num = tk.Label(eval_info_window, text='Goal Number: N/A')
            # label_goal_num.grid(row=0, column=0)

            # label_goal_type = tk.Label(eval_info_window, text='Goal Type: N/A')
            # label_goal_type.grid(row=1, column=0)

            # label_suggestions = tk.Label(eval_info_window, text='Suggestions: N/A')
            # label_suggestions.grid(row=2, column=0)

            # label_numA = tk.Label(eval_info_window, text='Number of A Grades: N/A')
            # label_numA.grid(row=3, column=0)

            # label_numB = tk.Label(eval_info_window, text='Number of B Grades: N/A')
            # label_numB.grid(row=4, column=0)

            # label_numC = tk.Label(eval_info_window, text='Number of C Grades: N/A')
            # label_numC.grid(row=5, column=0)

            # label_numF = tk.Label(eval_info_window, text='Number of F Grades: N/A')
            # label_numF.grid(row=6, column=0)

            # goal_num_entry = tk.Entry(eval_info_window)



def query_window(conn):
    query_window = tk.Toplevel()
    query_window.title("Query Menu")

    tk.Label(query_window, text="Query Menu", font=("Arial", 16)).pack(pady=10)
    tk.Button(query_window, text="List Courses for a Degree", width=30,
              command=lambda: query_courses_by_degree(conn)).pack(pady=5)
    tk.Button(query_window, text="List Sections by Instructor", width=30,
              command=lambda: query_sections_by_instructor(conn)).pack(pady=5)
    tk.Button(query_window, text="Incomplete Evaluations", width=30,
              command=lambda: query_incomplete_evaluations(conn)).pack(pady=5)
    tk.Button(query_window, text="List Goals for a Degree", width=30, command=lambda: query_goals_by_degree(conn)).pack(
        pady=5)

def query_courses_by_degree(conn):
    degree_window = tk.Toplevel()
    degree_window.title("Courses by Degree")

    tk.Label(degree_window, text="Degree Name").grid(row=0, column=0)
    tk.Label(degree_window, text="Degree Level").grid(row=1, column=0)

    degree_name_entry = tk.Entry(degree_window)
    degree_name_entry.grid(row=0, column=1)
    degree_level_entry = tk.Entry(degree_window)
    degree_level_entry.grid(row=1, column=1)

    def execute_query():
        degree_name = degree_name_entry.get()
        degree_level = degree_level_entry.get()

        if not degree_name or not degree_level:
            show_error_message("Both degree name and level are required!")
            return

        cursor = conn.cursor()
        query = """
            SELECT course_num 
            FROM degree_courses
            WHERE degree_name = %s AND degree_level = %s
        """
        cursor.execute(query, (degree_name, degree_level))
        courses = cursor.fetchall()

        result_window = tk.Toplevel()
        result_window.title("Courses Result")
        if courses:
            tk.Label(result_window, text="Courses Associated with the Degree:").pack()
            for course in courses:
                tk.Label(result_window, text=course[0]).pack()
        else:
            tk.Label(result_window, text="No courses found for the specified degree.").pack()

    tk.Button(degree_window, text="Submit", command=execute_query).grid(row=2, column=1)

def query_sections_by_instructor(conn):
    instructor_window = tk.Toplevel()
    instructor_window.title("Sections by Instructor")

    tk.Label(instructor_window, text="Instructor ID").grid(row=0, column=0)
    tk.Label(instructor_window, text="Start Semester (e.g., 2022)").grid(row=1, column=0)
    tk.Label(instructor_window, text="End Semester (e.g., 2024)").grid(row=2, column=0)

    instructor_id_entry = tk.Entry(instructor_window)
    instructor_id_entry.grid(row=0, column=1)
    start_semester_entry = tk.Entry(instructor_window)
    start_semester_entry.grid(row=1, column=1)
    end_semester_entry = tk.Entry(instructor_window)
    end_semester_entry.grid(row=2, column=1)

    def execute_query():
        instructor_id = instructor_id_entry.get()
        start_semester = start_semester_entry.get()
        end_semester = end_semester_entry.get()

        if not instructor_id or not start_semester or not end_semester:
            show_error_message("All fields are required!")
            return

        cursor = conn.cursor()
        query = """
            SELECT course_num, section_num, year, semester
            FROM section
            WHERE instructor_id = %s AND year BETWEEN %s AND %s
            ORDER BY year, semester
        """
        cursor.execute(query, (instructor_id, start_semester, end_semester))
        sections = cursor.fetchall()

        result_window = tk.Toplevel()
        result_window.title("Sections Result")
        if sections:
            tk.Label(result_window, text="Sections Taught by the Instructor:").pack()
            for section in sections:
                section_info = f"Course: {section[0]}, Section: {section[1]}, Year: {section[2]}, Semester: {section[3]}"
                tk.Label(result_window, text=section_info).pack()
        else:
            tk.Label(result_window, text="No sections found for the specified criteria.").pack()

    tk.Button(instructor_window, text="Submit", command=execute_query).grid(row=3, column=1)

def query_incomplete_evaluations(conn):
    eval_window = tk.Toplevel()
    eval_window.title("Incomplete Evaluations")

    tk.Label(eval_window, text="Semester (e.g., Spring 2024)").grid(row=0, column=0)
    semester_entry = tk.Entry(eval_window)
    semester_entry.grid(row=0, column=1)

    def execute_query():
        semester = semester_entry.get()
        if not semester:
            show_error_message("Semester is required!")
            return

        cursor = conn.cursor()
        query = """
            SELECT course_num, section_num
            FROM evaluation
            WHERE semester = %s AND (numA IS NULL OR numB IS NULL OR numC IS NULL OR numF IS NULL)
        """
        cursor.execute(query, (semester,))
        results = cursor.fetchall()

        result_window = tk.Toplevel()
        result_window.title("Incomplete Evaluations Result")
        if results:
            tk.Label(result_window, text="Sections with Incomplete Evaluations:").pack()
            for result in results:
                tk.Label(result_window, text=f"Course: {result[0]}, Section: {result[1]}").pack()
        else:
            tk.Label(result_window, text="No incomplete evaluations found for the given semester.").pack()

    tk.Button(eval_window, text="Submit", command=execute_query).grid(row=1, column=1)

def query_goals_by_degree(conn):
    degree_window = tk.Toplevel()
    degree_window.title("Goals by Degree")

    tk.Label(degree_window, text="Degree Name").grid(row=0, column=0)
    tk.Label(degree_window, text="Degree Level").grid(row=1, column=0)

    degree_name_entry = tk.Entry(degree_window)
    degree_name_entry.grid(row=0, column=1)
    degree_level_entry = tk.Entry(degree_window)
    degree_level_entry.grid(row=1, column=1)

    def execute_query():
        degree_name = degree_name_entry.get()
        degree_level = degree_level_entry.get()

        if not degree_name or not degree_level:
            show_error_message("Both degree name and level are required!")
            return

        cursor = conn.cursor()
        query = """
            SELECT goal_num, description
            FROM goal
            WHERE degree_name = %s AND degree_level = %s
        """
        cursor.execute(query, (degree_name, degree_level))
        goals = cursor.fetchall()

        result_window = tk.Toplevel()
        result_window.title("Goals Result")
        if goals:
            tk.Label(result_window, text="Goals Associated with the Degree:").pack()
            for goal in goals:
                tk.Label(result_window, text=f"Goal {goal[0]}: {goal[1]}").pack()
        else:
            tk.Label(result_window, text="No goals found for the specified degree.").pack()

    tk.Button(degree_window, text="Submit", command=execute_query).grid(row=2, column=1)

#https://www.geeksforgeeks.org/python-gui-tkinter/
def main_menu(conn):
    #mycursor = conn.cursor()
    def open_data_entry():
        data_entry_window(conn)

    def open_query_menu():
        query_window(conn)

    root = tk.Tk()
    root.title("Academic Database Manager")
    root.geometry("400x300")

    tk.Label(root, text="Main Menu", font=("Arial", 16)).pack(pady=20)

    tk.Button(root, text="Data Entry", width=20, command=open_data_entry).pack(pady=10)
    tk.Button(root, text="Query Menu", width=20, command=open_query_menu).pack(pady=10)

    root.mainloop()

def main():
    conn = connect_to_database()
    create_tables(conn)
    main_menu(conn)

if __name__ == "__main__":
    main()
