import mysql.connector
from mysql.connector import Error
import json
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
# TODO change errors to messageboxes

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
            section_num int(3),
            year int,
            semester VARCHAR(8),
            num_students int,
            instructor_id VARCHAR(10),
            PRIMARY KEY(course_num, section_num, year, semester),
            FOREIGN KEY (course_num) REFERENCES course(course_num) ON DELETE CASCADE,
            FOREIGN KEY (instructor_id) REFERENCES instructor(instructor_id) ON DELETE CASCADE,
            UNIQUE INDEX idx_section_composite (section_num, course_num, year, semester)
        );
        """
    
    cursor.execute(create_section)

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
                UNIQUE (course_num, degree_name, degree_level),
                FOREIGN KEY (course_num) REFERENCES course(course_num) ON DELETE CASCADE,
                FOREIGN KEY (degree_name, degree_level) REFERENCES degree(degree_name, degree_level) ON DELETE CASCADE
                
            );
            """
    cursor.execute(create_degree_courses)

#each goal is assoiciated with a degree, each num is unique to the degree
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

    drop_eval = """
    DROP TABLE IF EXISTS evaluation;

"""
    #cursor.execute(drop_eval)

    create_evaluation = """
            CREATE TABLE IF NOT EXISTS evaluation (
                section_num INT(3),
                year INT,
                semester VARCHAR(8),
                course_num VARCHAR(10),
                goal_num CHAR(4),
                degree_name VARCHAR(200),
                degree_level VARCHAR(200),
                goal_type VARCHAR(200),
                suggestions VARCHAR(500) DEFAULT NULL,
                suggestions_complete INT DEFAULT 0,
                numA int DEFAULT NULL,
                numB int DEFAULT NULL,
                numC int DEFAULT NULL,
                numF int DEFAULT NULL,
                PRIMARY KEY(goal_num, degree_name, degree_level, section_num, course_num, year, semester),
                FOREIGN KEY (goal_num, degree_name, degree_level) REFERENCES goal(goal_num, degree_name, degree_level) ON DELETE CASCADE,
                FOREIGN KEY (course_num, degree_name, degree_level) REFERENCES degree_courses(course_num, degree_name, degree_level) ON DELETE CASCADE,
                FOREIGN KEY (course_num, section_num, year, semester) 
                    REFERENCES section(course_num, section_num, year, semester) ON DELETE CASCADE
            );
            """
    
    cursor.execute(create_evaluation)


    create_goal_courses = """
            CREATE TABLE IF NOT EXISTS goal_courses (
                goal_num CHAR(4),
                degree_name VARCHAR(200),
                degree_level VARCHAR(200),
                course_num VARCHAR(10),
                PRIMARY KEY(goal_num, degree_name, degree_level, course_num),
                FOREIGN KEY (course_num, degree_name, degree_level) REFERENCES degree_courses(course_num, degree_name, degree_level) ON DELETE CASCADE,
                FOREIGN KEY (goal_num, degree_name, degree_level) REFERENCES goal(goal_num, degree_name, degree_level) ON DELETE CASCADE
            );
            """
    cursor.execute(create_goal_courses)


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
    tk.Button(data_entry_window, text="Associate a Course and a Degree", command=lambda: associate_degree_and_course(data_entry_window, conn)).pack(pady=10)

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
                associate_courses_options(conn, degree_name, degree_level)
                degree_window.destroy()
            except mysql.connector.Error as e:
                print(f"Error: {e}")
        else:
            print("Please fill in both degree name and degree level.")
    def associate_courses_options(conn, degree_name, degree_level):
        association_window = tk.Toplevel()
        association_window.title("Do you want to associate courses with this degree? ")
        tk.Label(association_window, text="Choose an option to associate courses with the degree:").grid(row=0, column=0, pady=10)

        def associate_existing():
            associate_courses(conn, degree_name, degree_level)
            association_window.destroy()

        def create_new_course():
            create_new_course_window(conn, degree_name, degree_level)
            association_window.destroy()

        tk.Button(association_window, text="Associate Existing Courses", command=associate_existing).grid(row=1, column=0, pady=10)
        tk.Button(association_window, text="Create New Course", command=create_new_course).grid(row=2, column=0, pady=10)
        tk.Button(association_window, text="Don't Associate a Course", command=association_window.destroy).grid(row=3, column=0, pady=10)




    def associate_courses(conn, degree_name, degree_level):

        course_window = tk.Toplevel()
        course_window.title("Associate Existing Courses")

        tk.Label(course_window, text = "Select Existing Courses").grid(row = 0, column = 0)

        cursor = conn.cursor()
        cursor.execute ("SELECT course_num, name FROM course")
        courses = cursor.fetchall()

        course_listbox = tk.Listbox(course_window, selectmode = tk.MULTIPLE, width = 50)
        for course in courses:
            course_listbox.insert(tk.END, f"{course[0]} :{course[1]}")
            
        course_listbox.grid(row = 1, column = 0, pady = 10)

        def add_selected_courses():
            selected_indices = course_listbox.curselection()
            for index in selected_indices:
                course_num = courses[index][0]
                try:
                    insert_course_deg = """
                    INSERT INTO degree_courses (degree_name, degree_level, course_num)
                    VALUES (%s, %s, %s)
                    """

                    cursor.execute(insert_course_deg, (degree_name, degree_level, course_num))   
                    
                except mysql.connector.Error as e:
                    print(f"Error adding course {course_num}: {e}")
                conn.commit()
                print("Course(s) associated with degree successfully!")

                try:
                    get_goal_query = """
                        SELECT goal_num
                        FROM goal
                        WHERE degree_name = %s and degree_level = %s
                    """
                    cursor.execute(get_goal_query, (degree_name, degree_level))
                    goal_nums = cursor.fetchall() 

                    goal_courses_query= """
                        INSERT INTO goal_courses (goal_num, degree_name, degree_level, course_num)
                        VALUES (%s, %s, %s, %s)
                        """
                    
                    for goal_num in goal_nums:
                        cursor.execute(goal_courses_query, (goal_num, degree_name, degree_level, course_num))      

                    conn.commit()
                    print("New course associated with all degree goals successfully!")

                except mysql.connector.Error as e:
                    print(f"Error: {e}")


            course_window.destroy()

        tk.Button(course_window, text="Add Selected Courses", command=add_selected_courses).grid(row=2, column=0)


    # Create new course and associate it with degree
    def create_new_course_window(conn, degree_name, degree_level):
        new_course_window = tk.Toplevel()
        new_course_window.title("Create New Course")

        tk.Label(new_course_window, text="Enter New Course Information").grid(row=0, column=0, pady=10)

        new_course_num_label = tk.Label(new_course_window, text="Course Number")
        new_course_num_label.grid(row=1, column=0)
        new_course_num_entry = tk.Entry(new_course_window)
        new_course_num_entry.grid(row=1, column=1)

        new_course_name_label = tk.Label(new_course_window, text="Course Name")
        new_course_name_label.grid(row=2, column=0)
        new_course_name_entry = tk.Entry(new_course_window)
        new_course_name_entry.grid(row=2, column=1)

        def add_new_course():
            new_course_num = new_course_num_entry.get()
            new_course_name = new_course_name_entry.get()

            if new_course_num and new_course_name:
                try:
                    cursor = conn.cursor()
                    # Insert new course into the 'course' table
                    insert_new_course_query = """
                    INSERT INTO course (course_num, name) VALUES (%s, %s)
                    """
                    cursor.execute(insert_new_course_query, (new_course_num, new_course_name))
                    conn.commit()
                    print(f"New course {new_course_num} added successfully!")

                    # Now associate this new course with the degree
                    insert_course_deg = """
                    INSERT INTO degree_courses (degree_name, degree_level, course_num)
                    VALUES (%s, %s, %s)
                    """
                    cursor.execute(insert_course_deg, (degree_name, degree_level, new_course_num))
                    conn.commit()
                    print("New course associated with the degree successfully!")

                    new_course_window.destroy()  # Close the window after adding
                except mysql.connector.Error as e:
                    print(f"Error adding new course: {e}")
            else:
                print("Please provide both course number and course name.")


            try:
                get_goal_query = """
                    SELECT goal_num
                    FROM goal
                    WHERE degree_name = %s and degree_level = %s
                """
                cursor.execute(get_goal_query, (degree_name, degree_level))
                goal_nums = cursor.fetchall() 

                goal_courses_query= """
                    INSERT INTO goal_courses (goal_num, degree_name, degree_level, course_num)
                    VALUES (%s, %s, %s, %s)
                    """
                
                for goal_num in goal_nums:
                    cursor.execute(goal_courses_query, (goal_num, degree_name, degree_level, new_course_num))      

                conn.commit()
                print("New course associated with all degree goals successfully!")

            except mysql.connector.Error as e:
                print(f"Error: {e}")


        tk.Button(new_course_window, text="Add New Course", command=add_new_course).grid(row=3, column=0, pady=10)       



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
                associate_course_with_degree(conn, course_num, course_name)
                course_window.destroy()
            except mysql.connector.Error as e:
                print(f"Error: {e}")
        else:
            print("Please fill in both course number and course name.")

    def associate_course_with_degree(conn, course_num, course_name):
        association_window = tk.Toplevel()
        association_window.title(f"Associate {course_name} with a Degree")

        tk.Label(association_window, text="Select a Degree to associate this course with:").grid(row=0, column=0, pady=10)
        tk.Button(association_window, text="Don't Associate a Course", command=association_window.destroy).grid(row=3, column=0, pady=10)
        cursor = conn.cursor()
        cursor.execute("SELECT degree_name, degree_level FROM degree")
        degrees = cursor.fetchall()

        degree_listbox = tk.Listbox(association_window, selectmode=tk.SINGLE, width=50)
        for degree in degrees:
            degree_listbox.insert(tk.END, f"{degree[0]} - {degree[1]}")
        
        degree_listbox.grid(row=1, column=0, pady=10)

        def add_association():
            selected_index = degree_listbox.curselection()
            if selected_index:
                
                degree_name, degree_level = degrees[selected_index[0]]
                try:
                    # Insert the course-degree association into the degree_course table
                    insert_course_degree_query = """
                    INSERT INTO degree_courses (degree_name, degree_level, course_num)
                    VALUES (%s, %s, %s)
                    """
                    cursor.execute(insert_course_degree_query, (degree_name, degree_level, course_num))
                    conn.commit()
                    print(f"Course {course_num} associated with {degree_name} successfully!")

                    try:
                        get_goal_query = """
                            SELECT goal_num
                            FROM goal
                            WHERE degree_name = %s and degree_level = %s
                        """

                        cursor.execute(get_goal_query, (degree_name, degree_level))
                        goal_nums = cursor.fetchall() 
                        print(goal_nums)
                        
                        goal_courses_query= """
                            INSERT INTO goal_courses (goal_num, degree_name, degree_level, course_num)
                            VALUES (%s, %s, %s, %s)
                            """
                        
                        for goal_num in goal_nums:
                            cursor.execute(goal_courses_query, (goal_num[0], degree_name, degree_level, course_num))      

                        conn.commit()
                        print("New course associated with all degree goals successfully!")

                    except mysql.connector.Error as e:
                        print(f"Error: {e}")


                    association_window.destroy()  # Close the association window
                except mysql.connector.Error as e:
                    print(f"Error associating course {course_num} with degree: {e}")
            else:
                print("Please select a degree to associate with the course.")


            
        tk.Button(association_window, text="Associate", command=add_association).grid(row=2, column=0, pady=10)
    

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
        try:
            course_num = course_num_entry.get()
            section_num = section_num_entry.get()
            year = year_entry.get()
            year = int(year)
            semester = semester_entry.get()
            num_students = num_students_entry.get()
            instructor_id = instructor_id_entry.get()
            cursor = conn.cursor()
        
            if not section_num.isdigit():
                print("Error: Section number must be an integer.")
                tk.Label(section_window, 
                                text="Error: Section number must be an integer."
                            ).grid(row=7, column=0)
                return

            if not len(year) == 4 or year < 1600:
                print("Error Year must be a 4-digit integer.")
                tk.Label(section_window, 
                                text="Error: Year must be a 4 digit integer above 1600."
                            ).grid(row=7, column=0)
                return

            if not semester.lower() in ['spring', 'summer', 'fall']:
                print("Error: Semester must be one of 'Spring', 'Summer', or 'Fall'.")
                tk.Label(section_window, 
                                text="Error: Semester must be one of Spring, Summer, or Fall."
                            ).grid(row=7, column=0)
                return

            if not num_students.isdigit():
                tk.Label(section_window, 
                                text="Error: Number of Students."
                            ).grid(row=7, column=0)
                return

            if course_num and section_num and year and semester and num_students and instructor_id:
                try: 
                    section_insert_query = "INSERT INTO section (course_num, section_num, year, semester, num_students, instructor_id) VALUES (%s, %s, %s, %s, %s, %s)"
                    cursor.execute(section_insert_query, (course_num, section_num, year, semester, num_students, instructor_id))
                    conn.commit()
                    print("Section added successfully!")
                    section_window.destroy()
                except mysql.connector.Error as e:
                    tk.Label(section_window, 
                                text=f"Error: {e}\nPlease ensure that both course number and instructor id have already been added to the table!"
                            ).grid(row=7, column=0)
            else:
                tk.Label(section_window, 
                                text="Please fill in all fields"
                            ).grid(row=7, column=0)
        except Exception as e:
                tk.Label(section_window, 
                                text=f"{e}: Please make sure all values are entered correctly"
                            ).grid(row=7, column=0)



def associate_degree_and_course(data_entry_window, conn):
    deg_course_window = tk.Toplevel()
    deg_course_window.title("Associate a degree and a course")

    label_course_id= tk.Label(deg_course_window, text='Course ID')
    label_course_id.grid(row=0, column=0)

    label_degree_name = tk.Label(deg_course_window, text='Degree name')
    label_degree_name.grid(row=1, column=0)

    label_degree_level = tk.Label(deg_course_window, text='Degree level')
    label_degree_level.grid(row=2, column=0)

    course_id_entry = tk.Entry(deg_course_window)
    course_id_entry.grid(row=0, column=1)

    degree_name_entry = tk.Entry(deg_course_window)  
    degree_name_entry.grid(row=1, column=1)

    degree_level_entry = tk.Entry(deg_course_window)  
    degree_level_entry.grid(row=2, column=1)


    submit_button = tk.Button(deg_course_window, text="Submit", command=lambda: submit_course_deg(conn))
    submit_button.grid(row=3, column=1, pady=10)

    def submit_course_deg(conn):
        course_id = course_id_entry.get()
        degree_name = degree_name_entry.get()
        degree_level = degree_level_entry.get()
        cursor = conn.cursor()

        if course_id and degree_name and degree_level:
            try:
                insert_course_deg = """
                INSERT INTO degree_courses (degree_name, degree_level, course_num)
                VALUES (%s, %s, %s)
                """

                cursor.execute(insert_course_deg, (degree_name, degree_level, course_id))
                print('Association between course and degree made successfully!')

                try:
                    goal_query = ''' 
                    SELECT goal_num
                    FROM goal
                    WHERE degree_name = %s AND degree_level = %s
                    '''

                    cursor.execute(goal_query, (degree_name, degree_level))
                    goal_nums = cursor.fetchall()

                    goals_courses_insert_query = """
                        INSERT INTO goal_courses (goal_num, degree_name, degree_level, course_num)
                        VALUES (%s, %s, %s, %s)
                    """         
                    for goal_num in goal_nums:
                        cursor.execute(goals_courses_insert_query, (goal_num[0], degree_name, degree_level, course_id))

                    conn.commit()
                    print("Goal and all courses for the degree associated successfully!")
                    deg_course_window.destroy()

                except mysql.connector.Error as e:
                    print(f"Error: {e}")

            except mysql.connector.Error as e:
                print(f"Error connecting {course_id} : {e}")
                tk.Label(deg_course_window, text="Unable to associate the given course and degree, please try again").grid(row=4, column=1, pady=10)

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
            
                try:
                    course_num_query = ''' 
                    SELECT course_num
                    FROM degree_courses
                    WHERE degree_name = %s AND degree_level = %s
                    '''

                    cursor.execute(course_num_query, (degree_name, degree_level))
                    course_nums = cursor.fetchall()

                    goals_courses_insert_query = """
                        INSERT INTO goal_courses (goal_num, degree_name, degree_level, course_num)
                        VALUES (%s, %s, %s, %s)
                 """         
                    for course_num in course_nums:
                        cursor.execute(goals_courses_insert_query, (goal_num, degree_name, degree_level, course_num[0]))

                    conn.commit()
                    print("Goal and all courses for the degree associated successfully!")
                    goals_window.destroy()


                except mysql.connector.Error as e:
                    print(f"Error: {e}")

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
        semester_and_instructor_window.title("Enter Semester, Year and Instructor ID")

        label_semester = tk.Label(semester_and_instructor_window, text='Semester (Spring, Summer, or Fall)')
        label_semester.grid(row=0, column=0)

        label_year = tk.Label(semester_and_instructor_window, text='Year')
        label_year.grid(row=1, column=0)

        label_instructor_id = tk.Label(semester_and_instructor_window, text='Instructor ID')
        label_instructor_id.grid(row=2, column=0)


        semester_entry = tk.Entry(semester_and_instructor_window)  # Entry field for semester
        semester_entry.grid(row=0, column=1)

        year_entry = tk.Entry(semester_and_instructor_window)  # Entry field for instructor ID
        year_entry.grid(row=1, column=1)

        instructor_id_entry = tk.Entry(semester_and_instructor_window)  # Entry field for instructor ID
        instructor_id_entry.grid(row=2, column=1)

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
            year = year_entry.get()
            instructor_id = instructor_id_entry.get()
            cursor = conn.cursor()

            if instructor_id and semester and year:
                cursor.execute("SELECT course_num, section_num FROM section WHERE semester = %s AND instructor_id = %s and year = %s", (semester, instructor_id, year))
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
                    print("No sections found for this semester, year, and instructor.")
                    return None
            else:
                print("Please fill in semester, year, and instructor ID.")
                return None
        tk.Button(semester_and_instructor_window, text="Submit", command=get_sections).grid(row=4, column=1, pady=10)
        tk.Button(semester_and_instructor_window, text="View Evaluation Info", command=lambda: view_eval_info(semester_and_instructor_window, conn)).grid(row=5, column=1, pady=10)

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
                SELECT goal_num, degree_name, degree_level, goal_type, suggestions, suggestions_complete, numA, numB, numC, numF
                FROM evaluation
                WHERE course_num = %s AND section_num = %s
            """

            cursor.execute(query, (course_num, section_num))
            eval_info = cursor.fetchall()

            if eval_info:
                tk.Label(eval_info_window, text="Evaluation Info:").grid(row=0, column=0)
                for eval in eval_info:
                    eval_text = f"Goal Number: {eval[0]}\nDegree Name: {eval[1]}\nDegree Level: {eval[2]}\nGoal Type: {eval[3]}\nSuggestions: {eval[4]}\nSuggestions complete? {"Yes" if eval[5] else "No"}\nNumber of A Grades: {eval[6]}\nNumber of B Grades: {eval[7]}\nNumber of C Grades: {eval[8]}\nNumber of F Grades: {eval[9]}\n"
                    tk.Label(eval_info_window, text=eval_text).grid(row=eval_info.index(eval) + 1, column=0)
            else:
                tk.Label(eval_info_window, text="No evaluation info found for this section.").grid(row=0, column=0)

            tk.Button(eval_info_window, text="Change/Add Evaluation Info", command=lambda: change_eval_info(eval_info_window, conn)).grid(row=len(eval_info) + 1, column=0, pady=10)

            def change_eval_info(eval_info_window, conn):
                eval_info_window.destroy()
                change_eval_window = tk.Toplevel()
                change_eval_window.title("Change/Add Evaluation Info")

                # label_year = tk.Label(change_eval_window, text='Year')
                # label_year.grid(row=0, column=0)

                label_goal_num = tk.Label(change_eval_window, text='Goal Number')
                label_goal_num.grid(row=1, column=0)

                label_degree_name = tk.Label(change_eval_window, text='Degree Name')
                label_degree_name.grid(row=2, column=0)

                label_degree_level = tk.Label(change_eval_window, text='Degree Level')
                label_degree_level.grid(row=3, column=0)

                label_goal_type = tk.Label(change_eval_window, text='Goal Type')
                label_goal_type.grid(row=4, column=0)

                label_suggestions = tk.Label(change_eval_window, text='Suggestions')
                label_suggestions.grid(row=5, column=0)

                label_suggestions_complete = tk.Label(change_eval_window, text='Suggestions Complete? (Enter 0 for yes and 1 for no)')
                label_suggestions_complete.grid(row=6, column=0)

                label_numA = tk.Label(change_eval_window, text='Number of A Grades')
                label_numA.grid(row=7, column=0)

                label_numB = tk.Label(change_eval_window, text='Number of B Grades')
                label_numB.grid(row=8, column=0)

                label_numC = tk.Label(change_eval_window, text='Number of C Grades')
                label_numC.grid(row=9, column=0)

                label_numF = tk.Label(change_eval_window, text='Number of F Grades')
                label_numF.grid(row=10, column=0)

                # year_entry = tk.Entry(change_eval_window)
                # year_entry.grid(row=0, column=1)

                goal_num_entry = tk.Entry(change_eval_window)
                goal_num_entry.grid(row=1, column=1)

                degree_name_entry = tk.Entry(change_eval_window)
                degree_name_entry.grid(row=2, column=1)

                degree_level_entry = tk.Entry(change_eval_window)
                degree_level_entry.grid(row=3, column=1)

                goal_type_entry = tk.Entry(change_eval_window)
                goal_type_entry.grid(row=4, column=1)

                suggestions_entry = tk.Entry(change_eval_window)
                suggestions_entry.grid(row=5, column=1)

                suggestions_complete_entry = tk.Entry(change_eval_window)
                suggestions_complete_entry.grid(row=6, column=1)

                numA_entry = tk.Entry(change_eval_window)
                numA_entry.grid(row=7, column=1)

                numB_entry = tk.Entry(change_eval_window)
                numB_entry.grid(row=8, column=1)

                numC_entry = tk.Entry(change_eval_window)
                numC_entry.grid(row=9, column=1)

                numF_entry = tk.Entry(change_eval_window)
                numF_entry.grid(row=10, column=1)

                tk.Button(change_eval_window, text="Submit", command=lambda: submit_eval_info()).grid(row=13, column=1, pady=10)

                def submit_eval_info():
                    goal_num = goal_num_entry.get()
                    semester = semester_entry.get()
                    year = year_entry.get()
                    degree_name = degree_name_entry.get()
                    degree_level = degree_level_entry.get()
                    goal_type = goal_type_entry.get()
                    suggestions = suggestions_entry.get() if suggestions_entry.get().strip() else None
                    suggestions_complete = suggestions_complete_entry.get()

                    # Ensure suggestions_complete is valid (0 or 1)
                    if suggestions_complete not in ['0', '1']:
                        suggestions_complete = None
                        tk.Label(
                            change_eval_window, 
                            text="Invalid value for 'Suggestions Complete'. Set to default value NO (NULL)."
                        ).grid(row=12, column=0)

                    numA = int(numA_entry.get()) if numA_entry.get().strip() else None
                    numB = int(numB_entry.get()) if numB_entry.get().strip() else None
                    numC = int(numC_entry.get()) if numC_entry.get().strip() else None
                    numF = int(numF_entry.get()) if numF_entry.get().strip() else None

                    cursor = conn.cursor()

                    if  goal_type or suggestions or suggestions_complete or numA or numB or numC or numF:
                        try: 
                            eval_insert_query = """
                                INSERT INTO evaluation (section_num, year, semester, course_num, goal_num, degree_name, degree_level, goal_type, suggestions, suggestions_complete, numA, numB, numC, numF) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                ON DUPLICATE KEY UPDATE
                                goal_type = VALUES(goal_type),
                                suggestions = VALUES(suggestions),
                                suggestions_complete = VALUES(suggestions_complete),
                                numA = VALUES(numA),
                                numB = VALUES(numB),
                                numC = VALUES(numC),
                                numF = VALUES(numF)
                            """
                            cursor.execute(eval_insert_query, (section_num, year, semester, course_num, goal_num, degree_name, degree_level, goal_type, suggestions, suggestions_complete, numA, numB, numC, numF))
                            conn.commit()
                            print("Evaluation added successfully!")
                            change_eval_window.destroy()
                        except mysql.connector.Error as e:
                            print(f"Error: {e}")
                    else:
                        print("Please fill in at least one evaluation criteria.")
        


        


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
    tk.Button(query_window, text="List Sections for a Degree", width=30,
              command=lambda: query_sections_by_degree(conn)).pack(pady=5)
    tk.Button(query_window, text="List Goals for a Degree", width=30,
              command=lambda: query_goals_by_degree(conn)).pack(pady=5)
    tk.Button(query_window, text="List Courses for each Goal", width=30,
              command=lambda: query_courses_by_goals(conn)).pack(pady=5)
    tk.Button(query_window, text="List Sections by Semesters", width=30,
              command=lambda: query_sections_by_semesters(conn)).pack(pady=5)
    tk.Button(query_window, text="List Sections by Instructor", width=30,
              command=lambda: query_sections_by_instructor(conn)).pack(pady=5)
    tk.Button(query_window, text="Incomplete Evaluations", width=30,
              command=lambda: query_incomplete_evaluations(conn)).pack(pady=5)
    tk.Button(query_window, text="F Percentage Query", width=30,
            command=lambda: query_pertcentage(conn)).pack(pady=5)

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
            print("Both degree name and level are required!")
            return

        cursor = conn.cursor()
        query = """
            SELECT * 
            FROM degree_courses
            WHERE degree_name = %s AND degree_level = %s
        """
        cursor.execute(query, (degree_name, degree_level))
        courses = cursor.fetchall()
        result_window = tk.Toplevel()
        result_window.title("Courses Result")
        if courses:
            tk.Label(result_window, text="Courses Associated with the Degree:").pack()
            print(courses)
            iteration = 0
            for course in courses:
                query1 = """
                            SELECT * 
                            FROM course
                            WHERE course_num = %s
                        """
                cursor.execute(query1, (course[2],))
                course_n = cursor.fetchall()
                print(f"Course name: {course_n}")
                tk.Label(result_window, text=f"{course_n[iteration][1]} {course[2]}: ").pack()
                iteration = iteration + 1
        else:
            tk.Label(result_window, text="No courses found for the specified degree.").pack()

    tk.Button(degree_window, text="Submit", command=execute_query).grid(row=2, column=1)


def query_sections_by_degree(conn):
    window = tk.Toplevel()
    window.title("Sections by Degree")

    tk.Label(window, text="Degree Name").grid(row=0, column=0)
    tk.Label(window, text="Degree Level").grid(row=1, column=0)
    tk.Label(window, text="Start Year").grid(row=2, column=0)
    tk.Label(window, text="End Year").grid(row=3, column=0)

    degree_name_entry = tk.Entry(window)
    degree_name_entry.grid(row=0, column=1)
    degree_level_entry = tk.Entry(window)
    degree_level_entry.grid(row=1, column=1)
    start_year_entry = tk.Entry(window)
    start_year_entry.grid(row=2, column=1)
    end_year_entry = tk.Entry(window)
    end_year_entry.grid(row=3, column=1)

    def execute_query():
        degree_name = degree_name_entry.get().strip()
        degree_level = degree_level_entry.get().strip()
        start_year = start_year_entry.get().strip()
        end_year = end_year_entry.get().strip()

        if not degree_name or not degree_level or not start_year or not end_year:
            print("All fields are required!")
            return

        try:
            # Ensure year inputs are integers
            start_year = int(start_year)
            end_year = int(end_year)

            cursor = conn.cursor()
            query = """
                SELECT s.course_num, s.section_num, s.year, s.semester, s.num_students, s.instructor_id
                FROM section s
                JOIN degree_courses dc ON s.course_num = dc.course_num
                WHERE dc.degree_name = %s AND dc.degree_level = %s
                  AND s.year BETWEEN %s AND %s
                ORDER BY s.year ASC, s.semester ASC
            """
            cursor.execute(query, (degree_name, degree_level, start_year, end_year))
            sections = cursor.fetchall()

            result_window = tk.Toplevel()
            result_window.title("Sections Result")

            if sections:
                tk.Label(result_window, text="Sections:").grid(row=0, column=0, columnspan=2)
                for idx, section in enumerate(sections, start=1):
                    text = f"Course: {section[0]}, Section: {section[1]}, Year: {section[2]}, Semester: {section[3]}, Students: {section[4]}, Instructor: {section[5]}"
                    tk.Label(result_window, text=text).grid(row=idx, column=0, columnspan=2)
            else:
                tk.Label(result_window, text="No sections found for the specified degree and time range.").grid(row=0, column=0, columnspan=2)

        except ValueError:
            print("Start year and end year must be valid integers!")
        except Exception as e:
            print(f"Error: {e}")

    tk.Button(window, text="Submit", command=execute_query).grid(row=4, column=1)

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
            print("Both degree name and level are required!")
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

def query_courses_by_goals(conn):
    window = tk.Toplevel()
    window.title("Courses by Goals")

    tk.Label(window, text="Degree Name").grid(row=0, column=0)
    tk.Label(window, text="Degree Level").grid(row=1, column=0)
    tk.Label(window, text="Goal Number").grid(row=2, column=0)

    degree_name_entry = tk.Entry(window)
    degree_name_entry.grid(row=0, column=1)
    degree_level_entry = tk.Entry(window)
    degree_level_entry.grid(row=1, column=1)
    goal_number_entry = tk.Entry(window)
    goal_number_entry.grid(row=2, column=1)

    def execute_query():
        degree_name = degree_name_entry.get().strip()
        degree_level = degree_level_entry.get().strip()
        goal_number = goal_number_entry.get().strip()

        if not degree_name or not degree_level or not goal_number:
            print("All fields are required!")
            return

        try:
            cursor = conn.cursor()
            query = """
                SELECT dc.course_num
                FROM degree_courses dc
                JOIN goal g ON dc.degree_name = g.degree_name AND dc.degree_level = g.degree_level
                WHERE g.degree_name = %s AND g.degree_level = %s AND g.goal_num = %s
                ORDER BY dc.course_num
            """

            cursor.execute(query, (degree_name, degree_level, goal_number))
            courses = cursor.fetchall()

            result_window = tk.Toplevel()
            result_window.title("Courses Result")

            if courses:
                tk.Label(result_window, text="Courses Associated with the Degree:").grid(row=0, column=0)
                for idx, course in enumerate(courses, start=1):
                    tk.Label(result_window, text=course[0]).grid(row=idx, column=0)
            else:
                tk.Label(result_window, text="No courses found for the specified degree.").grid(row=0, column=0)

        except Exception as e:
            print(f"Error: {e}")

    tk.Button(window, text="Submit", command=execute_query).grid(row=3, column=1)

def query_sections_by_semesters(conn):
    window = tk.Toplevel()
    window.title("Sections by Semesters")

    tk.Label(window, text="Course Number").grid(row=0, column=0)
    tk.Label(window, text="Start Semester").grid(row=1, column=0)
    tk.Label(window, text="End Semester").grid(row=2, column=0)
    tk.Label(window, text="Start Year").grid(row=3, column=0)
    tk.Label(window, text="End Year").grid(row=4, column=0)

    course_num = tk.Entry(window)
    course_num.grid(row=0, column=1)
    start_semester = tk.Entry(window)
    start_semester.grid(row=1, column=1)
    end_semester = tk.Entry(window)
    end_semester.grid(row=2, column=1)
    start_year = tk.Entry(window)
    start_year.grid(row=3, column=1)
    end_year = tk.Entry(window)
    end_year.grid(row=4, column=1)

    def execute_query():
        course = course_num.get().strip()
        start_sem = start_semester.get().strip()
        end_sem = end_semester.get().strip()
        start_yr = start_year.get().strip()
        end_yr = end_year.get().strip()

        if not (course and start_sem and end_sem and start_yr and end_yr):
            tk.Label(window, text="All fields are required!").grid(row=5, column=0, columnspan=2)
            return
        
        semester_order = {"spring": 1, "summer": 2, "fall": 3}

        try:
            # Convert years to integers
            start_yr = int(start_yr)
            end_yr = int(end_yr)
            start_sem_num = semester_order[start_sem.lower()]
            end_sem_num = semester_order[end_sem.lower()]

            # Construct the query
            query = """
                SELECT section_num, course_num, year, semester,
                       CASE semester.lower()
                           WHEN 'spring' THEN 1
                           WHEN 'summer' THEN 2
                           WHEN 'fall' THEN 3
                       END AS semester_order
                FROM section
                WHERE course_num = %s
                  AND year BETWEEN %s AND %s
                ORDER BY year, semester_order;
            """
        
            # Execute query
            cursor = conn.cursor()
            cursor.execute(query, (course, start_yr, end_yr))
            results = cursor.fetchall()

            end_results = []
            for result in results:
                sem_num = semester_order[result[3].lower()]
                if (result[2] == start_yr):
                    if sem_num >= start_sem_num:
                        end_results.append(result)

                elif (result[2] == end_yr):
                    if sem_num <= end_sem_num:
                        end_results.append(result)
                else:
                    end_results.append(result)
                
            # Display results
            if end_results:
                for idx, row in enumerate(end_results, start=6):
                    tk.Label(window, text=f'course num:{row[1]}, section num:{row[0]}, {row[2]} {row[3]}').grid(row=idx, column=0, columnspan=2)
            else:
                tk.Label(window, text="No sections found!").grid(row=6, column=0, columnspan=2)

        except Exception as e:
            tk.Label(window, text=f"Error: {e}").grid(row=5, column=0, columnspan=2)

    tk.Button(window, text="Submit", command=execute_query).grid(row=5, column=1)


def query_sections_by_instructor(conn):
    instructor_window = tk.Toplevel()
    instructor_window.title("Sections by Instructor")

    tk.Label(instructor_window, text="Instructor ID").grid(row=0, column=0)
    tk.Label(instructor_window, text="Start Semester").grid(row=1, column=0)
    tk.Label(instructor_window, text="End Semester").grid(row=2, column=0)
    tk.Label(instructor_window, text="Start Year").grid(row=3, column=0)
    tk.Label(instructor_window, text="End Year").grid(row=4, column=0)

    instructor_id_entry = tk.Entry(instructor_window)
    instructor_id_entry.grid(row=0, column=1)
    start_semester_entry = tk.Entry(instructor_window)
    start_semester_entry.grid(row=1, column=1)
    end_semester_entry = tk.Entry(instructor_window)
    end_semester_entry.grid(row=2, column=1)
    start_year_entry = tk.Entry(instructor_window)
    start_year_entry.grid(row=3, column=1)
    end_year_entry = tk.Entry(instructor_window)
    end_year_entry.grid(row=4, column=1)

    def execute_query():
        instructor_id = instructor_id_entry.get()
        start_semester = start_semester_entry.get()
        end_semester = end_semester_entry.get()
        start_year = start_year_entry.get()
        end_year = end_year_entry.get()

        if not instructor_id and start_semester and end_semester and start_year and end_year:
            tk.Label(instructor_window, text="All fields are required!").grid(row=5, column=0, columnspan=2)
            return

        semester_order = {"spring": 1, "summer": 2, "fall": 3}

        try:
            start_year = int(start_year)
            end_year = int(end_year)
            start_semester_num = semester_order[start_semester.lower()]
            end_semester_num = semester_order[end_semester.lower()]

            query = """
                WITH section_with_order AS (
                    SELECT course_num, section_num, year, semester,
                           CASE semester
                               WHEN 'spring' THEN 1
                               WHEN 'summer' THEN 2
                               WHEN 'fall' THEN 3
                           END AS semester_order
                    FROM section
                    WHERE instructor_id = %s
                )
                SELECT course_num, section_num, year, semester
                FROM section_with_order
                WHERE (year > %s OR (year = %s AND semester_order >= %s))
                    AND (year < %s OR (year = %s AND semester_order <= %s))
                ORDER BY year, semester_order;
            """
            cursor = conn.cursor()
            cursor.execute(query, (instructor_id, start_semester, end_semester, start_year, end_year))
            sections = cursor.fetchall()

            end_results = []
            for section in sections:
                semester_num = semester_order[section[3].lower()]
                if section[2] == start_year:
                    if semester_num >= start_semester_num:
                        end_results.append(section)

                elif section[2] == end_year:
                    if semester_num <= end_semester_num:
                        end_results.append(section)

                else:
                    end_results.append(section)

            result_window = tk.Toplevel()
            result_window.title("Sections Result")
            if end_results:
                tk.Label(result_window, text="Sections Taught by the Instructor:").pack()
                for section in end_results:
                    section_info = f"Course: {section[0]}, Section: {section[1]}, Year: {section[2]}, Semester: {section[3]}"
                    tk.Label(result_window, text=section_info).pack()
            else:
                tk.Label(result_window, text="No sections found for the specified criteria.").pack()

        except Exception as e:
            tk.Label(instructor_window, text=f"Error: {e}").grid(row=5, column=0, columnspan=2)

    tk.Button(instructor_window, text="Submit", command=execute_query).grid(row=6, column=1)

def query_incomplete_evaluations(conn):
    eval_window = tk.Toplevel()
    eval_window.title("Incomplete Evaluations")

    tk.Label(eval_window, text="Semester (e.g., Spring 2024)").grid(row=0, column=0)
    semester_entry = tk.Entry(eval_window)
    semester_entry.grid(row=0, column=1)

    def execute_query():
        semester = semester_entry.get()
        if not semester:
            print("Semester is required!")
            return

        cursor = conn.cursor()
        query = """
            SELECT course_num, section_num, suggestions
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

        query2 = """
            SELECT course_num, section_num, suggestions, suggestions_complete
            FROM evaluation
            WHERE semester = %s
        """

        cursor.execute(query2, (semester,))
        results2 = cursor.fetchall()

        tk.Label(result_window, text="Suggestion Paragraph Progress:").pack()
        for result in results2:
            if result[3]:
                tk.Label(result_window, text=f"Course {result[0]}, Section: {result[1]} is complete.").pack()
            elif not result[3] and len(result[2]) > 0:
                tk.Label(result_window, text=f"Course {result[0]}, Section: {result[1]} is partially complete.").pack()
            elif not result[3] and len(result[2]) == 0:
                tk.Label(result_window, text=f"Course {result[0]}, Section: {result[1]} is not complete, no information added.").pack()

    tk.Button(eval_window, text="Submit", command=execute_query).grid(row=1, column=1)


def query_pertcentage(conn):
    window = tk.Toplevel()
    window.title("Sections Where F's Percentage Not Reached")

    tk.Label(window, text="F percentage (enter as decimal between 0 and 1)").grid(row=0, column=0)
    tk.Label(window, text="Semester").grid(row=1, column=0)
    tk.Label(window, text="Year").grid(row=2, column=0)


    percentage_entry = tk.Entry(window)
    percentage_entry.grid(row=0, column=1)
    semester_entry = tk.Entry(window)
    semester_entry.grid(row=1, column=1)
    year_entry = tk.Entry(window)
    year_entry.grid(row=2, column=1)

    def execute_query():
        cursor = conn.cursor()
        percentage = percentage_entry.get()
        percentage = float(percentage)
        semester = semester_entry.get().strip().lower()
        year = year_entry.get()
        year = int(year)

        if not percentage or not semester or not year:
            tk.Label(window, text = 'All fields are required!').grid(row = 4, column = 1)
        elif (percentage <= 0 or percentage >= 1):
            tk.Label(window, text = 'Enter the percentage as a decimal between 0 and 1 (ex: enter .20 instead of 20%)').grid(row = 4, column = 1)
        else:
            get_sections_query = """
            SELECT * 
            FROM evaluation
            WHERE semester = %s
            AND year = %s
            """

            cursor.execute(get_sections_query, (semester, year))
            sections_info = cursor.fetchall()
            section_results = []
            for sections in sections_info:
                if sections[10] and sections[11] and sections[12] and sections[13]:
                    temp_total = sections[10]+sections[11]+sections[12]+sections[13]
                    get_percentage = float(sections[13])/float(temp_total)
                    #10-13
                    if get_percentage <= percentage:
                        section_results.append([sections, get_percentage])
                else:
                    tk.Label(window, text = 'All grade counts are not entered! Cannot find F percentage. Please complete evaluation!').grid(row = 4, column = 1)

            result_window = tk.Toplevel()
            result_window.title("Percentage Query Results")
            if section_results:
                for result in section_results:
                    section_info = f"Section num: {result[0][0]}, Course num: {result[0][3]}, Percentage of students that got an F: {result[1]*100:.1f}%"
                    tk.Label(result_window, text=section_info).pack()
            else:
                tk.Label(result_window, text="No sections found for the specified criteria.").pack()

    tk.Button(window, text="Submit", command=execute_query).grid(row=5, column=1)


                
        

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
