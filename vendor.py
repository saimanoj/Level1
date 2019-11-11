from flask import (Flask,
                   render_template,
                   request,
                   redirect,
                   jsonify,
                   url_for)
from flask import make_response, flash
from flask import session as login_session

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from functools import wraps

from db_setup import Base, User, Item

import json
import requests
import random
import string


app = Flask(__name__)

engine = create_engine('sqlite:///fm.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


def login_required(f):
    '''checks if user is loggedin or not'''
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in login_session:
            return f(*args, **kwargs)
        else:
            flash("You are not allowed to access there")
            return redirect('/login')
    return decorated_function

@app.route('/login')
@app.route('/')
def showLogin():
    ''' page to login'''
    if 'username' in login_session:
        return redirect(url_for('showVendor', vendor_id = login_session['user_id']))
    else:
        return render_template('login.html')

@app.route('/verifyLogin', methods=['GET','POST'])
def verifyLogin():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    user_data = json.loads(request.data)
    print user_data['user_name']
    user_pass = session.query(User).filter_by(user_name=user_data['user_name']).one()
    print user_pass.pass_word
    print user_data['password']

    if user_pass.pass_word == user_data['password']:
        login_session['username'] = user_data['user_name']
        login_session['user_id'] = user_pass.id

        output = {'login': 'pass'}

        flash("you are now logged in as %s" % user_data['user_name'])
    else:
        output = {'login': 'fail'}
    return output

@app.route('/logout', methods=['GET','POST'])
def logout():
    #login_session.pop('username', None)
    del login_session['username']
    del login_session['user_id']
    return redirect(url_for('showLogin'))

@login_required
@app.route('/vendor/<int:vendor_id>/')
def showVendor(vendor_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    vendor_items = session.query(Item).filter_by(user_id=vendor_id).all()
    return render_template('item.html', items=vendor_items, vendor=vendor_id)

@login_required
@app.route('/vendor/<int:vendor_id>/newItem', methods=['GET', 'POST'])
def newItem(vendor_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    user_id = login_session['user_id']

    if request.method == 'POST':
        newItem = Item(product_id=request.form['p_id'],
                       product_name=request.form['p_name'],
                       weave=request.form['weave'],
                       composition=request.form['composition'],
                       color=request.form['color'],
                       category_1=request.form['category1'],
                       category_2=request.form['category2'],
                       category_3=request.form['category3'],                       
                       user_id=vendor_id)
        session.add(newItem)
        session.commit()
        flash('%s Successfully Created' % (newItem.product_id))
        return redirect(url_for('showVendor', vendor_id=vendor_id))
    else:
        return render_template('item_new.html', vendor=vendor_id)

@login_required
@app.route('/itemEdit/<int:item_id>', methods=['GET', 'POST'])
def editItem(item_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    vendor_id = login_session['user_id']

    item = session.query(Item).filter_by(id=item_id).one()

    if item.user_id != vendor_id:
        flash('Item was created by another user and can only be edited by creator')  # NOQA
        return redirect(url_for('showVendor', vendor_id=vendor_id))

    if request.method == 'POST':
        item.product_id = request.form['p_id']
        item.product_name = request.form['p_name']
        item.weave = request.form['weave']
        item.composition = request.form['composition']
        item.color = request.form['color']
        item.category_1 = request.form['category1']
        item.category_2 = request.form['category2']
        item.category_3 = request.form['category3']
        session.add(item)
        session.commit()
        flash('%s Successfully Updated' % (item.product_id))
        return redirect(url_for('showVendor', vendor_id=vendor_id))
    else:
        return render_template('item_edit.html',
                               vendor=vendor_id,
                               item=item)    

@login_required
@app.route('/itemDelete/<int:item_id>', methods=['GET', 'POST'])
def deleteItem(item_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    vendor_id = login_session['user_id']

    item = session.query(Item).filter_by(id=item_id).one()
    if item.user_id != vendor_id:
        flash('Item was created by another user and can only be edited by creator')  # NOQA
        return redirect(url_for('showVendor', vendor_id=vendor_id))

    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash('%s Successfully Deleted' % (item.product_id))
        return {'deleted': 'pass'}
    else:
        return {'deleted': 'fail'}


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.run(host='0.0.0.0', port=5000)
