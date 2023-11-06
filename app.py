from flask import Flask,render_template,json,request,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text,ForeignKey


import json 

app = Flask(__name__,template_folder='template//owner')
app.config['SQLALCHEMY_DATABASE_URI']   ='mysql+pymysql://root:root@localhost/FYP'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class categories(db.Model):
    __tablename__ = 'categories'
    category_id = db.Column(db.Integer,primary_key =True, autoincrement = True)
    category_name = db.column(db.String(30))
    categoryyy = db.relationship('product',backref = 'categories',lazy = 'select')
    def __repr__(self) ->str:
        return f"{self.category_name}"
class product(db.Model):
    __tablename__ = 'product'
    product_id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(50))
    price = db.Column(db.Integer)
    stock = db.Column(db.Integer)
    description = db.Column(db.String(255))
    category = db.Column(db.Integer,db.ForeignKey(categories.category_id))
    def __repr__(self) ->str:
        return f"{self.name}"
@app.route('/')
def hello():
    #yearly statistics
    #total orders
    query = text("select count(*) from orders")
    res = db.session.execute(query)
    total_years_orders = res.scalar()

    #returned orders
    query = text("select count(*) from orders where status = 'returned'")
    res = db.session.execute(query)
    total_returned_orders = res.scalar()

    #pending orders
    query = text("select count(*) from orders where status = 'pending'")
    res = db.session.execute(query)
    total_pending_orders = res.scalar()

    #total sales
    query = text("select SUM(amount) from orders where status = 'received'")
    res = db.session.execute(query)
    total_sales = res.scalar()

    #today statistices
     #total orders
    query = text("select count(*) from orders where DATE(orderDate) = CURDATE()")
    res = db.session.execute(query)
    total_today_orders = res.scalar()

    #returned orders
    query = text("select count(*) from orders where status = 'returned' and DATE(orderDate) = CURDATE()")
    res = db.session.execute(query)
    today_returned_orders = res.scalar()

    #pending orders
    query = text("select count(*) from orders where status = 'pending' and DATE(orderDate) = CURDATE()")
    res = db.session.execute(query)
    today_pending_orders = res.scalar()

    #total sales
    query = text("select SUM(amount) from orders where status = 'received' and DATE(orderDate) = CURDATE()")
    res = db.session.execute(query)
    today_sales = res.scalar()


    #no of orders
    query  =text("SELECT EXTRACT(MONTH FROM orderDate) AS month, COUNT(*) AS total_orders FROM orders GROUP BY EXTRACT(MONTH FROM orderDate)ORDER BY month")
    res = db.session.execute(query)
    rows = res.fetchall()
    monthly_orders = [0] * 12

    for row in rows:
        index = int((row.month) -1)
        monthly_orders[index] = row.total_orders
    monthly_orders_json = json.dumps(monthly_orders)

    #total sales
    query  =text("SELECT EXTRACT(MONTH FROM orderDate) AS month, CAST(SUM(amount) AS SIGNED) AS total_sales FROM orders GROUP BY EXTRACT(MONTH FROM orderDate) ORDER BY month")
    res = db.session.execute(query)
    rows = res.fetchall()
    monthly_sales = [0] * 12
    for row in rows:
            index = int((row.month) -1)
            if row.total_sales == None:
                monthly_sales[index] = 0
            else:
                monthly_sales[index] = row.total_sales 
    print(monthly_sales)   
    monthly_sales_json = json.dumps(monthly_sales)

    #pie chart for most orderd categories
    query = text("select product.category as category,CAST(sum(order_items.quantity) AS signed) AS total from order_items join product on order_items.product_id = product.product_id group by product.category")
    res = db.session.execute(query)
    rows = res.fetchall()
    category_order = {}
    for row in rows:
            category_order[row.category] = row.total
   
    return render_template('abc.html',monthly_sales = monthly_sales_json,today_sales=today_sales,today_returned_orders=today_returned_orders,today_pending_orders=today_pending_orders,total_today_orders=total_today_orders,total_sales=total_sales,total_pending_orders=total_pending_orders,monthly_orders = monthly_orders_json,total_years_orders=total_years_orders,total_returned_orders=total_returned_orders)
   
@app.route('/stats')
def stats():
    #city customers
    query = text("select customer.city as city,cast(sum(orders.amount) as signed) as city_total from customer join orders on customer.customer_id = orders.customer_id group by city order by city_total desc limit 5")
    res = db.session.execute(query)
    rows = res.fetchall()
    city ={}
    for row in rows:
        city[row.city] = row.city_total
    
    #total customers
    query = text("select count(*) from customer")
    res = db.session.execute(query)
    total_customers = res.scalar()

    #customers per month
    query = text("select count(customer_id) as no_of_customer,EXTRACT(MONTH FROM Date) AS month from customer GROUP BY EXTRACT(MONTH FROM Date) ORDER BY month")
    res = db.session.execute(query)
    rows = res.fetchall()
    cus_per_month = [0] *12
    for row in rows:
        if row.month != None:
            index = int((row.month) -1)
            cus_per_month[index] = row.no_of_customer
    print(cus_per_month)
    cus_per_month_json = json.dumps(cus_per_month)
    return render_template('statistics.html',city = city,total_customers=total_customers, cus_per_month= cus_per_month_json)
#productDetails page
@app.route('/products')
def products():
    #products = db.product.query.all()
    query  =text("select *from product")
    res = db.session.execute(query)
    products = res.fetchall()
    return render_template('productPage.html' , products = products,product = None)

#open add new product page
@app.route('/addproduct',methods=['Get','Post'])
def addproductpage():
    return render_template('addproduct.html')

#adding new product into database
@app.route('/form_add_product',methods = ['Get','Post'])
def addproduct():
    if request.method == 'POST':
        product_id = 'clo_120'
        name = request.form['name']
        price = request.form['price']
        stock = request.form['stock']
        desc = request.form['desc']
        category = request.form['category']
        print(category)
        if category == 'Cloth':
            category_id  = 1
        elif category == 'Unstitched':
            category_id =2
        elif category == 'Shoes':
            category_id = 3
        new_product = product(
            product_id=product_id,
            name=name,
            price=price,
            stock=stock,
            description=desc,
            category=category_id
        )
        db.session.add(new_product)
        db.session.commit()
        return "product added successfully"
    return 'nos'


#search product
@app.route('/searchpro',methods=['Get','Post'])
def searchproduct():
    if request.method == 'POST':
        pro = request.form['searchpro']
        query = text("select * from product where product_id = :pro OR name = :pro ")
        res = db.session.execute(query,{"pro":pro})
        rows = res.fetchall()
    return render_template('productPage.html',products = rows)


#orderdetails page
@app.route('/orders')
def orders():
    query = text("select * from orders")
    res= db.session.execute(query)
    orders =  res.fetchall()
    return render_template('ordersPage.html',orders = orders)

#search order
@app.route('/searchorder',methods=['Get','Post'])
def searchorder():
    if request.method == 'POST':
        order = request.form['searchorder']
        query = text("select * from orders where order_id = :order")
        res = db.session.execute(query,{"order":order})
        rows = res.fetchall()
    return render_template('ordersPage.html',orders = rows)
#cusromer details page
@app.route('/customers')
def customers():
    query = text("select * from customer")
    res= db.session.execute(query)
    customers =  res.fetchall()
    return render_template('customerPage.html',customers = customers)

#search customer
@app.route('/searchcustomer',methods=['Get','Post'])
def searchcustomer():
    if request.method == 'POST':
        cust = request.form['searchcust']
        query = text("select * from customer where customer_id = :cust OR first_name like CONCAT('%', :cust, '%') OR last_name like CONCAT('%', :cust, '%') ")
        res = db.session.execute(query,{"cust":cust})
        rows = res.fetchall()
    return render_template('customerPage.html',customers = rows)
if __name__ == "__main__":
    app.run(debug=True)

