from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Time as SQLAlchemyTime
from datetime import datetime, time

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookings.db'
db = SQLAlchemy(app)

class Constants:
    SUCCESSFUL = "successful"
    FAILED = "failed"
    STATUS = "status"
    MESSAGE = "message"
    JSON_RESPONSE = {
        STATUS: "",
        MESSAGE: ""
    }

class Maid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    start_time = db.Column(SQLAlchemyTime, nullable=False)
    end_time = db.Column(SQLAlchemyTime, nullable=False)
    booked = db.Column(db.Boolean, default=False) 


@app.route("/", methods=["GET"])
def index():
    booking_time = request.args.get("booking_time")
    message = None

    if booking_time:
        booking_time = datetime.strptime(booking_time, "%H:%M").time()
        available_maids = Maid.query.filter(Maid.start_time <= booking_time, Maid.end_time >= booking_time, Maid.booked == False)
        sorted_maids = available_maids.order_by(Maid.rating.desc())
        if not sorted_maids.count():
            message = "Sorry, no maids available."
        return render_template("index.html", maids=sorted_maids, booking_time=booking_time, message=message, booked_message=None)
    return render_template("index.html", maids=[], booking_time=None, message=None, booked_message=None)


@app.route("/book", methods=["POST"])
def book():
    maid_id = request.form.get("maid_id")
    booking_time = request.form.get("booking_time")
    # print(booking_time)
    booking_time = datetime.strptime(booking_time, "%H:%M:%S").time()
    # print(booking_time)
    maid = Maid.query.get(maid_id)
    # status = Constants.FAILED
    message = f"Maid with id {maid_id} does not exist"
    if maid:
        # print(maid.start_time)
        # print(maid.end_time)
        if maid.start_time <= booking_time <= maid.end_time and not maid.booked:
            maid.booked = True
            db.session.commit()
            message = "Booking successful"
            status = Constants.SUCCESSFUL
        else:
            message = f"Maid with id {maid_id} is not available"
    return render_template("index.html", maids=[], booking_time=None, message=None, booked_message=message)
    # return {
    #     Constants.STATUS: status,
    #     Constants.MESSAGE: message
    # }


@app.route("/get_all", methods=["GET"])
def get_all():
    # return Maid.query.all()
    all_maids = Maid.query.all()
    result_arr = []
    for maid in all_maids:
        maid_json = {
            "id": maid.id,
            "name": maid.name,
            "rating": maid.rating,
            "start_time": str(maid.start_time),
            "end_time": str(maid.end_time),
            "booked": maid.booked
        }
        result_arr.append(maid_json)
    
    return {"data": result_arr}


@app.route("/delete_all", methods=["DELETE"])
def delete_all():
    db.session.query(Maid).delete()
    db.session.commit()
    return {
        "status": "Successful",
        "message": "All maids deleted!"
    }
        

def setup_database():
    with app.app_context():
        db.create_all()
        maids = [
            Maid(name="Maid-1", rating=3.5, start_time=time(9,0), end_time=time(11,0)),
            Maid(name="Maid-2", rating=4.5, start_time=time(10,0), end_time=time(13,0))
        ]
        if Maid.query.all():
            delete_all()
        db.session.add_all(maids)
        db.session.commit()

setup_database()

if __name__ == "__main__":
    app.run(debug=True)
