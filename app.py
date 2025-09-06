
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session, redirect, url_for
from flask import request



app = Flask(__name__)
app.secret_key = '857546844878786476487864786447878474878475634643541324'

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy


# 📦 Подключение к SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 📚 Модель книги
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    short_desc = db.Column(db.Text, nullable=False)
    full_desc = db.Column(db.Text, nullable=False)
    pages = db.Column(db.Integer)
    year = db.Column(db.Integer)
    genre = db.Column(db.String(100))
    publisher = db.Column(db.String(100))
    image = db.Column(db.String(200))  # 🖼️ Ссылка на картинку

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default="customer")  # customer, manager, owner


@app.route('/')
def home():
    books = Book.query.all()
    return render_template('index.html', books=books)

@app.route('/catalog')
def catalog():
    books = Book.query.all()
    return render_template('Catalog.html', books=books)

@app.route('/about')
def about():
    return render_template('about.html', )
@app.route('/contacts')
def contacts():
    return render_template('contacts.html', )
@app.route('/cart')
def cart():
    return render_template('cart.html', )
@app.route('/profile')
def profile():
    return render_template('profile.html', )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            if user.role == 'manager':
                session['user_id'] = user.id
                session['username'] = user.username
                session['role'] = user.role
                return redirect('/dashboard')
            else:
                return "Доступ разрешен только менеджерам"
        else:
            return "Неверный логин или пароль"

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'role' in session and session['role'] == 'manager':
        return render_template('manager_panel.html')
    else:
        return redirect('/login')

@app.route('/manager', methods=['GET'])
def manager_panel():
    if 'role' not in session or session['role'] != 'manager':
        return abort(403)
    
    books = Book.query.all()
    return render_template('manager_panel.html', books=books)

# ✅ Добавление книги
@app.route('/manager/add', methods=['POST'])
def add_book():
    if 'role' not in session or session['role'] != 'manager':
        return abort(403)

    new_book = Book(
        code=request.form['code'],
        title=request.form['title'],
        author=request.form['author'],
        price=request.form['price'],
        short_desc=request.form['short_desc'],
        full_desc=request.form['full_desc'],
        pages=request.form.get('pages'),
        year=request.form.get('year'),
        genre=request.form.get('genre'),
        publisher=request.form.get('publisher'),
        image=request.form.get('image')
    )
    db.session.add(new_book)
    db.session.commit()
    return redirect('/manager')

# ✅ Удаление книги
@app.route('/manager/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    if 'role' not in session or session['role'] != 'manager':
        return abort(403)

    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return redirect('/manager')

# ✅ Выход из системы
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('book_detail.html', book=book)


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
         # Создаем менеджера, если нет
        if not User.query.filter_by(username="manager").first():
            from werkzeug.security import generate_password_hash
            manager = User(
                username="manager",
                password_hash=generate_password_hash("managerpass"),
                role="manager"
            )
            db.session.add(manager)
            db.session.commit()

    app.run(debug=True)

