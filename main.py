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

logging.getLogger("flask_ask").setLevel(logging.DEBUG)

@ask.launch
def new_game():
    welcome_msg = render_template('welcome')
    session.attributes['question_index'] = 0
    session.attributes['incorrect_guesses'] = 0
    print('---start---')
    print(riddles)
    print(len(riddles))
    return question(welcome_msg)


@ask.intent("ResumeRiddle")
@ask.intent("RepeatRiddle")
@ask.intent("YesIntent")
def next_round():
    print('---next question---')
    print(session.attributes['question_index'])
    if session.attributes['question_index'] < len(riddles):
        print(riddles[session.attributes['question_index']]["question"])
        round_msg = riddles[session.attributes['question_index']]["question"]
        return question(round_msg)
    else:
        round_msg = render_template('gameover')
        session.attributes['question_index'] = 0
        return statement(round_msg)


@ask.intent("NoIntent")
@ask.intent("AMAZON.StopIntent")
@ask.intent("AMAZON.CancelIntent")
def end_round():
    print('---end round---')
    print(session.attributes['question_index'])
    round_msg = render_template('gameover')
    session.attributes['question_index'] = 0
    return statement(round_msg)


@ask.intent("AMAZON.HelpIntent")
def help_requested():
    print('---help---')
    print(session.attributes['question_index'])
    round_msg = render_template('help')
    return question(round_msg)


@ask.intent("AnswerIntent", convert={'answer_response': str})
def answer(answer_response):
    print('---answer---')
    print(answer_response)
    print(session.attributes['question_index'])
    if riddles[session.attributes['question_index']]["answer"] == answer_response:
        msg = render_template('right')
        session.attributes['question_index'] += 1
        session.attributes['incorrect_guesses'] = 0
    elif session.attributes['incorrect_guesses'] < 2 and riddles[session.attributes['question_index']]["hints"][session.attributes['incorrect_guesses']]:
        msg = riddles[session.attributes['question_index']]["hints"][session.attributes['incorrect_guesses']]
        session.attributes['incorrect_guesses'] += 1
    else:
        msg = render_template('wrong')
        session.attributes['incorrect_guesses'] = 0
    return question(msg)

if __name__ == '__main__':
    app.run(debug=True)
