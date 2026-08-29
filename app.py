from config import Config, EmailTemplates
import mysql.connector as sql
import random
import os
import smtplib
from email.message import EmailMessage
from flask import Flask,render_template,url_for,request,redirect,session
import bcrypt
from itsdangerous import URLSafeTimedSerializer,BadSignature,TimedSerializer

app=Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
serializer=URLSafeTimedSerializer(app.secret_key)

DBConfig=Config()

from_email=DBConfig.from_email
email_app_password=DBConfig.email_app_password


def getConnectionWithDB():
    db_host=DBConfig.db_host
    db_port=DBConfig.db_port
    db_user=DBConfig.db_user
    db_password=DBConfig.db_password
    db_name=DBConfig.db_name

    try:
        connection=sql.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name
        )
        return connection
    except:
        return 'Connection Failed'


def insertUserRecord(user_data):
    name=user_data['name']
    email=user_data['email']
    password_hash=user_data['password_hash']
    connection=getConnectionWithDB()
    if connection=='Connection Failed':
        return False
    else:
        try:
            cursor=connection.cursor()
            cursor.execute("INSERT INTO users(name,email,password_hash) VALUES(%s,%s,%s)",(name,email,password_hash))
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except:
            print("Data can't be inserted !!")
            return False


def readUserRecords():
    connection=getConnectionWithDB()
    if connection=='Connection Failed':
        return False
    else:
        cursor=connection.cursor()
        cursor.execute("SELECT * FROM USERS")
        data=cursor.fetchall()      # data if iterator object
        records=[]
        for record in data:
            temp={}
            temp['id']=record[0]
            temp['name']=record[1]
            temp['email']=record[2]
            temp['password_hash']=record[3]
            temp['is_verified']=record[4]
            temp['created_at']=record[5]
            records.append(temp)
        cursor.close()
        connection.close()
        return records


def readUserRecordByEmail(user_data):
    email=user_data['email']
    connection=getConnectionWithDB()
    if connection=='Connection Failed':
        return False
    else:
        cursor=connection.cursor()
        cursor.execute("SELECT * FROM USERS where email =%s",(email,))
        data=cursor.fetchone()      
        try:
            record = {
                'id': data[0],
                'name': data[1],
                'email': data[2],
                'password_hash': data[3],
                'is_verified': data[4],
                'created_at': data[5]
            }
            cursor.close()
            connection.close()
            return record
        except:
            cursor.close()
            connection.close()
            return 'No record'


def readUserRecordById(user_data):
    id=user_data['id']
    connection=getConnectionWithDB()
    if connection=='Connection Failed':
        return False
    else:
        cursor=connection.cursor()
        cursor.execute("SELECT * FROM USERS where id =%s",(id,))
        data=cursor.fetchone()      
        try:
            record = {
                'id': data[0],
                'name': data[1],
                'email': data[2],
                'password_hash': data[3],
                'is_verified': data[4],
                'created_at': data[5]
                }
            cursor.close()
            connection.close()
            return record
        except:
            cursor.close()
            connection.close()
            return 'No record founded'


def updateNameByIdorEmail(user_data):
    query_filter=''
    try:
        id=user_data['id']
        query_filter='id'
    except:
        email=user_data['email']
        query_filter='email'
    new_name=user_data['new_name']
    connection=getConnectionWithDB()
    if connection=='Connection Failed':
        return False
    else:
        cursor=connection.cursor()
        if query_filter=='id':
            query="UPDATE users SET name= %s WHERE id=%s"
            values=(new_name,id)
        elif query_filter=="email":
            query="UPDATE users SET name= %s WHERE email=%s"
            values=(new_name,email)
        cursor.execute(query,values)
        connection.commit()
        cursor.close()
        connection.close()
        return True


def updatePasswordByIdorEmail(user_data):
    query_filter=''
    try:
        id=user_data['id']
        query_filter='id'
    except:
        email=user_data['email']
        query_filter='email'
    new_password=user_data['new_password']
    connection=getConnectionWithDB()
    if connection=='Connection Failed':
        return False
    else:
        cursor=connection.cursor()
        if query_filter=='id':
            query="UPDATE users SET password_hash= %s WHERE id=%s"
            values=(new_password,id)
        elif query_filter=="email":
            query="UPDATE users SET password_hash= %s WHERE email=%s"
            values=(new_password,email)
        cursor.execute(query,values)
        connection.commit()
        cursor.close()
        connection.close()
        return True


def updateIsverifiedByIdorEmail(user_data):
    query_filter=''
    try:
        id=user_data['id']
        query_filter='id'
    except:
        email=user_data['email']
        query_filter='email'
    is_verified=user_data['is_verified']
    connection=getConnectionWithDB()
    if connection=='Connection Failed':
        return False
    else:
        cursor=connection.cursor()
        if query_filter=='id':
            query="UPDATE users SET is_verified= %s WHERE id=%s"
            values=(is_verified,id)
        elif query_filter=="email":
            query="UPDATE users SET is_verified= %s WHERE email=%s"
            values=(is_verified,email)
        cursor.execute(query,values)
        connection.commit()
        cursor.close()
        connection.close()
        return True


def generateOTP():
    otp=random.randint(1000,9999)
    return otp


def sendOTPviaEmail(to_email,otp):
    message = EmailMessage()
    message['Subject'] = 'OTP Notification'
    message['From'] = from_email
    message['To'] = to_email
    message.set_content(
        f"Your OTP is {otp}"
    )
    with smtplib.SMTP("smtp.gmail.com",587) as server:   # here with operater does is: whaterver obj is creaetd within the block the object destroys automatically 
        server.starttls()
        server.login(from_email,email_app_password)
        server.send_message(message)
    return True


def validateDataForRegister(user_data):
    errors=[]
    name=user_data['name']
    email=user_data['email']
    password=user_data['password']
    confirm_password=user_data['confirm_password']
    if name is None or len(name)<2:
            errors.append('Invalid Name')
    if email is None or len(email)<5:
        errors.append('Invalid Email')
    if password is None or len(password)<5:
            errors.append('Invalid Password')
    if confirm_password is None or len(confirm_password)<5:
        errors.append('Invalid Confirm Password')
    if password!=confirm_password:
        errors.append('Passwords not matched')
    return errors


def verifyDuplicateEmail(user_data):
    record=readUserRecordByEmail(user_data)
    if (record=='No record'):
        return False # no duplicate
    else:
        return True # duplicate found
    

#encode - str to bytes
#decode - bytes to str
#gensalt is used to generate a key
#how many times this key should iterate - gensalt(4) 4 times
#cipher_text is the return value of hashpw 
def generateHash(text):
    btext=text.encode('utf-8')
    cipher_text=bcrypt.hashpw(btext,bcrypt.gensalt(4))
    return cipher_text.decode('utf-8')
    print(cipher_text,len(cipher_text))


#rest password token generation
def resetPasswordTokenGenerate(email):
    token = serializer.dumps(
        email,
        salt="reset-password"
    )
    return token


def SendEmail(subject,to_email,body):
    message = EmailMessage()

    message['Subject'] = subject
    message['From'] = from_email
    message['To'] = to_email
    message.set_content(body)
    with smtplib.SMTP("smtp.gmail.com",587) as server:   # here with operater does is: whaterver obj is creaetd within the block the object destroys automatically 
        server.starttls()
        server.login(from_email,email_app_password)
        server.send_message(message)
    return True


#validate token
def validateToken(token):
    try:
        data = serializer.loads(
            token,
            salt = "reset-password",
            max_age=600
        )
        return data
    except BadSignature:   # if token changed
        return "Invalid"  
    except TimedSerializer: # if token time out
        return "Timeout"


def readNotesByUserId(user_data):
    user_id = user_data['user_id']
    connection = getConnectionWithDB()
    if connection == 'Connection Failed':
        return []
    else:
        cursor = connection.cursor()
        query = "SELECT id, title, content, created_at FROM notes WHERE user_id=%s ORDER BY created_at DESC"
        cursor.execute(query, (user_id,))
        data = cursor.fetchall()
        notes = []
        for record in data:
            notes.append({
                'id': record[0],
                'title': record[1],
                'content': record[2],
                'created_at': record[3]
            })
        cursor.close()
        connection.close()
        return notes


def insertNote(note_data):
    connection = getConnectionWithDB()
    if connection == 'Connection Failed':
        return False
    else:
        try:
            cursor = connection.cursor()
            query = "INSERT INTO notes(user_id, title, content) VALUES (%s, %s, %s)"
            values = (note_data['user_id'], note_data['title'], note_data['content'])
            cursor.execute(query, values)
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Exception as e:
            print("Error inserting note:", e)
            return False


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='GET':
        return render_template('register.html')
    elif request.method=='POST':
            name=request.form['name']
            email=request.form['email']
            password=request.form['password']
            confirm_password=request.form['confirm_password']
            user_data={
                "name":name,
                "email":email,
                "password":password,
                "confirm_password":confirm_password
                }        
            errors=validateDataForRegister(user_data)
            if errors:
                return render_template('register.html',errors=errors)
            else:
                is_duplicate=verifyDuplicateEmail(user_data)
                if is_duplicate==False:
                    OTP=generateOTP()
                    password_hash=generateHash(user_data['password'])
                    name=user_data['name']
                    email=user_data['email']
                    status = insertUserRecord({
                    "name": name,
                    "email": email,
                    "password_hash": password_hash
                })
                    if status == True:
                        session['username']=email 
                        session['otp']=OTP  
                        SendEmail(subject="Verify Your Registration - Notes Management",
                                  to_email=email,
                                  body=EmailTemplates.send_otp_template(username=name,otp=OTP)
                                  )
                        # return render_template('register.html', res = 'Registration Successfully Completed')
                        return redirect('/verify')
                    else:
                        return render_template('register.html',err='Registration failed')
                
                else:
                    return render_template('register.html',err="Account already exists")
 
                
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif (request.method == 'POST'):
        email = request.form['email']
        password = request.form['password']
        # we have to check acc existed or not
        # if data exist, then we have to check is_verified is True or False
        # if acc exist and verified, then compare passwords
        # if password is equal then create session.. inside session we have to store email
        user_data = readUserRecordByEmail({'email': email})
        if user_data == 'No record':
            return render_template('login.html', err = "Email Not exist")
        elif user_data['is_verified'] == False:
            return render_template('login.html', err = "Please Verify you account")
        elif bcrypt.checkpw(password.encode('utf-8'), user_data['password_hash'].encode('utf-8')) == False:
            return render_template('login.html', err = "Passwords do not match")
        else:
            session['username'] = user_data['name']
            session['email'] = email
            session['id'] = user_data['id']
            return redirect('/dashboard')


@app.route('/dashboard')
def dashboard():
    if "id"  not in session:
        return redirect('/login')
    email = session['email']
    username = session['username']
    return render_template('dashboard.html',  username = username)


@app.route('/verify',methods=['GET','POST'])
def verify():
    if request.method == 'GET':
        return render_template('verify.html')
    elif (request.method == 'POST'):
        otp = request.form['otp']
        otp = int(otp)
        if otp == session['otp']:
            is_verify = True
            updateIsverifiedByIdorEmail({'email':session['username'],'is_verified':is_verify})
            return redirect('/login')
        else:
            return render_template('verify.html',err="Invalid OTP")


@app.route("/logout",methods=["GET"])
def logout():
    if "id" in session:
        session.pop('id',None)
        session.pop('username',None)
        session.pop('email',None)
        return redirect('/login')


@app.route("/profile", methods=["GET"])
def profile():
    if "id" not in session:
        return redirect("/login")
    
    user_data = readUserRecordByEmail({"email": session["email"]})
    if user_data == "No record":
        return render_template("profile.html", user=None, err="User not found")
    return render_template("profile.html", user=user_data)


@app.route("/forgot-password",methods=['GET','POST'])
def forgot_password():
    if request.method=='GET':
        return render_template("forgot_password.html")
    if request.method=='POST':
        email=request.form.get('email',None)
        user_data = readUserRecordByEmail({'email': email})
        if "id" in user_data:
            #generate token
            token=resetPasswordTokenGenerate(email=email)
            #reset password url
            reset_url=url_for('reset_password',token=token,_external=True)
            email_status=SendEmail(
                subject="Password Reset Request",
                to_email=email,
                body=EmailTemplates.send_reset_password_template(
                    username=user_data['name'],
                    link=reset_url,
                    time=5
                )
                )
            if email_status:
                return render_template('forgot_password.html', msg = "Password reset link sent to your email")
            else:
                return render_template('forgot_password.html', err = "Unable to send the email")
        else:
            return render_template('forgot_password.html', err = "Enter a valid registered email")


# reset password route
@app.route('/reset-password/<string:token>', methods = ['GET','POST'])
def reset_password(token):
    token_status = validateToken(token=token)
    if token_status == 'Invalid':
        return render_template('forgot_password.html', err = "Invalid URL")
    elif token_status == 'Timeout':
        return render_template('forgot_password.html', err = "URL Expired")
    email = token_status
    if request.method == 'GET':
        return render_template('reset_password.html')
    # POST request
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        if new_password == confirm_password:
            # generate hash password
            password_hash = generateHash( text = new_password)
            # update password in DB
            data = {'email':email,
                    'new_password':password_hash
                    }
            update = updatePasswordByIdorEmail(user_data=data)
          
            if update:
                # redirect to login page
                return redirect('/login')
            else:
                return render_template('reset_password.html',err="Password update failed")
        else:
            return render_template('reset_password.html', err = "Password Mismatch")


@app.route('/notes')
def my_notes():
    if "id" not in session:
        return redirect('/login')

    notes = readNotesByUserId({"user_id": session['id']})
    return render_template("notes.html", notes=notes)


@app.route('/notes/add', methods=['GET', 'POST'])
def add_note():
    if "id" not in session:
        return redirect('/login')

    if request.method == 'GET':
        return render_template('add_note.html')

    elif request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        status = insertNote({
            "user_id": session['id'],
            "title": title,
            "content": content
        })

        if status:
            return redirect('/notes')
        else:
            return render_template('add_note.html', err="Failed to add note")


@app.route('/notes/<int:note_id>')
def view_note(note_id):
    if "id" not in session:
        return redirect('/login')

    connection = getConnectionWithDB()
    cursor = connection.cursor()
    cursor.execute("SELECT id, title, content, created_at FROM notes WHERE id=%s AND user_id=%s", (note_id, session['id']))
    data = cursor.fetchone()
    cursor.close()
    connection.close()

    if not data:
        return render_template("note_view.html", err="Note not found")

    note = {
        "id": data[0],
        "title": data[1],
        "content": data[2],
        "created_at": data[3]
    }
    return render_template("note_view.html", note=note)


@app.route('/notes/<int:note_id>/edit', methods=['GET','POST'])
def edit_note(note_id):
    if "id" not in session:
        return redirect('/login')

    connection = getConnectionWithDB()
    cursor = connection.cursor()

    if request.method == 'GET':
        cursor.execute("SELECT id, title, content FROM notes WHERE id=%s AND user_id=%s", (note_id, session['id']))
        data = cursor.fetchone()
        cursor.close()
        connection.close()
        if not data:
            return render_template("edit_note.html", err="Note not found")
        return render_template("edit_note.html", note={"id": data[0], "title": data[1], "content": data[2]})

    elif request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        cursor.execute("UPDATE notes SET title=%s, content=%s WHERE id=%s AND user_id=%s", (title, content, note_id, session['id']))
        connection.commit()
        cursor.close()
        connection.close()
        return redirect('/notes')


@app.route('/notes/<int:note_id>/delete', methods=['POST'])
def delete_note(note_id):
    if "id" not in session:
        return redirect('/login')

    connection = getConnectionWithDB()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM notes WHERE id=%s AND user_id=%s", (note_id, session['id']))
    connection.commit()
    cursor.close()
    connection.close()
    return redirect('/notes')


@app.route('/notes/<int:note_id>/delete', methods=['GET', 'POST'])
def delete_note(note_id):
    if "id" not in session:
        return redirect('/login')

    connection = getConnectionWithDB()
    cursor = connection.cursor()

    if request.method == 'GET':
        # Fetch note details to show confirmation
        cursor.execute("SELECT id, title, content FROM notes WHERE id=%s AND user_id=%s", (note_id, session['id']))
        data = cursor.fetchone()
        cursor.close()
        connection.close()

        if not data:
            return render_template("delete_note.html", err="Note not found")

        note = {"id": data[0], "title": data[1], "content": data[2]}
        return render_template("delete_note.html", note=note)

    elif request.method == 'POST':
        # Perform deletion
        cursor.execute("DELETE FROM notes WHERE id=%s AND user_id=%s", (note_id, session['id']))
        connection.commit()
        cursor.close()
        connection.close()
        return redirect('/notes')

if(__name__=="__main__"):
    app.run(host='0.0.0.0',port=5000,debug=True)