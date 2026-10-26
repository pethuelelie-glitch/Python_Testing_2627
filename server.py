import json
from flask import Flask,render_template,request,redirect,flash,url_for


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary',methods=['POST'])
def showSummary():
    matchingClubs = [club for club in clubs if club['email'] == request.form['email']]
    if not matchingClubs:
        flash("Sorry, that email wasn't found.")
        return redirect(url_for('index'))
    club = matchingClubs[0]
    return render_template('welcome.html',club=club,competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClubs = [c for c in clubs if c['name'] == club]
    foundCompetitions = [c for c in competitions if c['name'] == competition]
    if foundClubs and foundCompetitions:
        return render_template('booking.html',club=foundClubs[0],competition=foundCompetitions[0])
    else:
        flash("Something went wrong-please try again")
        if foundClubs:
            return render_template('welcome.html', club=foundClubs[0], competitions=competitions)
        return redirect(url_for('index'))


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    foundCompetitions = [c for c in competitions if c['name'] == request.form.get('competition')]
    foundClubs = [c for c in clubs if c['name'] == request.form.get('club')]
    if not foundCompetitions or not foundClubs:
        flash("Something went wrong-please try again")
        return redirect(url_for('index'))
    competition = foundCompetitions[0]
    club = foundClubs[0]
    try:
        placesRequired = int(request.form.get('places', ''))
    except ValueError:
        flash("Please enter a valid number of places.")
        return render_template('booking.html', club=club, competition=competition)
    if placesRequired > int(club['points']):
        flash("You don't have enough points to book that many places.")
        return render_template('booking.html', club=club, competition=competition)
    competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
    club['points'] = int(club['points'])-placesRequired
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))