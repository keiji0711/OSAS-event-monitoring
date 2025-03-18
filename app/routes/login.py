from flask import Blueprint,render_template,redirect,request
import mysql.connector
import hashlib

bp = Blueprint('login', __name__, template_folder='templates')



def enc_pass(password):
    hashed = hashlib.sha256(password.encode()).hexdigest()
    return hashed


@bp.route('/')
def login():

    return render_template('login.html')

@bp.route('/register', methods = ['POST', 'GET'])
def register():

    conn = mysql.connector.connect(
            host='localhost',  
            user='root',  
            password='', 
            database='OSAS_event_management' 
        )

    if request.method == 'POST':

        Username = request.form['username']
        pw1 = request.form['password']
        pw2 = request.form['confirm-pass']


        try:
            if pw1 == pw2:
                cursor = conn.cursor()
                cursor.execute('insert into acounts(username,password) Values(%s,%s)',(Username,enc_pass(pw2)))
                conn.commit()

                return redirect('/')

            else:
                return "Error inserting"


        except mysql.connector.Error as e:
            print("Database Error:", e)  # Debugging line
            return {"status": "error", "message": str(e)}, 500

        
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

            

    return render_template('register.html')