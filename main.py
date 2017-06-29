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
riddles = list(db_collection.find())

ask = Ask(app, "/")

question_index = 0
incorrect_guesses = 0

logging.getLogger("flask_ask").setLevel(logging.DEBUG)

@ask.launch
def new_game():
    welcome_msg = render_template('welcome')
    print(riddles)
    print(len(riddles))
    return question(welcome_msg)

@ask.intent("ResumeRiddle")
@ask.intent("RepeatRiddle")
@ask.intent("YesIntent")
def next_round():
    global question_index
    if question_index < len(riddles):
        print(riddles[question_index]["question"])
        round_msg = riddles[question_index]["question"]
        return question(round_msg)
    else:
        round_msg = render_template('gameover')
        question_index = 0
        return statement(round_msg)

@ask.intent("AMAZON.StopIntent")
@ask.intent("NoIntent")
def end_round():
    round_msg = render_template('gameover')
    question_index = 0
    return statement(round_msg)

@ask.intent("AMAZON.HelpIntent")
def help_requested():
    round_msg = render_template('help')
    return question(round_msg)

@ask.intent("AnswerIntent", convert={'answer_response': str})
def answer(answer_response):
    global question_index, incorrect_guesses
    print(answer_response)
    print(riddles[question_index]["answer"])
    if riddles[question_index]["answer"] == answer_response:
        msg = render_template('right')
        question_index += 1
        incorrect_guesses = 0
    elif incorrect_guesses < 2 and riddles[question_index]["hints"][incorrect_guesses]:
        msg = riddles[question_index]["hints"][incorrect_guesses]
        incorrect_guesses += 1
    else:
        msg = render_template('wrong')
        incorrect_guesses = 0
    return question(msg)

if __name__ == '__main__':
    app.run(debug=True)
