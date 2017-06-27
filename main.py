import logging
from random import randint
from flask import Flask, render_template
from pymongo import MongoClient
from flask_ask import Ask, statement, question, session

app = Flask(__name__)
db_client = MongoClient("mongodb://admin:admin@ds137882.mlab.com:37882/riddles")
db = db_client.riddles
db_collection = db.riddles

riddles=[]

ask = Ask(app, "/")

logging.getLogger("flask_ask").setLevel(logging.DEBUG)

@ask.launch
def new_game():
    count = session.attributes['count'] = 0
    print(riddles[count]["question"])
    welcome_msg = render_template('welcome')
    return question(welcome_msg)

@ask.intent("YesIntent")
def next_round():
    numbers = [randint(0, 9) for _ in range(3)]
    session.attributes['count'] = 1
    count = session.attributes['count']
    print(riddles[count]["question"])
    round_msg = riddles[count]["question"]
    return question(round_msg)

@ask.intent("AnswerIntent", convert={'answer': str})
def answer(answer):
    count = session.attributes['count']
    print(riddles[count]["answer"])
    #winning_numbers = session.attributes['numbers']
    if riddles[count]["answer"] == answer:
        msg = render_template('right')
    else:
        msg = render_template('wrong')
    return statement(msg)

if __name__ == '__main__':
    riddles = list(db_collection.find())
    app.run(debug=True)