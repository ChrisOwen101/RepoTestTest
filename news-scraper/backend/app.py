from datetime import datetime
import json
from flask_sqlalchemy import SQLAlchemy
from flask import Flask,jsonify,request, make_response
from flask_cors import CORS
import psycopg2
from sqlalchemy import desc

app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://domvinyard@localhost/social_news'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app, origins=["http://127.0.0.1:8080", "localhost"], supports_credentials=True)

@app.route('/')
def index():
    return "Welcome to the Social News API!"

@app.route('/stories', methods = ['POST', 'GET'])
def stories():
    if(request.method == 'POST'):
        return add_story(request.json)
    else:
        return get_stories()

@app.route('/stories/<id>/votes', methods=['POST'])
def vote(id):
    if(request.method == 'POST'):
        update_vote(request.data, id)
        return jsonify({"Success": True, "Message": "Vote updated"}), 201

@app.route('/story/<id>')
def get_story(id):
    queried = db.session.query(Story).filter(Story.id == id).all()
    story = []
    for q in queried:
        story.append(q.title)
    return jsonify(story), 200

@app.route('/search')
def search_stories():
    li = request.args['tags'].split(",")
    newl = []
    for l in li:
        newl.append(l.capitalize())
    stories = get_searched_stories(tuple(newl))
    print(stories)
    return jsonify(stories)



def get_searched_stories(search_terms):
    conn = None
    try:
        conn = psycopg2.connect(host="localhost",database="social_news", user="domvinyard")
        cur = conn.cursor()
        query = "SELECT stories.title, tags.description FROM stories JOIN metadata ON metadata.story_id = stories.id JOIN tags ON tags.id = metadata.tag_id WHERE tags.description IN %(search_terms)s;"
        cur.execute(query, {"search_terms": search_terms})
        data = cur.fetchall()
        cur.close()
        return data
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def update_vote(data, id):
    direction = json.loads(data)['direction']
    add_score = 0
    if direction == 'down':
        add_score = -1
    else: 
        add_score = 1
    
    db.session.query(Story).filter(Story.id == id).update({"score": Story.score + add_score})
    db.session.commit()

def add_story(data):
    story = Story(title=data.title, url=data.url)
    db.session.add(story)
    db.session.commit()
    return jsonify({"Success": True,"Response": "Story added"}), 200

def get_stories():
    all_stories = []
    stories = Story.query.order_by(desc(Story.score)).all()
    for story in stories:
        all_stories.append({"id": story.id, "title": story.title, "url": story.url, "created_at": story.created_at, "updated_at": story.updated_at, "score": story.score})
    return jsonify(
        {
            "success": True,
            "stories": all_stories,
            "total_stories": len(stories),
        }
    ), 200

row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}

class Story(db.Model):
    __tablename__ = "stories"
    id = db.Column(db.Integer, primary_key = True)
    title = db. Column(db.Text, nullable = False)
    url = db.Column(db.Text, nullable = False)
    created_at = db.Column(db.DateTime, nullable = False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable = False, default=datetime.utcnow)
    score = db.Column(db.Integer, nullable = False, default=0)

    def __repr__(self):
        return '<Story %r>' % self.title