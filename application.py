# import
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash  # noqa
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Hotel, HotelInfo, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from functools import wraps

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secret.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Hotel Catalog Application"

# Connect to Database

engine = create_engine('sqlite:///hotelcatalogwithusers.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

# Login


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in login_session:
            return redirect(url_for('showLogin'))
        return f(*args, **kwargs)
    return decorated_function

# Create anti-forgery state token


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)

# Google connect


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps("Invalid state parameter."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps("Failed to upgrade the authorization code."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            "Current user is already connected."), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = width: 300px; height: 300px; border-radius: 150px;'
    output += '"style = -webkit-border-radius: 150px;'
    output += '"style = -moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output
# Google disconnect


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'get')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# User Helper Functions

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:  # noqa 722
        return None

# CRUD
# Show all hotels C(R)UD


@app.route('/')
@app.route('/hotel/')
def showHotels():
    hotels = session.query(Hotel).order_by(Hotel.name)
    if 'username' not in login_session:
        return render_template('publichotels.html', hotels=hotels)
    else:
        return render_template('hotels.html', hotels=hotels)

# Create a new hotel (C)RUD


@app.route('/hotel/new/', methods=['GET', 'POST'])
@login_required
def newHotel():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newHotel = Hotel(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newHotel)
        flash('New Hotel %s has been successfully created' % newHotel.name)
        session.commit()
        return redirect(url_for('showHotels'))
    else:
        return render_template('newhotel.html')

# Edit a hotel CR(U)D


@app.route('/hotel/<int:hotel_id>/edit/', methods=['GET', 'POST'])
@login_required
def editHotel(hotel_id):
    editedHotel = session.query(
        Hotel).filter_by(id=hotel_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedHotel.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this hotel. Please create your own hotel in order to edit.');}</script><body onload='myFunction()'>"  # noqa
    if request.method == 'POST':
        if request.form['name']:
            editedHotel.name = request.form['name']
            flash('%s Hotel has been successfully edited' % editedHotel.name)
            return redirect(url_for('showHotels'))
    else:
        return render_template('edithotel.html', hotel=editedHotel)

# Delete a hotel CRU(D)


@app.route('/hotel/<int:hotel_id>/delete/', methods=['GET', 'POST'])
@login_required
def deleteHotel(hotel_id):
    hotelToDelete = session.query(
        Hotel).filter_by(id=hotel_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if hotelToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this hotel. Please create your own hotel in order to delete.');}</script><body onload='myFunction()'>"  # noqa
    if request.method == 'POST':
        session.delete(hotelToDelete)
        flash('%s Hotel has been successfully deleted' % hotelToDelete.name)
        session.commit()
        return redirect(url_for('showHotels', hotel_id=hotel_id))
    else:
        return render_template('deletehotel.html', hotel=hotelToDelete)

# Show  Hotel's Information


@app.route('/hotel/<int:hotel_id>/')
@app.route('/hotel/<int:hotel_id>/info/')
def showInfo(hotel_id):
    hotel = session.query(Hotel).filter_by(id=hotel_id).one()
    creator = getUserInfo(hotel.user_id)
    info = session.query(HotelInfo).filter_by(
        hotel_id=hotel_id).all()
    if 'username' not in login_session:
        return render_template(
            'publicinfo.html', info=info, hotel=hotel, creator=creator)
    else:
        return render_template(
            'info.html', info=info, hotel=hotel, creator=creator)

# Create new Hotel Information


@app.route('/hotel/<int:hotel_id>/info/new/', methods=['GET', 'POST'])
@login_required
def newHotelInfo(hotel_id):
    hotel = session.query(Hotel).filter_by(id=hotel_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if login_session['user_id'] != hotel.user_id:
        return "<script>function myFunction() {alert('You are not authorized to add information to this hotel. Please create your own hotel in order to add information.');}</script><body onload='myFunction()'>"  # noqa
    if request.method == 'POST':
        newInfo = HotelInfo(name=request.form[
            'name'], description=request.form[
            'description'], price=request.form[
            'price'], category=request.form[
            'category'], hotel_id=hotel_id, user_id=hotel.user_id)
        session.add(newInfo)
        session.commit()
        flash('New Information %s of this Hotel has been successfully created' % (newInfo.name))  # noqa
        return redirect(url_for('showInfo', hotel_id=hotel_id))
    else:
        return render_template('newhotelinfo.html', hotel_id=hotel_id)

# Edit Hotel Information


@app.route('/hotel/<int:hotel_id>/info/<int:info_id>/edit', methods=['GET', 'POST'])  # noqa
@login_required
def editHotelInfo(hotel_id, info_id):
    editedInfo = session.query(HotelInfo).filter_by(id=info_id).one()
    hotel = session.query(Hotel).filter_by(id=hotel_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if login_session['user_id'] != hotel.user_id:
        return "<script>function myFunction() {alert('You are not authorized to edit information  to this hotel. Please create your own hotel in order to edit information.');}</script><body onload='myFunction()'>"  # noqa
    if request.method == 'POST':
        if request.form['name']:
            editedInfo.name = request.form['name']
        if request.form['description']:
            editedInfo.description = request.form['description']
        if request.form['price']:
            editedInfo.price = request.form['price']
        if request.form['category']:
            editedInfo.category = request.form['category']
        session.add(editedInfo)
        session.commit()
        flash('Hotel Info has been successfully edited')
        return redirect(url_for('showInfo', hotel_id=hotel_id))
    else:
        return render_template('edithotelinfo.html', hotel_id=hotel_id, info_id=info_id, info=editedInfo)  # noqa

# Delete a Hotel's information


@app.route('/hotel/<int:hotel_id>/info/<int:info_id>/delete', methods=['GET', 'POST'])  # noqa
@login_required
def deleteHotelInfo(hotel_id, info_id):
    hotel = session.query(Hotel).filter_by(id=hotel_id).one()
    info = session.query(HotelInfo).filter_by(id=info_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if login_session['user_id'] != hotel.user_id:
        return "<script>function myFunction() {alert('You are not authorized to delete information to this hotel. Please create your own hotel in order to delete information.');}</script><body onload='myFunction()'>"  # noqa
    if request.method == 'POST':
        session.delete(info)
        session.commit()
        flash('Hotel Information has been successfully deleted')
        return redirect(url_for(
            'showInfo', hotel_id=hotel_id, info_id=info_id))
    else:
        return render_template(
            'deletehotelinfo.html', hotel_id=hotel_id, info_id=info_id, hotel=hotel, info=info)  # noqa

# JSON APIs to view Hotel Information


@app.route('/hotel/<int:hotel_id>/info/JSON')
def hotelInfoJSON(hotel_id):
    hotel = session.query(Hotel).filter_by(id=hotel_id).one()
    info = session.query(HotelInfo).filter_by(hotel_id=hotel_id).all()
    return jsonify(HotelInfo=[i.serialize for i in info])


@app.route('/hotel/JSON')
def hotelsJSON():
    hotels = session.query(Hotel).all()
    return jsonify(hotels=[h.serialize for h in hotels])

# Disconnect


@app.route('/disconnect')
def disconnect():
    if 'username' in login_session:
        gdisconnect()
        del login_session['gplus_id']
        del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        flash("You have successfully been logged out.")
        return redirect(url_for('showHotels'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showHotels'))

# IMPORTANT Always at the end!!!


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
