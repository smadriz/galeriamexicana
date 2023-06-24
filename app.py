from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm 
from wtforms import StringField, SubmitField, FloatField, FileField
from flask_wtf.csrf import CSRFProtect
import base64
from flask import send_file, abort
from io import BytesIO


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/santiago/Desktop/test.db'
app.config['SECRET_KEY'] = 'your-secret-key'

db = SQLAlchemy(app)
csrf = CSRFProtect(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.LargeBinary, nullable=False)

class ProductForm(FlaskForm):
    name = StringField('Name')
    description = StringField('Description')
    price = FloatField('Price')
    image = FileField('Image')
    submit = SubmitField('Submit')

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    form = ProductForm()
    if form.validate_on_submit():
        image_data = form.image.data.read()
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            image=image_data
        )
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('admin'))
    products = Product.query.all()
    return render_template('admin.html', form=form, products=products)

@app.route('/admin/delete/<int:id>', methods=['POST'])
@csrf.exempt
def delete_product(id):
    product = Product.query.get(id)
    if product:
        db.session.delete(product)
        db.session.commit()
    return redirect(url_for('admin'))

@app.route('/image/<int:product_id>')
def get_image(product_id):
    product = Product.query.get(product_id)
    if product:
        if product.image:
            image_data = BytesIO(product.image)
            return send_file(image_data, mimetype='image/jpeg')
        else:
            abort(404)
    else:
        abort(404)

@app.route('/')
def home():
    featured_products = Product.query.all()
    return render_template('home.html', featured_products=featured_products)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/shop', methods=['GET', 'POST'])
def shop():
    form = ProductForm()
    selected_products = []  # Agregar esta línea para asegurarse de que siempre haya una lista inicializada
    if request.method == 'POST':
        selected_products = request.form.getlist('selected_product')
        total = calculate_total(selected_products)
    else:
        total = 0
    return render_template('shop.html', products=Product.query.all(), selected_products=selected_products, total=total, form=form)



def calculate_total(selected_products):
    total = 0
    for product_id in selected_products:
        product = Product.query.get(product_id)
        if product:
            total += product.price
    return total

if __name__ == '__main__':
    app.run(debug=True)
