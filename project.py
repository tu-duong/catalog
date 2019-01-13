#!/usr/bin/python3
### #!/usr/bin/env python3


from flask import Flask, render_template, request, redirect, url_for, flash,jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User

app = Flask(__name__)

from flask import session as login_session
import random, string

# IMPORTS FOR THIS STEP
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Application"

# Connect to Database and create database session
engine = create_engine('sqlite:///categoryitemwithusers.db',connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
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
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
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
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print ("done!")
    return output


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is %s', access_token)
    print('User name is: ')
    print(login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print (result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
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
    except:
        return None


@app.route('/')
def HelloWorld():
    categories = session.query(Category).all()
    items = session.query(Item).join(Category).order_by(Item.id.desc()).limit(5)
    if 'username' not in login_session:
        return render_template('publichome.html', categories=categories, items=items)
    else:
        return render_template('home.html', categories=categories, items=items)
        
@app.route('/catalog/<category_name>/items/')
def categoryList(category_name):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(category_id=category.id)
    itemscount = session.query(Item).filter_by(category_id=category.id).count()
    if 'username' not in login_session:
        isloggedin = 0
    else:
        isloggedin = 1

    return render_template('category.html', categories=categories,category=category, items = items, itemcount=itemscount, isloggedin = isloggedin)


@app.route('/catalog/<int:category_id>/items/JSON')
def CategoryListJSON(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category.id)
    return jsonify(Item=[i.serialize for i in items])

@app.route('/catalog.json')
def ListJSON():
    items = session.query(Item).all()
    return jsonify(Item=[i.serialize for i in items])


@app.route('/catalog/<category_name>/<item_name>/')
def itemList(category_name,item_name):
    #category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(Item).filter_by(name=item_name).one()
    creator = getUserInfo(item.user_id)
    if 'username' not in login_session:
        isloggedin = 0
    else:
        isloggedin = 1

    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('publicitem.html', item = item, isloggedin=isloggedin)
    else:
        return render_template('item.html', item = item, )

# Task 1: Create route for newItem function here
@app.route('/catalog/items/new/',methods=['GET', 'POST'])
def newItem():
    if 'username' not in login_session:
        return redirect('/login')
        
    categories = session.query(Category).all()
    if request.method == 'POST':
        newItem = Item(name=request.form['name'], description=request.form['description'],category_id=request.form['category'],user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('New item created!')
        return redirect(url_for('HelloWorld'))
    else:
        return render_template('newitem.html', categories=categories)

# Task 2: Create route for editMenuItem function here

@app.route('/catalog/items/<item_name>/edit/',methods=['GET', 'POST'])
def editItem(item_name):
    if 'username' not in login_session:
        return redirect('/login')
        
    categories = session.query(Category).all()
    editedItem = session.query(Item).filter_by(name=item_name).one()
    if login_session['user_id'] != editedItem.user_id:
        return "<script>function myFunction() {alert('You are not authorized to edit. You can only edit item you created.');}</script><body onload='myFunction()''>"

    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['new_category']:
            editedItem.category_id = request.form['new_category']
        session.add(editedItem)
        session.commit()
        flash('Item edited!')
        return redirect(url_for('categoryList', category_name=editedItem.category.name))
    else:
        # USE THE RENDER_TEMPLATE FUNCTION BELOW TO SEE THE VARIABLES YOU
        # SHOULD USE IN YOUR EDITMENUITEM TEMPLATE
        return render_template(
            'edititem.html', item=editedItem, categories=categories)
    
# Task 3: Create a route for deleteMenuItem function here

@app.route('/catalog/items/<item_name>/delete/',methods=['GET', 'POST'])
def deleteItem(item_name):
    if 'username' not in login_session:
        return redirect('/login')
    deletedItem = session.query(Item).filter_by(name=item_name).one()
    if login_session['user_id'] != deletedItem.user_id:
        return "<script>function myFunction() {alert('You are not authorized to delete. You can only delete item you created.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(deletedItem)
        session.commit()
        flash('Item deleted!')
        return redirect(url_for('categoryList', category_name=deletedItem.category_name))
    else:
        # USE THE RENDER_TEMPLATE FUNCTION BELOW TO SEE THE VARIABLES YOU
        # SHOULD USE IN YOUR EDITMENUITEM TEMPLATE
        return render_template(
            'deleteitem.html', item=deletedItem)


if __name__ == '__main__':
    app.secret_key = 'super_secret_code'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)