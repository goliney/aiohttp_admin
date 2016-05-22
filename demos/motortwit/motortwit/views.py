import aiohttp_jinja2
import trafaret as t

from aiohttp import web
from aiohttp_session import get_session
from bson import ObjectId
from .security import check_password_hash, generate_password_hash
from .utils import redirect_response


RegisterValidator = t.Dict({
    t.Key("username"): t.String(max_length=30),
    t.Key("email"): t.Email,
    t.Key("password"): t.String,
    t.Key("password2"): t.String,
})


class SiteHandler:

    def __init__(self, mongo):
        self._mongo = mongo

    @property
    def mongo(self):
        return self._mongo

    @aiohttp_jinja2.template('timeline.html')
    async def timeline(self, request):
        session = await get_session(request)
        user_id = session.get('user_id')

        if user_id is None:
            return redirect_response(request, 'public_timeline')

        query = {'who_id': ObjectId(user_id)}
        filter = {'whom_id': 1}
        followed = await self.mongo.follower.find_one(query, filter)
        if followed is None:
            followed = {'whom_id': []}

        query = {'$or': [{'author_id': ObjectId(user_id)},
                         {'author_id': {'$in': followed['whom_id']}}]}
        messages = self.mongo.message.find(query).sort('pub_date', -1)
        endpoint = request.match_info.route.name
        return {"messages": messages,
                "endpoint": endpoint}

    @aiohttp_jinja2.template('timeline.html')
    async def public_timeline(self, request):
        messages = await (self.mongo.message
                          .find()
                          .sort('pub_date', -1)
                          .to_list(30))
        return {"messages": messages,
                "endpoint": request.match_info.route.name}

    @aiohttp_jinja2.template('timeline.html')
    async def user_timeline(self, request):
        username = request.match_info['username']
        profile_user = await self.mongo.user.find_one({'username': username})
        if profile_user is None:
            raise web.HTTPNotFound()
        followed = False
        session = await get_session(request)
        user_id = session.get('user_id')
        if user_id:
            followed = await self.mongo.follower.find_one(
                {'who_id': ObjectId(session['user_id']),
                 'whom_id': {'$in': [ObjectId(profile_user['_id'])]}}) is not None

        messages = await (self.mongo.message.find({'author_id': ObjectId(profile_user['_id'])})
                          .sort('pub_date', -1)
                          .to_list(30))

        return {"messages": messages,
                "followed": followed,
                "profile_user": profile_user}



#@app.route('/<username>')
#def user_timeline(username):
#    """Display's a users tweets."""
#    profile_user = mongo.db.user.find_one({'username': username})
#    if profile_user is None:
#        abort(404)
#    followed = False
#    if g.user:
#        followed = mongo.db.follower.find_one(
#            {'who_id': ObjectId(session['user_id']),
#             'whom_id': {'$in': [ObjectId(profile_user['_id'])]}}) is not None
#    messages = mongo.db.message.find(
#        {'author_id': ObjectId(profile_user['_id'])}).sort('pub_date', -1)
#    return render_template('timeline.html', messages=messages,
#                           followed=followed, profile_user=profile_user)

#@app.route('/login', methods=['GET', 'POST'])
#def login():
#    """Logs the user in."""
#    if g.user:
#        return redirect(url_for('timeline'))
#    error = None
#    if request.method == 'POST':
#        user = mongo.db.user.find_one({'username': request.form['username']})
#        if user is None:
#            error = 'Invalid username'
#        elif not check_password_hash(user['pw_hash'], request.form['password']):
#            error = 'Invalid password'
#        else:
#            flash('You were logged in')
#            session['user_id'] = str(user['_id'])
#            return redirect(url_for('timeline'))
#    return render_template('login.html', error=error)

    @aiohttp_jinja2.template('login.html')
    async def login(self, request):
        session = await get_session(request)
        user_id = session.get('user_id')
        if user_id is not None:
            return redirect_response(request, 'timeline')

        error = None
        if request.method == "post":
            form = await request.post()
            query = {'username': request.form['username']}
            user = await self.mongo.user.find_one(query)
            if user is None:
                error = 'Invalid username'
            elif not check_password_hash(user['pw_hash'], form['password']):
                error = 'Invalid password'
            else:
                session['user_id'] = str(user['_id'])
                return redirect_response(request, 'timeline')
        return {"error": error, "form": form}

    @aiohttp_jinja2.template('timeline.html')
    async def logout(self, request):
        session = await get_session(request)
        session.pop('user_id', None)
        return redirect_response(request, 'public_timeline')

    @aiohttp_jinja2.template('register.html')
    async def register(self, request):
        session = await get_session(request)
        user_id = session.get('user_id')
        if user_id is not None:
            return redirect_response(request, 'timeline')

        if request.method == "post":
            form = await request.post()
            form = RegisterValidator(form)
            pw_hash = generate_password_hash(form['password'])
            query = {'username': form['username'],
                     'email': form['email'],
                     'pw_hash': pw_hash}
            await self.mongo.user.insert(query)
            return redirect_response(request, 'login')

        return {"error": "error", "form": form}

#@app.route('/register', methods=['GET', 'POST'])
#def register():
#    """Registers the user."""
#    if g.user:
#        return redirect(url_for('timeline'))
#    error = None
#    if request.method == 'POST':
#        if not request.form['username']:
#            error = 'You have to enter a username'
#        elif not request.form['email'] or '@' not in request.form['email']:
#            error = 'You have to enter a valid email address'
#        elif not request.form['password']:
#            error = 'You have to enter a password'
#        elif request.form['password'] != request.form['password2']:
#            error = 'The two passwords do not match'
#        elif get_user_id(request.form['username']) is not None:
#            error = 'The username is already taken'
#        else:
#            mongo.db.user.insert(
#                {'username': request.form['username'],
#                 'email': request.form['email'],
#                 'pw_hash': generate_password_hash(request.form['password'])})
#            flash('You were successfully registered and can login now')
#            return redirect(url_for('login'))
#    return render_template('register.html', error=error)


#import datetime
#from hashlib import md5
#
#import pytz
#
## create our little application :)
#app = Flask(__name__)
#
## setup mongodb
#mongo = PyMongo(app)
#
## Load default config and override config from an environment variable
#app.config.update(dict(
#    DEBUG=True,
#    SECRET_KEY='development key'))
#app.config.from_envvar('MINITWIT_SETTINGS', silent=True)
#
#
#
#
#def format_datetime(timestamp):
#    """Format a timestamp for display."""
#    return timestamp.replace(tzinfo=pytz.utc).strftime('%Y-%m-%d @ %H:%M')
#
#
#
#
#
#
## add some filters to jinja
#import datetime
#from hashlib import md5
#
#import pytz
#from flask import Flask, request, session, url_for, redirect, \
#    render_template, abort, g, flash
#from werkzeug.security import check_password_hash, generate_password_hash
#from flask.ext.pymongo import PyMongo
#from bson.objectid import ObjectId
#
#
#@app.route('/<username>/follow')
#def follow_user(username):
#    """Adds the current user as follower of the given user."""
#    if not g.user:
#        abort(401)
#    whom_id = get_user_id(username)
#    if whom_id is None:
#        abort(404)
#    mongo.db.follower.update(
#        {'who_id': ObjectId(session['user_id'])},
#        {'$push': {'whom_id': whom_id}}, upsert=True)
#    flash('You are now following "%s"' % username)
#    return redirect(url_for('user_timeline', username=username))
#
#
#@app.route('/<username>/unfollow')
#def unfollow_user(username):
#    """Removes the current user as follower of the given user."""
#    if not g.user:
#        abort(401)
#    whom_id = get_user_id(username)
#    if whom_id is None:
#        abort(404)
#    mongo.db.follower.update(
#        {'who_id': ObjectId(session['user_id'])},
#        {'$pull': {'whom_id': whom_id}})
#    flash('You are no longer following "%s"' % username)
#    return redirect(url_for('user_timeline', username=username))
#
#
#@app.route('/add_message', methods=['POST'])
#def add_message():
#    """Registers a new message for the user."""
#    if 'user_id' not in session:
#        abort(401)
#    if request.form['text']:
#        user = mongo.db.user.find_one(
#            {'_id': ObjectId(session['user_id'])}, {'email': 1, 'username': 1})
#        mongo.db.message.insert(
#            {'author_id': ObjectId(session['user_id']),
#             'email': user['email'],
#             'username': user['username'],
#             'text': request.form['text'],
#             'pub_date': datetime.datetime.utcnow()})
#        flash('Your message was recorded')
#    return redirect(url_for('timeline'))
#
#
#@app.route('/register', methods=['GET', 'POST'])
#def register():
#    """Registers the user."""
#    if g.user:
#        return redirect(url_for('timeline'))
#    error = None
#    if request.method == 'POST':
#        if not request.form['username']:
#            error = 'You have to enter a username'
#        elif not request.form['email'] or '@' not in request.form['email']:
#            error = 'You have to enter a valid email address'
#        elif not request.form['password']:
#            error = 'You have to enter a password'
#        elif request.form['password'] != request.form['password2']:
#            error = 'The two passwords do not match'
#        elif get_user_id(request.form['username']) is not None:
#            error = 'The username is already taken'
#        else:
#            mongo.db.user.insert(
#                {'username': request.form['username'],
#                 'email': request.form['email'],
#                 'pw_hash': generate_password_hash(request.form['password'])})
#            flash('You were successfully registered and can login now')
#            return redirect(url_for('login'))
#    return render_template('register.html', error=error)
