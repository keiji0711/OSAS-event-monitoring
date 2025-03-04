from flask import Blueprint, render_template,current_app
import mysql.connector
import math

bp = Blueprint('adminDashboard', __name__, template_folder='templates')

@bp.route('/adminDashboard')
def adminDashboard():
    
    conn = mysql.connector.connect(
        host='localhost',  
        user='root',  
        password='', 
        database='OSAS_event_management' 
    )
    cursor = conn.cursor()

  
    cursor.execute('SELECT COUNT(*) FROM students;')
    attendee = cursor.fetchone()[0]  

    cursor.execute('SELECT COUNT(*) FROM events;')
    events = cursor.fetchone()[0]  

    cursor.execute('SELECT COUNT(*) FROM attendance;')
    attendance = cursor.fetchone()[0]  

    cursor.execute("""SELECT events.event_name, events.event_date, COUNT(attendance.attendance_id) AS attendance_count, 
       events.SchoolYear, events.Semester, events.status 
FROM events
LEFT JOIN attendance ON events.event_id = attendance.event_id
WHERE events.status = 'active' 
GROUP BY events.event_id;
""")
    
    eventsRec = cursor.fetchall()

    

    if attendance == 0 or events == 0: 
        final_rate = 0
    else:
        attendance_rate = attendee * events
        attendees = attendance / attendance_rate
        final_rate = math.ceil(attendees * 1000) / 10

 
    cursor.close()
    conn.close()

    
    return render_template('adminDashbaord.html', attendee = attendee, events = events, final_rate = final_rate, eventsRec = eventsRec)