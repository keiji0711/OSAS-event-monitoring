from flask import Blueprint,jsonify,current_app, request
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

@bp.route('/archived_event/<int:event_id>', methods=['POST'])
def archived_event(event_id):
    conn = mysql.connector.connect(
        host='localhost',  
        user='root',  
        password='', 
        database='OSAS_event_management'
    )
    cursor = conn.cursor()

    print(event_id)

    try:
        cursor.execute("UPDATE events SET status = 'archived' WHERE event_id = %s", (event_id,))
        conn.commit()  
        return jsonify({'message': 'Event archived successfully'}), 200
    except mysql.connector.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()







