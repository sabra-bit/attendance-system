
# venv\Scripts\activate
# Set-ExecutionPolicy Unrestricted -Scope Process
from datetime import datetime ,date,timedelta
import csv ,os
import sqlite3
from flask import Flask, redirect, url_for, render_template, request, session, jsonify

app = Flask(__name__)

app.secret_key = "sabraSecret"
# app.permanent_session_lifetime= timedelta(minutes=3)

@app.route('/')  
def index():
    return render_template("login.html")  
    # return render_template("upload.html")

@app.route('/admin', methods = ['POST','GET'])  
def admin():
    if "admin" in session:
        return render_template("admin.html")
    else:
        return redirect("/")

@app.route('/viewatendance', methods = ['POST','GET'])  
def viewAtt():
    if "id" in session:
        att = request.form["att"] # course id
        ID=session["id"]
        con = sqlite3.connect("data_store.db") 
        cur = con.cursor()

        cur.execute("select  Dname,DTime,DDate,STU,STUdateTime,attType  from atendance Where DID=? and courseID =? ;",(ID,att))
        result = cur.fetchall()
        return render_template("viewDoctor.html" , data=result)
    else:
        return redirect("/")


@app.route('/user', methods = ['POST','GET'])  
def user():
    if "id" in session:
        name = session["name"]
        cId=len(session["courseID"])

        return render_template("user.html", x=cId, name=name,courseId=session["courseID"],courseName=session["courseName"])
    else:
        return redirect("/")

@app.route("/genrate", methods=["POST", "GET"] )
def genrateQR():
    if "id" in session:
        today = date.today().strftime("%d/%m/%Y")
        now = datetime.now().strftime("%H:%M:%S")
        qr = request.form["QRdata"]
        qr = qr +"-"+str(now)+"-"+today+"-"+session["name"]+"-"+session["id"]
        return render_template("genrate.html",qdata=qr)
    else:
        return redirect("/")

@app.route("/sss", methods=[ "GET","POST"] )
def addAT():
        if request.method == 'POST':
            now = datetime.now()
            ID = request.json['data']
            data=ID
            data = data.split("-")
            if len(data) ==7:
                
                con = sqlite3.connect("data_store.db") 
                cur = con.cursor()
                cur.execute("create table if not exists atendance (courseID text NOT NULL,DTime text NOT NULL,DDate text NOT NULL,Dname text NOT NULL,DID text NOT NULL,STU text NOT NULL,MAC text NOT NULL,STUdateTime text NOT NULL,attType text NOT NULL)")
                with sqlite3.connect("data_store.db") as con:  
                            cur = con.cursor()  
                            cur.execute("INSERT INTO atendance (courseID,DTime,DDate,Dname,DID,STU,MAC,STUdateTime,attType) values (?,?,?,?,?,?,?,?,?)",(data[0],data[1],data[2],data[3],data[4],data[5],data[6],now,"physical"))  
                            con.commit()  
                            msg = "Added" 
                
                return jsonify(msg)
    
        else:
            return 'no bad req.'

@app.route("/sss2", methods=["POST", "GET"] )
def uploadDoctor():
    if "id" in session:
        if request.method == 'POST':
            today = date.today().strftime("%d/%m/%Y")
            now = datetime.now().strftime("%H:%M:%S")
            courseIDg = request.form["att1"]
            ID = session["id"] 
            name = session["name"]
            mac = "NULL" 
            Type = "logical"
            
            f = request.files['file']  
            f.save(f.filename)  
            os.rename(f.filename, 'att.csv')
            con = sqlite3.connect("data_store.db") 
            cur = con.cursor()
            cur.execute("create table if not exists atendance (courseID text NOT NULL,DTime text NOT NULL,DDate text NOT NULL,Dname text NOT NULL,DID text NOT NULL,STU text NOT NULL,MAC text NOT NULL,STUdateTime text NOT NULL,attType text NOT NULL)")
            with open('att.csv','r') as fin: # `with` statement available in 2.5+
            # csv.DictReader uses first line in file for column headings by default
                dr = csv.DictReader(fin) # comma is default delimiter
                to_db = [(courseIDg,now,today,name,ID,i['STU'],mac,i['time'] ,Type ) for i in dr]
          
            cur = con.cursor()
            cur.executemany("INSERT INTO atendance (courseID,DTime,DDate,Dname,DID,STU,MAC,STUdateTime,attType) values (?,?,?,?,?,?,?,?,?)",(to_db))  
            con.commit()
            os.remove("att.csv")  
            name = session["name"]
            cId=len(session["courseID"])

            return render_template("user.html",msg="uplode Done!", x=cId, name=name,courseId=session["courseID"],courseName=session["courseName"])

        else:
            return 'bad req.'
        
    
    else:
        return redirect("/")
    

@app.route('/addcourse', methods = ['POST','GET'])  
def addCourse():
    if "admin" in session:   
        ID = request.form["id"]
        CourseName = request.form["courseName"]
        CourseId = request.form["courseId"]
        con = sqlite3.connect("data_store.db") 
        cur = con.cursor()
        con.execute("create table if not exists course  (id INTEGER PRIMARY KEY AUTOINCREMENT, D_id TEXT NOT NULL, courseName TEXT NOT NULL, courseId TEXT NOT NULL)")
        with sqlite3.connect("data_store.db") as con:  
                    cur = con.cursor()  
                    cur.execute("INSERT into course (D_id, courseName, courseId) values (?,?,?)",(ID,CourseName,CourseId))  
                    con.commit()  
                    msg = "doctor successfully Added" 
        return render_template("admin.html" , ms=msg)
    else:
        return redirect("/")


@app.route('/add', methods = ['POST','GET'])  
def add():
    if "admin" in session:   
        ID = request.form["id"]
        Name = request.form["name"]
        con = sqlite3.connect("data_store.db") 
        cur = con.cursor()
        con.execute("create table if not exists doctor  (id INTEGER PRIMARY KEY AUTOINCREMENT, id_num TEXT UNIQUE NOT NULL, name TEXT NOT NULL)")
        with sqlite3.connect("data_store.db") as con:  
                    cur = con.cursor()  
                    cur.execute("INSERT into doctor (id_num, name) values (?,?)",(ID,Name))  
                    con.commit()  
                    msg = "doctor successfully Added" 
        return render_template("admin.html" , ms=msg)
    else:
        return redirect("/")


@app.route('/login', methods = ['POST'])  
def login():
    ID = request.form["ID"]
    con = sqlite3.connect("data_store.db") 
    cur = con.cursor()
    cur.execute("select * from admin")
    result = cur.fetchall()
    print (ID) # do session 5 min
    for row in result:
        if ID == row[0]:
            session["admin"] = row[0]
            return redirect("/admin")
    
    cur.execute("select id_num ,name ,courseName,courseId  from doctor, course Where id_num= ? and D_id=?;",(ID,ID))
    result = cur.fetchall()
    print (ID) # do session 5 min
    name =[]
    C_id =[]
    name.clear()
    C_id.clear()
    for row in result:
        if ID == row[0]: 
            name.append(row[2]) 
            C_id.append(row[3])
    session["courseName"] =[]
    session["courseID"] =[]

    for row in result:
        if ID == row[0]:
            session["id"] = row[0]
            session["name"] = row[1] 
            session["courseName"] = name
            session["courseID"] = C_id
            return redirect("/user")
    
    return render_template("login.html", ms="Bad ID")  
    
@app.route('/viewDoctor', methods = ['POST','GET'])  
def viewD():
    if "admin" in session:
        con = sqlite3.connect("data_store.db") 
        cur = con.cursor()

        cur.execute("select id_num ,name ,courseName,courseId  from doctor, course Where id_num= D_id ;")
        result = cur.fetchall()
        return render_template("view.html" , data=result)
    else:
        return redirect("/")




    # if result:
    #     redirect("/admin")

    # return render_template("user.html") 

@app.route('/out', methods = ['POST','GET'])  
def out():
    if "admin" in session:
        session.pop("admin",None)
        return redirect("/") 
    
    elif "id" in session:
        session.pop("id",None)
        session.pop("name",None)
        session.pop("courseName",None)
        session.pop("courseID",None)
        
        return redirect("/") 
    else:
        return redirect("/")



if __name__ == '__main__':
    app.run(host="0.0.0.0" ,port=5001 , debug= True)
    # app.run(debug= True)