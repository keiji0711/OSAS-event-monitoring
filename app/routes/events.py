from flask import Blueprint, render_template, Response, request, redirect, current_app, flash, url_for
import mysql.connector
from datetime import datetime
import pytz

bp = Blueprint('adminEvents', __name__, template_folder='templates')


now = datetime.now()

@bp.route('/events')
def events():

    conn = mysql.connector.connect(
        host='localhost',  
        user='root',  
        password='', 
        database='OSAS_event_management'
    )
    try:
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM events where status = 'active'")
        Events = cursor.fetchall()
    
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        Events = []
        flash("Failed to retrieve events from the database.", "danger")
    
    finally:
        if cursor:
            cursor.close()

    return render_template('events.html', Events=Events)

@bp.route('/addEvents', methods=['GET', 'POST'])
def addEvents():
    if request.method == 'POST':
        eventName = request.form['eventName']
        date = request.form['date']
        eventTime = request.form['time']
        schoolYear = request.form['schoolYear']
        semester = request.form['semester']

        try:
            conn = current_app.mysql
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO events (event_name, event_date, event_time, schoolYear, Semester, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """, (eventName, date, eventTime, schoolYear, semester, 'Active'))

            conn.commit()
            flash("Event added successfully!", "success")

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            flash("An error occurred while adding the event.", "danger")
        
        finally:
            if cursor:
                cursor.close()

        return redirect('/events')  

    return render_template('addEvents.html')


@bp.route('/admin/events/edit', methods=['POST'])
def editEvent():
    event_id = request.form['eventId']
    name = request.form['eventName']
    date = request.form['date']
    time = request.form['time']
    school_year = request.form['schoolYear']
    semester = request.form['semester']
    
    try:
        conn = current_app.mysql
        cursor = conn.cursor()

       
        cursor.execute("""UPDATE events 
                          SET event_name=%s, event_date=%s, event_time=%s, schoolYear=%s, Semester=%s 
                          WHERE event_id=%s""", 
                       (name, date, time, school_year, semester, event_id))
        conn.commit()
        flash('Event updated successfully!', 'success')
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flash("Failed to update the event.", "danger")
    finally:
        if cursor:
            cursor.close()
    
    return redirect(url_for('adminEvents.events'))


@bp.route('/eventAttendance')
def eventAttendance():
    
    event_name = request.args.get('event_name')
    eventid = request.args.get('event_id')

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
    AND events.event_id = %s;""",(eventid,))
    event = cursor.fetchall()
    cursor.close()

    
    
    return render_template('eventAttendance.html', event_name=event_name, event_id = eventid,event = event )


@bp.route('/scanBarcode', methods=['POST'])
def scanBarcode():
    barcode = request.json.get('barcode')
    action = request.json.get('action')  
    event_id = request.json.get('event_id')  

    ph_tz = pytz.timezone('Asia/Manila')
    now = datetime.now(ph_tz) 
    

    print(action)
    print(event_id)
    print(barcode)
    
    if not barcode:
        return {"status": "error", "message": "No barcode provided."}, 400

    if not action or action not in ['Time-In', 'Time-Out']:
        return {"status": "error", "message": "Invalid or missing action."}, 400

    conn = None
    cursor = None

    try:
        conn = mysql.connector.connect(
            host='localhost',  
            user='root',  
            password='', 
            database='OSAS_event_management' 
        )
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT 
                CONCAT(l_name, ', ', f_name, ' ', m_name) AS full_name, 
                department 
            FROM 
                students 
            WHERE 
                TRIM(student_id) = TRIM(%s)
            """, 
            (barcode.strip(),)
        )
        student = cursor.fetchone()

        if not student:
            return {"status": "error", "message": "This USN is not registered."}, 404

        full_name, department = student

        if str(action) == 'Time-In':
            time_in = now.strftime("%I:%M:%S %p")
            cursor.execute(
                """
                SELECT 1 FROM attendance 
                WHERE TRIM(student_id) = TRIM(%s) AND event_id = %s 
                LIMIT 1
                """, 
                (barcode.strip(), event_id)
            )
            existing_time_in = cursor.fetchone()

            if existing_time_in:
                return {
                    "status": "error",
                    "message": "This student has already timed in for this event."
                }, 400

            cursor.execute(
                """
                INSERT INTO attendance (student_id, event_id, time_in, time_out, created_at)
                VALUES (%s,%s,%s, '', NOW())
                """, 
                (barcode.strip(), event_id, time_in)
            )
            conn.commit()
            message = f"Time-In recorded for {full_name} in {department}."

        elif str(action) == 'Time-Out':
            time_out = now.strftime("%I:%M:%S %p")
            cursor.execute(
                """
                SELECT 1 FROM attendance 
                WHERE TRIM(student_id) = TRIM(%s) AND event_id = %s AND time_out != '' 
                LIMIT 1
                """, 
                (barcode.strip(), event_id)
            )
            existing_time_out = cursor.fetchone()

            if existing_time_out:
                return {
                    "status": "error",
                    "message": "This student has already timed out for this event."
                }, 400

        
            cursor.execute(
                """
                UPDATE attendance 
                SET time_out = %s 
                WHERE TRIM(student_id) = TRIM(%s) AND event_id = %s AND time_out = ''
                LIMIT 1
                """, 
                (time_out, barcode.strip(), event_id)
            )
            if cursor.rowcount == 0:  
                return {
                    "status": "error",
                    "message": "No matching Time-In record found for Time-Out."
                }, 400
            conn.commit()
            message = f"Time-Out recorded for {full_name} in {department}."

    
        return {
            "status": "success",
            "message": message,
            "full_name": full_name,
            "department": department
        }, 200

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return {"status": "error", "message": "Database error occurred."}, 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()







