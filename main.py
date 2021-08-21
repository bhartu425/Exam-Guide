from flask import Flask,render_template,request,redirect,session
from flask_sqlalchemy import SQLAlchemy
import os
import json
app=Flask(__name__)
app.secret_key = 'super-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///question_papers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['UPLOAD_FOLDER'] = 'F:\\question paper project\\static\\question_paper'
db=SQLAlchemy(app)
with open('config.json', 'r') as c:
    json_data = json.load(c)["parameter"]
class Stream(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stream_name = db.Column(db.String(80), nullable=False)
    subject_name = db.Column(db.String(200), nullable=False)
    semester = db.Column(db.String(80), nullable=False)
    year = db.Column(db.String(80), nullable=False)
    file_name=db.Column(db.String(200), nullable=False)

@app.route('/')
def home():
    streams=Stream.query.all()
    #this function will check the how many semesters display in the streams
    def semester_checker(stream_call):
        s_count=[i.semester for i in streams if stream_call==i.stream_name]
        maximum_value=max(s_count)
        return maximum_value[0]
    app.jinja_env.globals.update(semester_checker=semester_checker)
    return render_template('index.html',streams=streams)
@app.route('/backend',methods=['GET','POST'])
def back_end():
    if 'user' in session and session['user']==json_data['user_name']:
        if request.method=='POST':
            search_stream_subject=request.form.get('search_subject')
            if search_stream_subject:
                stream_data=Stream.query.filter_by(stream_name=search_stream_subject.upper())
                return render_template('back_end.html',stream_data=stream_data)
            stream_name=request.form.get('stream').upper()
            subject_name=request.form.get('subject').lower()
            semester=request.form.get('semester')
            year=request.form.get('year')
            file_name=request.files.get('file_name')
            file_name.save(os.path.join(app.config['UPLOAD_FOLDER'],file_name.filename))
            stream=Stream(stream_name=stream_name,subject_name=subject_name,semester=semester,year=year,file_name=file_name.filename)
            db.session.add(stream)
            db.session.commit()
            return redirect('/backend')
        stream_data=Stream.query.all()
        return render_template('back_end.html',stream_data=stream_data)
    else:
        return redirect('/login')
@app.route('/delete_stream/<id>')
def delete_stream(id):
    if 'user' in session and session['user']==json_data['user_name']:
        stream_delete = Stream.query.filter_by(id=id).first()
        db.session.delete(stream_delete)
        db.session.commit()
        return redirect('/backend')
    else:
        return redirect('/login')
@app.route('/update_stream/<id>',methods=['GET','POST'])
def update_stream(id):
    if 'user' in session and session['user']==json_data['user_name']:
        stream_update = Stream.query.filter_by(id=id).first()
        if request.method =="POST":
            new_stream=request.form.get('stream_update').upper()
            subject_update=request.form.get('subject_update').lower()
            semester_update=request.form.get('semester_update')
            print(new_stream,subject_update,semester_update)
            stream_update.stream_name=new_stream
            stream_update.subject_name=subject_update
            stream_update.semester=semester_update
            db.session.commit()
            return redirect('/backend')
        return render_template('stream_update.html',stream_update=stream_update)
    else:
        return redirect('/login')
@app.route('/stream/<stream_name>/<semester>',methods=['GET','POST'])
def question_paper(stream_name,semester):
    if request.method=='POST':
        search_subject=request.form.get('search_subject').lower()
        if search_subject:
            data=Stream.query.filter_by(stream_name=stream_name,semester=semester,subject_name=search_subject).all()
        else:
            data=Stream.query.filter_by(stream_name=stream_name,semester=semester).all()
    else:
        data=Stream.query.filter_by(stream_name=stream_name,semester=semester).all()
    return render_template('show_question_paper.html',data=data)
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=="POST":
        username=request.form.get('username')
        password=request.form.get('password')
        if json_data['user_name']==username and json_data['password']==password:
            session['user']=username
            return redirect('/backend')
        else:
            return redirect('/login')
    return render_template('login.html')
@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/login')
if __name__=='__main__':
    app.run(debug=True)