from flask import Flask, render_template, request, session, redirect, url_for, Blueprint, abort
from flask_sqlalchemy import SQLAlchemy
import json
from flask_mail import Mail
import mysql.connector as mysqldb
import datetime

# CONFIG.JSON

with open('config.json', 'r') as cj:
    params = json.load(cj)["params"]

app = Flask(__name__, static_folder="static")

# SET SECRET KEY
app.secret_key = 'meditransit'

# INITIALIZE MAIL

app.config.update(
    MAIL_SERVER = params['smtp_server'],
    MAIL_PORT = params['smtp_port'],
    MAIL_USE_SSL = params['smtp_ssl'],
    MAIL_USERNAME = params['smtp_username'],
    MAIL_PASSWORD = params['smtp_password']
    )
mail = Mail(app)
# INITIALIZE DATABASE
conn = mysqldb.connect(host='localhost', user='root', password='Creative#123', db='flask')
cur = conn.cursor(buffered=False, dictionary=True)

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')
@dashboard_bp.route("/", methods=['GET','POST'])
def dashboard():
    queryemail = ""
    querymobile = ""
    querypassword = ""
    if ('user' in session and session['user'] != None):
        try:
            conn.connect()
            cur.execute(f"""
                        SELECT * FROM users WHERE EMAIL = "{session['user']}" or MOBILE = "{session['user']}"
                        """)
            result = cur.fetchall()
            for row in result:
                queryusername = row['NAME']
                queryemail = row['EMAIL']
                querymobile = row['MOBILE']
                querypassword = row['PASSWORD']
            cur.execute(f"""
                        SELECT COUNT(*) AS 'NUMBOOKINGS', MAX(BOOKING_DATETIME) AS 'LASTBOOKING' FROM bookings WHERE MOBILE = "{querymobile}"
                        """)
            bookings = cur.fetchall()
            for booking in bookings:
                numbookings = booking['NUMBOOKINGS']
                lastbooking = booking['LASTBOOKING']
            cur.execute(f"SELECT COUNT(*) AS 'NUMCONTACTS' FROM contact")
            contacts = cur.fetchall()
            for contact in contacts:
                numcontacts = contact['NUMCONTACTS']
        except:
            numbookings = None
            numcontacts = None
            lastbooking = None
        finally:
            conn.close()
            return render_template('index.html', loginid=queryusername, title="DASHBOARD", total_bookings=numbookings, last_booking=lastbooking, total_contacts = numcontacts)
    else:
        pass
    if (request.method == 'POST'):
        loginid = request.form.get('loginid')
        password = request.form.get('password')
        try:
            conn.connect()
            cur.execute(f"""
                        SELECT * FROM users WHERE EMAIL = "{loginid}" or MOBILE = "{loginid}"
                        """)
            result = cur.fetchall()
            for row in result:
                queryusername = row['NAME']
                queryemail = row['EMAIL']
                querymobile = row['MOBILE']
                querypassword = row['PASSWORD']
            cur.execute(f"""
                        SELECT COUNT(*) AS 'NUMBOOKINGS', MAX(BOOKING_DATETIME) AS 'LASTBOOKING' FROM bookings WHERE MOBILE = "{querymobile}"
                        """)
            bookings = cur.fetchall()
            for booking in bookings:
                numbookings = booking['NUMBOOKINGS']
                lastbooking = booking['LASTBOOKING']
            cur.execute(f"SELECT COUNT(*) AS 'NUMCONTACTS' FROM contact")
            contacts = cur.fetchall()
            for contact in contacts:
                numcontacts = contact['NUMCONTACTS']
        except:
            numbookings = None
            numcontacts = None
            lastbooking = None
        finally:
            conn.close()
        if (loginid == queryemail or loginid == querymobile) and password == querypassword:
            session['user'] = querymobile
            return render_template('index.html', loginid=queryusername, title="DASHBOARD", total_bookings = numbookings, last_booking=lastbooking, total_contacts=numcontacts)
        else:
           return redirect(url_for("login"))
    else:
        return redirect(url_for("login"))

@dashboard_bp.route("/booknow", methods=['GET', 'POST'])
def booknow():
    if ('user' in session) and (session['user'] != None) and (request.method == 'POST'):
        conn.connect()
        cur.execute(f"""
                    SELECT * FROM users WHERE MOBILE = "{session['user']}"
                    """)
        userinfo = cur.fetchall()
        for info in userinfo:
            f_username = info['NAME']
            f_mobile  = info['MOBILE']
            f_email = info['EMAIL']
        patientname = request.form.get('patientname')
        address = request.form.get('address')
        gender = request.form.get('gender')
        age = request.form.get('age')
        try:
            conn.connect()
            cur.execute(f"""INSERT INTO bookings (MOBILE, PATIENT, ADDRESS, GENDER, AGE, BOOKING_DATETIME) VALUES ("{f_mobile}", "{patientname}", "{address}", "{gender}", "{age}", "{datetime.datetime.now()}")""")
            conn.commit()
            return render_template("booknow.html", loginid=f_username, title="BOOKING SUCCESSFUL", msgclass="alert alert-primary", showform="hidden", msg=f"Ambulance is on its way. ETA: 15:32 PM", flashmsg="", imgheight="200")
        except Exception as e:
            return render_template("booknow.html", loginid=f_username, title="BOOK", msgclass="alert alert-danger", showform="", msg=f"Error in booking ambulance. Please try again", flashmsg="", imgheight="0")
        finally:
            conn.close()
    elif ('user' in session) and (session['user'] != None):
            try:
                conn.connect()
                cur.execute(f"""
                            SELECT * FROM users WHERE MOBILE = "{session['user']}"
                            """)
                userinfo = cur.fetchall()
                for info in userinfo:
                    f_username = info['NAME']
                    f_email = info['EMAIL']
                    f_mobile = info['MOBILE']
            except:
                return render_template("booknow.html", loginid=f_username,  title="BOOK", showform="", flashmsg="", imgheight=0, msgclass="alert alert-danger", msg="Can't fetch Contact Information")
            return render_template("booknow.html", loginid=f_username, title="BOOK", showform="", flashmsg="hidden", imgheight="0", cperson=f_username, mobile=f_mobile, email=f_email, cd_readonly="readonly")
    else:
        return redirect(url_for("login"))
    
@app.route('/', methods=['GET', 'POST'])
def index():
    return redirect(url_for("login"))

@app.route("/error")
def error():
    abort(404)

@app.route("/booknow", methods= ['GET', 'POST'])
def instantbook():
    return render_template("instantbook.html")

@app.route("/signup", methods = ['GET', 'POST'])
def signup():
    if (request.method == 'POST'):
        username = request.form.get('name')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        password = request.form.get('password')
        try:
            conn.connect()
            cur.execute(f"""INSERT INTO users (NAME, EMAIL, MOBILE, PASSWORD) VALUES ("{username}","{email}","{mobile}", "{password}")""")
            conn.commit()
            '''try:
                mail.send_message(f'New Message from Flask - {name}',
                sender=params['smtp_username'],
                    recipients = [email],
                    body = f"{name}\n{email}\n{mobile}"
                )
            except:
                pass'''
            session['user'] = mobile
            return redirect(url_for("dashboard.dashboard"))
        except Exception as e:
            return render_template('pages-register.html', showerror="")
        finally:
            conn.close()
    return render_template('pages-register.html', showerror="hidden")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if ('user' in session and session['user'] != None):
        return redirect(url_for("dashboard.dashboard"))
    else:
        return render_template("pages-login.html")

@app.route("/logout", methods=['GET', 'POST'])
def logout():
    if request.method=='POST':
        session['user'] = None
        return redirect(url_for("login"))
    
# Error Handlers

@app.errorhandler(404)
def not_found_error(error):
    return render_template("pages-error-404.html")

app.register_blueprint(dashboard_bp)
app.run(use_reloader=True,debug=True, host='192.168.1.2')