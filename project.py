#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for, flash,jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item
app = Flask(__name__)


engine = create_engine('sqlite:///categoryitem.db',connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
def HelloWorld():
    categories = session.query(Category).all()
    items = session.query(Item).join(Category).order_by(Item.id.desc()).limit(5)
    return render_template('home.html', categories=categories, items=items)
        
@app.route('/catalog/<int:category_id>/items/')
def categoryList(category_id):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category.id)
    itemscount = session.query(Item).filter_by(category_id=category.id).count()
    return render_template('category.html', categories=categories,category=category, items = items, itemcount=itemscount)


@app.route('/catalog/<int:category_id>/items/JSON')
def CategoryListJSON(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category.id)
    return jsonify(Item=[i.serialize for i in items])

@app.route('/catalog.json')
def ListJSON():
    items = session.query(Item).all()
    return jsonify(Item=[i.serialize for i in items])


@app.route('/catalog/<int:category_id>/<int:item_id>/')
def itemList(category_id,item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    return render_template('item.html', item = item)


# Task 1: Create route for newItem function here
@app.route('/catalog/items/new/',methods=['GET', 'POST'])
def newItem():
    categories = session.query(Category).all()
    if request.method == 'POST':
        newItem = Item(name=request.form['name'], description=request.form['description'],category_id=request.form['category'])
        session.add(newItem)
        session.commit()
        flash('New item created!')
        return redirect(url_for('HelloWorld'))
    else:
        return render_template('newitem.html', categories=categories)

# Task 2: Create route for editMenuItem function here

@app.route('/catalog/items/<int:item_id>/edit/',methods=['GET', 'POST'])
def editItem(item_id):
    categories = session.query(Category).all()
    editedItem = session.query(Item).filter_by(id=item_id).one()
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
        return redirect(url_for('categoryList', category_id=editedItem.category_id))
    else:
        # USE THE RENDER_TEMPLATE FUNCTION BELOW TO SEE THE VARIABLES YOU
        # SHOULD USE IN YOUR EDITMENUITEM TEMPLATE
        return render_template(
            'edititem.html', item=editedItem, categories=categories)
    
# Task 3: Create a route for deleteMenuItem function here

@app.route('/catalog/<int:category_id>/<int:item_id>/delete/',methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    deletedItem = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        session.delete(deletedItem)
        session.commit()
        flash('Item deleted!')
        return redirect(url_for('categoryList', category_id=category_id))
    else:
        # USE THE RENDER_TEMPLATE FUNCTION BELOW TO SEE THE VARIABLES YOU
        # SHOULD USE IN YOUR EDITMENUITEM TEMPLATE
        return render_template(
            'deleteitem.html', item=deletedItem)


if __name__ == '__main__':
    app.secret_key = 'super_secret_code'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)