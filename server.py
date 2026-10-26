import json
from datetime import datetime
from flask import Flask,render_template,request,redirect,flash,url_for,session


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


def isPastCompetition(competition):
    competitionDate = datetime.strptime(competition['date'], '%Y-%m-%d %H:%M:%S')
    return competitionDate < datetime.now()


app = Flask(__name__)
app.secret_key = 'something_special'
app.jinja_env.globals['isPastCompetition'] = isPastCompetition

competitions = loadCompetitions()
clubs = loadClubs()

MAX_PLACES_PER_CLUB = 12
# Places already booked, keyed by (competition name, club name)
bookings = {}

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
    session['club'] = club['name']
    return render_template('welcome.html',club=club,competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition,club):
    if session.get('club') != club:
        flash("Please log in with your club's email to book places.")
        return redirect(url_for('index'))
    foundClubs = [c for c in clubs if c['name'] == club]
    foundCompetitions = [c for c in competitions if c['name'] == competition]
    if foundClubs and foundCompetitions and isPastCompetition(foundCompetitions[0]):
        flash("This competition has already taken place, booking is closed.")
        return render_template('welcome.html', club=foundClubs[0], competitions=competitions)
    if foundClubs and foundCompetitions:
        return render_template('booking.html',club=foundClubs[0],competition=foundCompetitions[0])
    else:
        flash("Something went wrong-please try again")
        if foundClubs:
            return render_template('welcome.html', club=foundClubs[0], competitions=competitions)
        return redirect(url_for('index'))


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    if session.get('club') != request.form.get('club'):
        flash("Please log in with your club's email to book places.")
        return redirect(url_for('index'))
    foundCompetitions = [c for c in competitions if c['name'] == request.form.get('competition')]
    foundClubs = [c for c in clubs if c['name'] == request.form.get('club')]
    if not foundCompetitions or not foundClubs:
        flash("Something went wrong-please try again")
        return redirect(url_for('index'))
    competition = foundCompetitions[0]
    club = foundClubs[0]
    if isPastCompetition(competition):
        flash("This competition has already taken place, booking is closed.")
        return render_template('welcome.html', club=club, competitions=competitions)
    try:
        placesRequired = int(request.form.get('places', ''))
    except ValueError:
        flash("Please enter a valid number of places.")
        return render_template('booking.html', club=club, competition=competition)
    if placesRequired <= 0:
        flash("Please enter a number of places greater than zero.")
        return render_template('booking.html', club=club, competition=competition)
    if placesRequired > int(competition['numberOfPlaces']):
        flash("Not enough places available in this competition.")
        return render_template('booking.html', club=club, competition=competition)
    if placesRequired > int(club['points']):
        flash("You don't have enough points to book that many places.")
        return render_template('booking.html', club=club, competition=competition)
    alreadyBooked = bookings.get((competition['name'], club['name']), 0)
    if alreadyBooked + placesRequired > MAX_PLACES_PER_CLUB:
        flash(f"You can't book more than {MAX_PLACES_PER_CLUB} places per competition "
              f"(already booked: {alreadyBooked}).")
        return render_template('booking.html', club=club, competition=competition)
    competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
    club['points'] = int(club['points'])-placesRequired
    bookings[(competition['name'], club['name'])] = alreadyBooked + placesRequired
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/pointsBoard')
def pointsBoard():
    return render_template('points.html', clubs=clubs)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))