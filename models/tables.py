
import datetime

def get_current_time():
    return datetime.datetime.utcnow()

def get_user_email():
    return None if auth.user is None else auth.user.email

db.define_table('product',
    Field('product_name', 'string'),
    Field('product_quantity', 'integer'),
    Field('sales_price', 'float'),
)

db.product.product_quantity.requires = IS_INT_IN_RANGE(1, 1000)
db.product.sales_price.requires = IS_FLOAT_IN_RANGE(0,1000)

def get_product_name(p):
    return None if p is None else p.product_name

def get_profile_name(pro):
    return None if pro is None else pro.profile_name

db.define_table('profile',
    Field('profile_email', default=get_user_email()),
    Field('profile_name', 'string'),
    Field('profile_street', 'string'),
    Field('profile_city', 'string'),
    Field('profile_zip', 'string')
)


db.profile.profile_city.writable = True

db.profile.profile_name.writable = True
db.profile.profile_name.readable = True

db.profile.profile_email.readable = True
db.profile.profile_email.writable = False

db.define_table('orders',
    Field('orders_user', 'string', 'reference profile'),
    Field('product_id', 'string', 'reference product'), # toggle star
    Field('orders_quantity', 'integer'),
    Field('orders_date'),
    Field('orders_paid', 'float')
)
db.orders.orders_user.readable = False
db.orders.orders_user.writable = False


# product = db((db.product.product_quantity == db.orders.orders_quantity)).select().first()
# db.orders.orders_quantity.requires = IS_INT_IN_RANGE(1, product.product_quantity)

db.orders.product_id.readable = False
db.orders.product_id.writable = False

db.orders.orders_user.readable = False

db.orders.orders_date.readable = False
db.orders.orders_date.writable = False

db.orders.orders_paid.writable = False

# db.orders.orders_paid.requires = IS_FLOAT_IN_RANGE(
    # db.product.sales_price * db.orders.orders_quantity)



# after defining tables, uncomment below to enable auditing
auth.enable_record_versioning(db)

