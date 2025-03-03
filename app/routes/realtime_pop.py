from flask import Blueprint,jsonify,current_app
import mysql.connector

bp = Blueprint('realtimePop', __name__, template_folder='templates')

@bp.route('/fetchAttendanceLogs/<int:event_id>', methods=['GET'])
def fetch_attendance_logs(event_id):
    conn = mysql.connector.connect(
            host='localhost',  
            user='root',  
            password='', 
            database='OSAS_event_management' 
        )
    cursor = conn.cursor()
    cursor.execute("""SELECT 
    CONCAT(students.l_name, ' ', students.f_name, ' ', COALESCE(students.m_name, '')) AS full_name, 
    students.department,
    events.event_date,
    attendance.time_in, 
    attendance.time_out
FROM 
    students, attendance, events
WHERE 
    students.student_id = attendance.student_id
    AND attendance.event_id = events.event_id
    AND events.event_id = %s;""",(event_id,))
    logs = cursor.fetchall()
    cursor.close()

    logs_list = [
        {
            "name": log[0],
            "department": log[1],
            "date": log[2],
            "time_in": log[3],
            "time_out": log[4],
        }
        for log in logs
    ]
    
    return jsonify(logs_list)
