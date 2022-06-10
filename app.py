from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy
import requests
from bs4 import BeautifulSoup
from time import sleep
from random import randint


app = Flask(__name__)
app.config['SECRET_KEY'] = 'python'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite'
app.config['SQLALCHEMY_BINDS'] = {'playlist': 'sqlite:///playlist.sqlite'}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), nullable=False)
    password = db.Column(db.String(40), nullable=False)

    def __str__(self):
        return f' {[self.username , self.password]}'


class playlist(db.Model):
    __bind_key__ = "playlist"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), nullable=False)
    songname = db.Column(db.String(40), nullable=False)
    artistname = db.Column(db.String(40), nullable=False)
    albumname = db.Column(db.String(40), nullable=False)

    def __str__(self):
        return f' {[self.username , self.songname, self.artistname, self.albumname]}'


db.create_all()
db.create_all(bind='playlist')

all_playlists = playlist.query.all()

all_users = users.query.all()

username = []
password = []
for each in all_users:
    username.append(each.username)
    password.append(each.password)


username2 = []
songname = []
artistname = []
albumname = []
table_song = []
table_artist = []
table_album = []
id = []
length = []

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login',  methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        if u == '' or p == '':
            flash('Fill in every blank space!', 'error')
        elif u not in username or p not in password:
            flash('Incorrect Information!', 'error')
        elif u in username and p not in password or username.index(u) != password.index(p):
            flash('Incorrect password!', 'error')
        elif u in username and p in password and username.index(u) == password.index(p):
            session['username'] = u
            return redirect(url_for('topsongs'))
        else:
            return redirect(url_for('home'))
    return render_template('login.html')


@app.route('/signup',  methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        r = request.form['repeat']
        c = request.form['checkbox']
        if u == '' or p == '' or r == '':
            flash('Please fill in every blank space!', 'error')
        elif u in username:
            flash('Username already exists!', 'error')
        elif p != r:
            flash('Passwords don\'t match up!', 'error')
        elif len(p) < 8:
            flash('Password should be at least 8 characters long!', 'error')
        elif u and p:
            user_1 = users(username=u, password=p)
            db.session.add(user_1)
            db.session.commit()
            for each in all_users:
                    username.append(u)
                    password.append(p)
            # session['username'] = u
            flash('Account was created, you can now log in!', 'create')
        else:
            flash('Fill in every blank space!', 'error')
    return render_template('signup.html')


@app.route('/topsongs')
def topsongs():
    url = 'https://www.billboard.com/charts/hot-100/'
    resp = requests.get(url)
    songs = []
    images = []
    artists = []
    final = []
    ranks = []
    soup = BeautifulSoup(resp.text, 'html.parser')
    section = soup.find('div', class_="chart-results-list // lrv-u-padding-t-150 lrv-u-padding-t-050@mobile-max")
    info = section.find_all('div', class_='o-chart-results-list-row-container')
    for infos in info:
        features = infos.find('ul',
                              class_="lrv-a-unstyle-list lrv-u-flex lrv-u-height-100p lrv-u-flex-direction-column@mobile-max")
        song = (features.h3.text.strip())
        artist = (features.span.text.strip())
        artists.append(artist)
        songs.append(song)
        image = infos.find('img',class_="c-lazy-image__img lrv-u-background-color-grey-lightest lrv-u-width-100p lrv-u-display-block lrv-u-height-auto")
        images.append(image['data-lazy-src'])
        rank = infos.find_all('li',class_="o-chart-results-list__item // a-chart-color u-width-72 u-wid"
                                          "th-55@mobile-max u-width-55@tablet-only lrv-u-flex lrv-u-flex-shrink-0 lrv-u-align-items-center lrv-u-jus"
                                          "tify-content-center lrv-u-border-b-1 u-border-b-0@mobile-max lrv-u-border-color-grey-light u-background-color-white-064@mobile-max u-hidden@mobile-max")

        for i in rank:
            ranks.append(i.text.strip())

    sleep(randint(1, 5))

    for i in range(1, 201, 2):
        final.append(ranks[i])

    return render_template('topsongs.html',  ranks=songs, artists=artists, images=images, final=final)


@app.route('/user', methods=['POST', 'GET'])
def user():
    if request.method == 'POST':
        u = session['username']
        s = request.form['songname']
        ar = request.form['artistname']
        al = request.form['albumname']
        if s == '' or ar == '':
            flash('Fill in every blank space!', 'error')
        elif al and s and ar:
            user_2 = playlist(username=u, songname=s, artistname=ar, albumname=al)
            db.session.add(user_2)
            db.session.commit()
            for each in all_playlists:
                username2.append(u)
                songname.append(s)
                artistname.append(ar)
                albumname.append(al)
            session['username'] = u
            flash('Song was added to your playlist!', 'create')
    return render_template('user.html')


@app.route('/myplaylist')
def myplaylist():
    table_song=[]
    table_artist=[]
    table_album=[]
    all_playlists = playlist.query.all()
    a = 0
    for each in all_playlists:
        if each.username == session['username']:
            table_song.append(each.songname)
            table_artist.append(each.artistname)
            table_album.append(each.albumname)
            a = a +1
    return render_template('myplaylist.html', song=table_song, artist=table_artist, album=table_album, length=a)


@app.route('/allplaylists')
def allplaylists():
    table_song=[]
    table_artist=[]
    table_album=[]
    all_playlists = playlist.query.all()
    a = 0
    for each in all_playlists:
        table_song.append(each.songname)
        table_artist.append(each.artistname)
        table_album.append(each.albumname)
        a = a + 1
    return render_template('allplaylists.html', song=table_song, artist=table_artist, album=table_album, len=a)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)


