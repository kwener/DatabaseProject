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
                name VARCHAR(100) NOT NULL,
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
            instructor_id int,
            PRIMARY KEY(course_num, section_num, year, semester)
            FOREIGN KEY (course_num) REFERENCES course(course_num) ON DELETE CASCADE,
            FOREIGN KEY (instructor_id) REFERENCES instructor(instructor_id) ON DELETE CASCADE,
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
                PRIMARY KEY(course_num, degree_name, degree_level)
                FOREIGN KEY (course_num) REFERENCES course(course_num) ON DELETE CASCADE,
                FOREIGN KEY (degree_name) REFERENCES degree(degree_name) ON DELETE CASCADE,
                FOREIGN KEY (degree_level) REFERENCES degree(degree_level) ON DELETE CASCADE,
            );
            """
    cursor.execute(create_degree_courses)

#each goal is assoiciated with a degree, each goal_num is unique to the degree 
#different degrees can have same goal_num

#how do i do delete on cascade if the combo is deleted?
    create_goal = """
            CREATE TABLE IF NOT EXISTS degree (
                goal_num CHAR(4),
                degree_name VARCHAR(200),
                degree_level VARCHAR(200),
                description VARCHAR, 
                PRIMARY KEY(goal_num, degree_name, degree_level)
                FOREIGN KEY (degree_name) REFERENCES degree(degree_name) ON DELETE CASCADE,
                FOREIGN KEY (degree_level) REFERENCES degree(degree_level) ON DELETE CASCADE,
            );
            """
    cursor.execute(create_goal)


    create_evaluation = """
            CREATE TABLE IF NOT EXISTS degree (
                section_num INT,
                course_num VARCHAR(10),
                goal_num CHAR(4),
                degree_name VARCHAR(200),
                degree_level VARCHAR(200),
                goal_type VARCHAR(200),
                suggestions VARCHAR,
                numA int,
                numB int,
                numC int,
                numF int,
                PRIMARY KEY(goal_num, degree_name, degree_level, section_num, course_num)
                FOREIGN KEY (degree_name, degree level) 
                    REFERENCES degree(degree_name, degree_level) ON DELETE CASCADE,
                FOREIGN KEY (goal_num) REFERENCES goal(goal_num) ON DELETE CASCADE,
                FOREIGN KEY (section_num, course_num) 
                    REFERENCES section(section_num, course_num) ON DELETE CASCADE
            );
            """
    cursor.execute(create_evaluation)

    #maybe make a table for course degree relationship?

def data_entry_window(cursor):
    data_entry_window = tk.Toplevel()  # Create a new top-level window
    data_entry_window.title("Data Entry Choices")
    
    # Add buttons for each data type
    tk.Button(data_entry_window, text="Enter Degree", command=lambda: enter_degree(data_entry_window, cursor)).pack(pady=10)
    tk.Button(data_entry_window, text="Enter Course", command=lambda: enter_course(data_entry_window)).pack(pady=10)
    tk.Button(data_entry_window, text="Enter Instructor", command=lambda: enter_instructor(data_entry_window)).pack(pady=10)
    tk.Button(data_entry_window, text="Enter Section", command=lambda: enter_section(data_entry_window)).pack(pady=10)
    tk.Button(data_entry_window, text="Enter Evaluation", command=lambda: enter_evaluation(data_entry_window)).pack(pady=10)


def enter_degree(data_entry_window, cursor):
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

    submit_button = tk.Button(degree_window, text="Submit", command=lambda: submit_degree(cursor))
    submit_button.grid(row=2, column=1, pady=10)
     
    def submit_degree(cursor):
        degree_name = deg_name.get()
        degree_level = deg_level.get()

        if degree_name and degree_level:
            try: 
                deg_insert_query = "INSERT INTO degree (degree_name, degree_level) VALUES (%s, %s)"
                cursor.execute(deg_insert_query, (degree_name, degree_level))
                print("Degree added successfully!")
                degree_window.destroy()
            except mysql.connector.Error as e:
                print(f"Error: {e}")
        else:
            print("Please fill in both degree name and degree level.")

        submit_button = tk.Button(degree_window, text="Submit", command=lambda: submit_degree(cursor))
        submit_button.grid(row=2, column=1, pady=10)



def enter_course(data_entry_window):
    return

def enter_instructor(data_entry_window):
    return

def enter_section(data_entry_window):
    return

def enter_evaluation(data_entry_window):
    return



#https://www.geeksforgeeks.org/python-gui-tkinter/
def main_menu(conn):
    mycursor = conn.cursor()
    def open_data_entry():
        data_entry_window(mycursor)

    def open_query_menu():
        query_window()

    root = tk.Tk()
    root.title("Academic Database Manager")
    root.geometry("400x300")

    tk.Label(root, text="Main Menu", font=("Arial", 16)).pack(pady=20)

    tk.Button(root, text="Data Entry", width=20, command=open_data_entry).pack(pady=10)
    tk.Button(root, text="Query Menu", width=20, command=open_query_menu).pack(pady=10)

    root.mainloop()


conn = connect_to_database()
load_config()

main_menu(conn)

def main():
    conn = connect_to_database()
    create_tables(conn)
    main_menu(conn)


