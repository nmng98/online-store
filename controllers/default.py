# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------


def index():
	
	db.product.id.readable = False
	grid = SQLFORM.grid(db.product,
        create=False, editable=True, searchable=False
    )
	return dict(grid=grid)


def store():
    """Returns the store page, with the list of products to be bought"""
    query = db.product
    links = []
    if auth.user is not None:
    	links.append(
        	dict(header = 'Buy', body = lambda row: 
         	   A('', _class = 'fa fa-shopping-cart', _href = URL('default', 'create_order', 
            	args = [row.id], user_signature = True))

        	)
    	)
    db.product.id.readable = False
    grid = SQLFORM.grid(
        query,
        field_id = db.product.id,
        fields = [db.product.title, db.product.quantity, 
        db.product.price],
        details = False,
        links = links,
        create = True,
        editable = True, deletable = True, # do not need delete or edit later
        csv = False,
        searchable = False,
        user_signature = True
    )
    

    return dict(grid=grid)


@auth.requires_login()
def create_order():
    product = db.product(request.args(0))
    orders = db.orders(request.args(0))

    profile = db(db.profile.email == auth.user.email).select().first()

    # cannot not redirect to create profile if none
    if profile is None:
			redirect(URL('default', 'profile',
					vars=dict(next=URL('default', 'create_order', args=[product.id]),
				    	edit='y')))
    # Ok, here you know the profile exists.
    # Sets the default for the order to be created. 
    db.orders.product_id.default = product.id
    db.orders.orders_user.default = auth.user.email
    db.orders.orders_date.default = datetime.datetime.utcnow()

    form = SQLFORM(db.orders)
    if form.process(onvalidation=mychecks).accepted:
		redirect(URL('default', 'store'))


    return dict(title= product.title, form = form)

def mychecks(form):
	"""Performs form validation.  
	See http://www.web2py.com/books/default/chapter/29/07/forms-and-validators#onvalidation 
    for details."""
	product = db.product(request.args(0))

	if form.vars.orders_quantity > product.quantity:
		form.errors.orders_quantity = "I am sorry but %d is more than product's quantity " % form.vars.orders_quantity

	if form.vars.orders_quantity < 0:
		form.errors.orders_quantity = "I am sorry but %d is less than product's quantity " % form.vars.orders_quantity

	if form.vars.orders_quantity == 0:
		form.errors.orders_quantity = "I am sorry but you cannot order 0 items "


@auth.requires_login()
def profile():
	profile = db.profile(request.args(0))
	
	db.profile.id.readable = False
	
	user_email = request.vars.email or auth.user.email

	pro = db(db.profile.email == user_email).select().first()

	if request.vars.edit == 'y':
        
        # create
		if pro is None: 

			form = SQLFORM(db.profile,  pro)
			if form.process().accepted: # process form after either if statement executes
				redirect(request.vars.next or URL('default', 'profile'))
        

		profile = db.profile(request.user_email)

		if pro is not None: 
            
			form = SQLFORM(db.profile, pro) 
			if form.process().accepted: # process form after either if statement executes
                # form.update_record()
				redirect(request.vars.next or URL('default', 'profile'))

    # view

	else:
		if db.profile.email == auth.user.email:
			form = SQLFORM(db.profile, pro, readonly = True)
	
	return dict(form=form)



@auth.requires_login()
def order_list(): # completed for now??? 
   
    """Page to display the list of orders."""
    # Fixes visualization of email and product.  I hope this works, it should give you the idea at least.
    #db.product_order.user_email.represent = lambda v, r : A(v, _href=URL('default', 'profile', vars=dict(email=v)))
    #db.product_order.product_id.represent = lambda v, r : A(get_name(db.product(v)), _href=URL('default', 'view_product', args=[v]))
    db.orders.orders_user.represent = lambda v, r : A(v, _href=URL('default', 'profile', vars=dict(email=v)))
    db.orders.product_id.represent = lambda v, r : A(get_name(db.product(v)), _href=URL('default', 'view_product', args=[v]))
    db.orders.id.readable = False


    rows = db().select(db.orders.orders_user, db.orders.product_id, db.orders.orders_quantity)
    # ADD DECREASE QUANTITY
    return dict(rows = rows)

def view_product():
    """Controller to view a product."""
    p = db.product(request.args(0))
    if p is None:
        form = P('No such product')
    else:
    	db.product.id.readable = False
        form = SQLFORM(db.product, p, readonly=True)

    return dict(form=form)



def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


