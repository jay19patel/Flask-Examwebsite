

from flask import Flask,render_template,request,session,redirect,url_for,flash,jsonify,Blueprint
from pymongo import MongoClient # mongodb 
from flask_jwt_extended import create_access_token,get_jwt_identity,jwt_required,JWTManager,set_access_cookies,unset_jwt_cookies
from datetime import timedelta
import requests

app = Flask(__name__)


app.secret_key = 'jaypateltopsecret789654123'
app.config["JWT_SECRET_KEY"] = "jaypateltopsecret789654123" 
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=60) 
jwt = JWTManager(app)

client = MongoClient('localhost', 27017) # connection 
db = client.Website # create table
regapi = db.Userdata # triger
qna_bank = db.QNA_bank # triger

# expire token 
@jwt.expired_token_loader
def handle_expired_token(jwt_header, jwt_payload):
    return redirect(url_for('LoginPage'))  


@jwt.unauthorized_loader
def custom_unauthorized_response(_err):
    return redirect(url_for('LoginPage'))



@app.route('/login',methods=['GET','POST'])
def LoginPage():
    error =None
    if request.method == "POST":
        email=request.form['loginemail']
        pwd=request.form['loginpss']
        userdata=regapi.find_one({'email':email})
        if not userdata:
            flash("Email id not Founed Please Check Email id ")
            return redirect(url_for('LoginPage'))
        else:
            newpwd = pwd[::-1]+pwd[::-1]+pwd
            if userdata['password'] == newpwd:
                print("login done ....")
                access_token = create_access_token(identity=(
                    {'name':userdata['name'],
                     'city':userdata['city'],
                     'email':userdata['email'],
                     'school_id':userdata['school_id']}
                     )
                    )
                res = redirect(url_for('HomePage'))
                set_access_cookies(res, access_token) 
                session['login_user'] = "login"
                session['youare'] = userdata['school_id']
                session['in_auther'] = userdata['name']
                print("login sucsessfull ......")     
                return res
               

            else:
                flash('Email & Password not match')
                return redirect(url_for('LoginPage'))

    
    return render_template('LoginPage.html')





@app.route('/logout',methods=['GET','POST'])
@jwt_required()
def Logout():
    res = jsonify({"message":"logout"})
    unset_jwt_cookies(res)
    session.clear()
    session['login_user']='logout'
    print("loged out...")
    flash("You are logout Login New ID ")
    return redirect(url_for('HomePage'))



@app.route('/register',methods=['GET','POST'])
def RegistrationPage():
    if request.method == "POST":
        name=request.form['fullname']
        city=request.form['mycity']
        email=request.form['myemail']
        pwd1=request.form['pass1']
        pwd2=request.form['pass2']
        School_id=request.form['School_id']
        print(name,city,email)
        if pwd1==pwd2:
            newpwd = pwd1[::-1]+pwd1[::-1]+pwd1
            senddata = regapi.insert_one({
                "name":name,
                "city":city,
                "email":email,
                "password":newpwd,
                'school_id':School_id
            })
            flash('You were successfully Register Your Data')
            print("Registration Successhull......")  
            return redirect(url_for('LoginPage'))


        else:
            flash('Some kind of MisMatch Please Check Data')
            return redirect(url_for('RegistrationPage'))

    return render_template('RegistrPage.html')


@app.route("/" ,methods=["GET"])
def HomePage():
    if session.get('login_user'):
        if session['login_user'] == 'login':
            schholid = session['youare']
            if schholid == "190200107098":
                youare = "TEACHER"
            else:
                youare = "STUDENT"
            print("loged in ...")
            return render_template('Home.html',data=youare)
        return render_template('Home.html')
    else:
        print(" not loged in ...")
        return render_template('Home.html')

   

@app.route('/test',methods=['GET','POST'])
@jwt_required()
def TestPage():
    if session['login_user'] == 'login':
        alldata = qna_bank.find()

        # if request.method=="POST":
        #     pass 

        data = get_jwt_identity()
        name = data['name']
        email = data['email']
        city = data['city']
        print(session['login_user'])
        return render_template('Test.html',name=name,email=email,city=city,alldata=alldata)
    else:
        flash("You are not Log in, Login and then use TEST Page ")
        return redirect(url_for('LoginPage'))
    




@app.route('/dashbord')
@jwt_required()
def Dashbord():
    if session.get('youare'):
        if session['youare'] == "190200107098":
            if session['login_user'] == 'login': 
                return render_template('admin.html')
            else:
                flash("You are not Log in, Login and then use TEST Page ")
                return redirect(url_for('LoginPage'))
        else:
            flash("you are not access dashbord page")
            return redirect(url_for('HomePage'))
    flash("You are not Login, Plase Log In First")
    return redirect(url_for('HomePage'))

    
    
@app.route('/add_qna',methods=['GET','POST'])
@jwt_required()
def add_qna():
    if session['youare'] == "190200107098":
        if request.method == "POST":
            qna = request.form['qna']
            senddata = qna_bank.insert_one(
                {"quation":qna,"auth":session['in_auther']})
            flash("your quation was added in data base ")
        return render_template('addqna.html')
    else:
        flash("you are not access add_qna page")
        return redirect(url_for('HomePage'))

   
@app.route('/show_all',methods=['GET','POST'])
@jwt_required()
def show_all():
    if session['youare'] == "190200107098":
        alldata = qna_bank.find({'auth':session['in_auther']})
        print(alldata)
        return render_template('showall.html',data=alldata)
    else:
        flash("you are not access show_all page")
        return redirect(url_for('HomePage'))



@app.errorhandler(404)
def error404(error=None):
    return "<h1>Page Not Found</h1>"


# _______run_________________
if __name__=='__main__':
    app.run(debug=True)