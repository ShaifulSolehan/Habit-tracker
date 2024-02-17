import os
import datetime
import uuid
import certifi
from collections import defaultdict
from flask import Flask,render_template,request,redirect,url_for
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__,template_folder="templates")
client = MongoClient(os.environ.get("MONGODB_URI"))
app.db=client.habit_tracker

@app.context_processor
def add_cal_date_range():
    def date_range(start: datetime.datetime):
        dates = [start + datetime.timedelta(days=diff) for diff in range(-3,4)]
        return dates
    return {"date_range":date_range}

def today_at_midnight():
    today = datetime.datetime.today()
    return datetime.datetime(today.year, today.month, today.day)

@app.route("/")
def home():
    date_str = request.args.get("date")
    if(date_str):
        selected_date = datetime.datetime.fromisoformat(date_str)
    else:
        selected_date = datetime.datetime.today()

    habits_on_date = app.db.habits.find({"added":{"$lte":selected_date}})
    completions = [
        habit["habit"]
        for habit in app.db.completions.find({"date":selected_date})
    ]    
    return render_template("home.html", habits=habits_on_date,title="Habit tracker - Home",selected_date=selected_date,completions=completions)

@app.route("/add",methods=["GET","POST"])
def add_habit():
    today = today_at_midnight()

    if request.method == "POST":
        app.db.habits.insert_one(
            {"id":uuid.uuid4().hex, "added":today, "name":request.form.get("habit")}
        )
    return render_template("add_habit.html",title="Habit Tracker - Add Habit",selected_date=today)

@app.route("/complete",methods=["Post"])
def complete():
    date_string = request.form.get("date")
    habit = request.form.get("habitId")
    date=datetime.datetime.fromisoformat(date_string)
    app.db.completions.insert_one({"date":date, "habit":habit})
    
    return redirect(url_for("home",date=date_string))
