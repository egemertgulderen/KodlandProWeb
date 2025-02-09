from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Konfigürasyon ayarları
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '12421512361651252153215'

db = SQLAlchemy(app)

# Veritabanı modeli: Her sınav gönderimi kaydedilir.
class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

quiz_questions = [
    {
        "id": 1,
        "question": "Python ile sohbet botu otomasyonu için hangi kütüphane kullanılır?",
        "options": {"a": "discord.py", "b": "Flask", "c": "TensorFlow", "d": "BeautifulSoup"},
        "answer": "a"
    },
    {
        "id": 2,
        "question": "Python ile web geliştirme için hangi framework kullanılır?",
        "options": {"a": "discord.py", "b": "Flask", "c": "ImageAI", "d": "NLTK"},
        "answer": "b"
    },
    {
        "id": 3,
        "question": "Python ile yapay zeka geliştirmede en çok kullanılan kütüphanelerden biri hangisidir?",
        "options": {"a": "BeautifulSoup", "b": "Flask", "c": "TensorFlow", "d": "discord.py"},
        "answer": "c"
    },
    {
        "id": 4,
        "question": "Bilgisayar görüşü (Computer Vision) için aşağıdaki kütüphanelerden hangisi kullanılabilir?",
        "options": {"a": "NLTK", "b": "Flask", "c": "ImageAI", "d": "discord.py"},
        "answer": "c"
    },
    {
        "id": 5,
        "question": "Doğal Dil İşleme (NLP) için hangi kütüphane kullanılabilir?",
        "options": {"a": "TensorFlow", "b": "ImageAI", "c": "BeautifulSoup", "d": "NLTK"},
        "answer": "d"
    }
]

@app.route('/', methods=['GET', 'POST'])
def quiz():
    if request.method == 'POST':
        username = request.form.get('username')
        if not username:
            username = "Anonymous"

        score = 0
        for q in quiz_questions:
            user_answer = request.form.get(f'question_{q["id"]}')
            if user_answer == q["answer"]:
                score += 1

        new_submission = Submission(username=username, score=score)
        db.session.add(new_submission)
        db.session.commit()

        session['last_score'] = score
        user_best = db.session.query(db.func.max(Submission.score))\
                              .filter(Submission.username == username).scalar()
        session['user_best'] = user_best

        return redirect(url_for('result', username=username))

    global_best = db.session.query(db.func.max(Submission.score)).scalar() or 0
    user_best = session.get('user_best', 0)

    return render_template('quiz.html', questions=quiz_questions, global_best=global_best, user_best=user_best)

@app.route('/result')
def result():
    username = request.args.get('username', 'Anonymous')
    last_score = session.get('last_score', 0)
    user_best = session.get('user_best', 0)
    global_best = db.session.query(db.func.max(Submission.score)).scalar() or 0

    # Yüzdelik sonuç hesaplama
    total_questions = len(quiz_questions)
    last_percentage = (last_score / total_questions) * 100
    user_best_percentage = (user_best / total_questions) * 100
    global_best_percentage = (global_best / total_questions) * 100

    return render_template('result.html', username=username, last_score=last_score,
                           user_best=user_best, global_best=global_best,
                           last_percentage=last_percentage,
                           user_best_percentage=user_best_percentage,
                           global_best_percentage=global_best_percentage)

if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
