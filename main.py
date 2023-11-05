import os

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from helpers import apology, login_required, lookup, usd
from firebase_admin import credentials, firestore, initialize_app
from google.cloud.firestore_v1.base_query import FieldFilter, Or

from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

cred = credentials.Certificate("./scmachinery-troubleshooting/key.json")
default_app = initialize_app(cred)
db = firestore.client()
user_ref = db.collection('users')
trouble_ref = db.collection('trouble_info')

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
req = lambda cell: request.form.get(cell)

@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        username = request.form.get("username")
        password = request.form.get("password")
        if not username:
            flash("must provide username", 'warning')
        # Ensure password was submitted
        elif not password:
            flash("must provide password", 'warning')
        else:
            user = user_ref.document(username).get().to_dict()
            pwhash = user["hash"]
            if not check_password_hash(pwhash, password):
                flash("Wrong username or password", 'warning')
                return redirect("/login")
            
            session["username"] = username
            session["real_name"] = user["real_name"]
            session["admin"] = user["admin"]
            return redirect("/")
    
    # User reached route via GET or flash (as by clicking a link or via redirect)
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Ensure all required fields are provided
        username = request.form.get("username")
        real_name = request.form.get("real_name")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        admin = request.form.get("ifadmin")
        if not username:
            flash("ユーザー名を入力してください", 'warning')
        elif not real_name:
            flash("本名を入力してください", 'warning')  
        elif not password:
            flash("パスワードを入力してください", 'warning')
        elif not confirmation or not confirmation == password:
            flash("確認用パスワードが元のものと異なります", 'warning')
        else:
            collection_ref = db.collection('users')
            
            user = user_ref.document(username)
            if not user.get().exists:
                try:
                    user.set(
                        {
                            'real_name': real_name,
                            'hash': generate_password_hash(password),
                            'admin': admin
                        }
                    )
                    
                    session["username"] = username
                    session["real_name"] = real_name
                    session["admin"] = admin
                    return redirect("/")
                except Exception as e:
                    return apology(f"Query error: {e}", 500)
            else:
                flash("同じユーザ名が存在しています", 'warning')       

    return render_template("register.html")            


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Main page"""
    user = session_dict(session)
    trouble_ref = db.collection('trouble_info')
    if request.method == "POST":
        try:
            if req("search"):
                filter_1 = FieldFilter("main_category", "==", req("main_category"))
                filter_2 = FieldFilter("machine_name", "==", req("machine_name"))
                filter_3 = FieldFilter("part_name", "==", req("part_name"))
                or_filter = Or(filters=[filter_1, filter_2, filter_3])
                query = trouble_ref.where(filter=or_filter).stream()

            else: # when req("all")
                query = trouble_ref.stream()
        
            return render_template("result.html", query=query)
        except Exception as e:
            flash(e, "warning")

    return render_template("index.html", user=user["real_name"])

@app.route("/report", methods=["GET", "POST"])
@login_required
def report():
    """Report page"""
    user = session_dict(session)
    if request.method == "POST":
        try:
            trouble_ref.add(
                {
                    'username': user["username"],
                    'real_name': user["real_name"],
                    'datetime': req("datetime"),
                    'working_days': req("main_category"),
                    'main_category': req("machine_category"),
                    'machine_name': req("machine_name"),
                    'part_name': req("part_name"),
                    'area': req("area"),
                    'place': req("place"),
                    'detail': req("detail"),
                    'cause': req("cause"),
                    'solution': req("solution"),
                    'prevention': req("prevention"),
                    'others': req("others")
                }
            )
        except Exception as e:
            return apology(f"Query error: {e}", 500)

        flash("追加しました")

    return render_template("report.html", user=user)


@app.route("/logout")
def logout():
    """Log user out"""

    session.clear()

    return redirect("/")

@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    """Managing account"""

    user = session_dict(session)
    if request.method == "POST":
        pwhash = db.collection("users").document(user["username"]).get().to_dict()["hash"]
        if check_password_hash(pwhash, request.form.get("password")):
            db.collection("users").document(user["username"]).delete()
            session.clear()
            return redirect("/login")
        else:
            flash("Wrong password!", "warning")

    return render_template("account.html", user=user)

def session_dict(prop):
    dict = {
        "username": prop["username"],
        "real_name": prop["real_name"],
        "admin": prop["admin"]
    }
    return dict

if  __name__ == "__main__":
	app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

