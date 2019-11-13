from __future__ import division
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

from db_setup import Base, User, Item, Order, Product

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
            return redirect(url_for('showLogin'))
    return decorated_function

@app.route('/login')
@app.route('/vendor')
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

@app.route('/vendor/<int:vendor_id>/')
@login_required
def showVendor(vendor_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    vendor_items = session.query(Item).filter_by(user_id=vendor_id).all()
    return render_template('item.html', items=vendor_items, vendor=vendor_id)

@app.route('/vendor/<int:vendor_id>/newItem', methods=['GET', 'POST'])
@login_required
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

@app.route('/itemEdit/<int:item_id>', methods=['GET', 'POST'])
@login_required
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

@app.route('/itemDelete/<int:item_id>', methods=['GET', 'POST'])
@login_required
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

@app.route('/download/<int:vendor_id>/', methods=['GET','POST'])
@login_required
def downloadItem(vendor_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    vendor_items = session.query(Item).filter_by(user_id=vendor_id).all()
    data = 'Product ID,Product Name,Weave,Composition,Color,Category 1,Category 2,Category 3\n'
    for item in vendor_items:
        data += str(item.product_id)+','
        data += str(item.product_name)+','
        data += '"'+str(item.weave)+'",'
        data += '"'+str(item.composition)+'",'
        data += '"'+str(item.color)+'",'
        data += '"'+str(item.category_1)+'",'
        data += '"'+str(item.category_2)+'",'
        data += '"'+str(item.category_3)+'"'
        data += '\n'
    return {'download': 'pass', 'data' : data}

def minutesToText(mins):
    days = mins//1440
    hours = (mins - days*1440)//60
    minutes = mins - days*1440 - hours*60
    result = ("{0} day{1}".format(days, "s" if days!=1 else "") if days else "") + \
    (", {0} hour{1}".format(hours, "s" if hours!=1 else "") if hours else "") + \
    (", {0} minute{1}".format(minutes, "s" if minutes!=1 else "") if minutes else "")
    return result

@app.route('/orders')
def showOrders():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    order_items = session.query(Order).all()
    for order in order_items:
        r_distance = order.delivery_distance.split(' ')
        distance = int(r_distance[0])
        if r_distance[1] == 'm':
            distance /= 1000
        if distance > 2000:
            if distance > 5000:
                total_time = distance
            else:
                r_int = random.randint(0,100)
                if r_int%2 == 0:
                    total_time = distance
                else:
                    total_time = int((distance/5) * 60)
        elif distance < 2000:
            total_time = int((distance/5) * 60)
        order_type = order.order_type
        if order_type == 'swatch':
            total_time += (24*60)
        elif order_type == 'sample':
            total_time += (3*24*60)
        elif order_type == 'bulk':
            total_time += (15*24*60)
        order.delivery_time = minutesToText(total_time)
    return render_template('orders.html', items=order_items)

@app.route('/')
def product():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    product_items = session.query(Product).all()
    return render_template('product.html', items = product_items)

@app.route('/filter/<string:filter_key>', methods=['GET','POST'])
def filterProduct(filter_key):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    filter_key_split = filter_key.split('_')
    prod_filter = filter_key_split[0]
    filter_item = filter_key_split[1]
    print prod_filter
    print filter_item
    if prod_filter == 'comp':
        product_items = session.query(Product).filter(Product.composition.contains(filter_item)).all()
    elif prod_filter == 'color':
        product_items = session.query(Product).filter(Product.color.contains(filter_item)).all()
    elif prod_filter == 'pat':
        product_items = session.query(Product).filter(Product.pattern.contains(filter_item)).all()
    elif prod_filter == 'wev':
        product_items = session.query(Product).filter(Product.weave.contains(filter_item)).all()
    else:
        product_items = session.query(Product).all()

    return render_template('product.html', items = product_items)    

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.run(host='0.0.0.0', port=5000)
