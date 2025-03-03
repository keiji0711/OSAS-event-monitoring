from flask import Blueprint, render_template, request, jsonify
import mysql.connector

bp = Blueprint('reports', __name__, template_folder='templates')

conn = mysql.connector.connect(
            host='localhost',  
            user='root',  
            password='', 
            database='OSAS_event_management' 
        )


@bp.route('/studRec')
def studRec():

    conn = mysql.connector.connect(
            host='localhost',  
            user='root',  
            password='', 
            database='OSAS_event_management' 
        )
    stud_id = request.args.get('student_id')
    print(stud_id)

    
    cursor = conn.cursor()
    cursor.execute("""SELECT CONCAT(students.l_name, ' ', students.f_name, ' ', students.m_name) as full_name, students.student_id,students.department,students.phone_number 
FROM students WHERE student_id = %s""",(stud_id,))
    student = cursor.fetchone()
    
    cursor.execute("""SELECT DISTINCT events.event_name, attendance.time_in  
FROM attendance  
JOIN events ON attendance.event_id = events.event_id  
JOIN students ON attendance.student_id = students.student_id  
WHERE students.student_id = %s
""",(stud_id,))
    
    attendedEvents = cursor.fetchall()
    print(attendedEvents)

    cursor.execute("SELECT event_name from events; ")
    allEvents = cursor.fetchall()
    print(allEvents)

    attended = [events[0] for events in attendedEvents]
    overall = [item[0] for item in allEvents]

    missed = list(set(overall) - set(attended))
    print(missed)



    return render_template('stud_record.html', student = student, attendedEvents = attendedEvents, missed = missed)




@bp.route('/studList')
def studList():
    
    cursor = conn.cursor()
    cursor.execute("""SELECT CONCAT(students.l_name, ' ', students.f_name, ' ', students.m_name) as 
                   full_name, students.student_id, students.department, 
                   students.phone_number FROM students""")
    studentList = cursor.fetchall()
    cursor.close()
    return render_template('stud_list.html', studentList=studentList)

@bp.route('/searchStudents')
def searchStudents():
    query = request.args.get('query', '')
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT CONCAT(students.l_name, ' ', students.f_name, ' ', students.m_name) as full_name,
               students.student_id, students.department, students.phone_number 
        FROM students 
        WHERE students.f_name LIKE %s OR students.l_name LIKE %s OR students.student_id LIKE %s
    """, ('%' + query + '%', '%' + query + '%', '%' + query + '%'))
    
    students = cursor.fetchall()
    cursor.close()

    student_data = [
        {
            'name': student[0],
            'student_number': student[1],
            'department': student[2],
            'contacts': student[3]
        }
        for student in students
    ]
    
    return jsonify(student_data)


@bp.route('/archeivedEvents')
def archeivedEvents():
    return render_template('archeived_events.html')


@bp.route('/event_stat')
def event_stat():
    return render_template('event_stat.html')
