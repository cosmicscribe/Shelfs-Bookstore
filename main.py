from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file, make_response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from models import db, User, Book, Order, OrderItem, Library, Review
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kitabghar-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kitabghar.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_folders():
    os.makedirs('static/uploads/books', exist_ok=True)
    os.makedirs('static/uploads/covers', exist_ok=True)

def create_demo_pdf():
    demo_pdf_path = 'static/uploads/books/demo.pdf'
    if not os.path.exists(demo_pdf_path):
        pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources 4 0 R /MediaBox [0 0 612 792] /Contents 5 0 R >>
endobj
4 0 obj
<< /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >>
endobj
5 0 obj
<< /Length 100 >>
stream
BT
/F1 24 Tf
100 700 Td
(KitabGhar Demo eBook) Tj
0 -30 Td
(This is a sample book for demonstration.) Tj
ET
endstream
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000214 00000 n 
0000000304 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
456
%%EOF"""
        with open(demo_pdf_path, 'wb') as f:
            f.write(pdf_content)
        print(f"Created demo PDF at {demo_pdf_path}")
    return demo_pdf_path

def seed_data():
    if User.query.count() == 0:
        admin = User(username='admin', email='admin@shelfs.com', role='Admin', phone='1234567890')
        admin.set_password('admin123')
        
        user = User(username='reader', email='reader@example.com', role='Customer', phone='9876543210')
        user.set_password('user123')
        
        db.session.add(admin)
        db.session.add(user)
        db.session.commit()
        print("Created test users (admin/admin123, reader/user123)")
    
    if Book.query.count() == 0:
        demo_pdf_path = create_demo_pdf()
        
        books = [
            Book(
                title='The Alchemist',
                author='Paulo Coelho',
                price=299.00,
                category='Fiction',
                cover_image='https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400&h=600&fit=crop',
                file_path=demo_pdf_path,
                tag='Shelfs Choice 🏆',
                stock=50
            ),
            Book(
                title='Atomic Habits',
                author='James Clear',
                price=399.00,
                category='Self-Help',
                cover_image='https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400&h=600&fit=crop',
                file_path=demo_pdf_path,
                tag='Best Seller 🔥',
                stock=22
            ),
            Book(
                title='Sapiens',
                author='Yuval Noah Harari',
                price=499.00,
                category='History',
                cover_image='https://images.unsplash.com/photo-1589998059171-988d887df646?w=400&h=600&fit=crop',
                file_path=demo_pdf_path,
                tag='Limited Edition 💎',
                stock=35
            ),
            Book(
                title='Clean Code',
                author='Robert C. Martin',
                price=599.00,
                category='Technology',
                cover_image='https://images.unsplash.com/photo-1532012197267-da84d127e765?w=400&h=600&fit=crop',
                file_path=demo_pdf_path,
                stock=40
            ),
            Book(
                title='The Psychology of Money',
                author='Morgan Housel',
                price=349.00,
                category='Finance',
                cover_image='https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?w=400&h=600&fit=crop',
                file_path=demo_pdf_path,
                tag='Best Seller 🔥',
                stock=25
            ),
            Book(
                title='Educated',
                author='Tara Westover',
                price=449.00,
                category='Biography',
                cover_image='https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=400&h=600&fit=crop',
                file_path=demo_pdf_path,
                stock=30
            ),
            Book(
                title='The Lean Startup',
                author='Eric Ries',
                price=549.00,
                category='Business',
                cover_image='https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=600&fit=crop',
                file_path=demo_pdf_path,
                tag='Shelfs Choice 🏆',
                stock=45
            ),
            Book(
                title='Thinking, Fast and Slow',
                author='Daniel Kahneman',
                price=599.00,
                category='Psychology',
                cover_image='https://images.unsplash.com/photo-1519682337058-a94d519337bc?w=400&h=600&fit=crop',
                file_path=demo_pdf_path,
                stock=20
            ),
            Book(
                title='The Power of Now',
                author='Eckhart Tolle',
                price=379.00,
                category='Spirituality',
                cover_image='https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=400&h=600&fit=crop',
                file_path=demo_pdf_path,
                stock=15
            ),
            Book(
                title='1984',
                author='George Orwell',
                price=329.00,
                category='Classic',
                cover_image='https://images.unsplash.com/photo-1541963463532-d68292c34b19?w=400&h=600&fit=crop',
                file_path=demo_pdf_path,
                tag='Limited Edition 💎',
                stock=18
            )
        ]
        
        for book in books:
            db.session.add(book)
        
        db.session.commit()
        print(f"Database seeded with {len(books)} books with varied stock levels and tags")

@app.route('/')
def index():
    query = Book.query
    
    search_term = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    
    if search_term:
        query = query.filter(
            db.or_(
                Book.title.ilike(f'%{search_term}%'),
                Book.author.ilike(f'%{search_term}%')
            )
        )
    
    if category:
        query = query.filter(Book.category.ilike(f'%{category}%'))
    
    books = query.all()
    categories = db.session.query(Book.category).distinct().filter(Book.category.isnot(None)).order_by(Book.category).all()
    categories = [cat[0] for cat in categories]
    
    return render_template('store.html', books=books, categories=categories)

@app.route('/search')
def search():
    category = request.args.get('category', '')
    author = request.args.get('author', '')
    
    query = Book.query
    
    if category:
        query = query.filter(Book.category.ilike(f'%{category}%'))
    if author:
        query = query.filter(Book.author.ilike(f'%{author}%'))
    
    books = query.all()
    categories = db.session.query(Book.category).distinct().filter(Book.category.isnot(None)).order_by(Book.category).all()
    categories = [cat[0] for cat in categories]
    return render_template('store.html', books=books, categories=categories, search_category=category, search_author=author)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            if user.is_admin():
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone', '')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
        
        user = User(username=username, email=email, role='Customer', phone=phone)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/cart')
@login_required
def cart():
    cart_items = session.get('cart', [])
    cart_books = []
    total = 0
    
    for item in cart_items:
        book = Book.query.get(item['book_id'])
        if book:
            quantity = item.get('quantity', 1)
            row_total = book.price * quantity
            cart_books.append({
                'book': book,
                'quantity': quantity,
                'row_total': row_total
            })
            total += row_total
    
    return render_template('cart.html', cart_books=cart_books, total=total)

@app.route('/add-to-cart/<int:book_id>')
@login_required
def add_to_cart(book_id):
    if current_user.is_admin():
        flash('Admins cannot purchase books', 'error')
        return redirect(url_for('index'))
    
    book = Book.query.get_or_404(book_id)
    
    existing = Library.query.filter_by(user_id=current_user.id, book_id=book_id).first()
    if existing:
        flash('You already own this book!', 'info')
        return redirect(url_for('index'))
    
    cart = session.get('cart', [])
    
    existing_item = next((item for item in cart if item['book_id'] == book_id), None)
    
    if existing_item:
        if existing_item['quantity'] >= book.stock:
            flash(f'Cannot add more! Only {book.stock} copies available.', 'error')
        else:
            existing_item['quantity'] += 1
            session['cart'] = cart
            flash(f'{book.title} quantity increased to {existing_item["quantity"]}!', 'success')
    else:
        cart.append({'book_id': book_id, 'quantity': 1})
        session['cart'] = cart
        flash(f'{book.title} added to cart!', 'success')
    
    return redirect(url_for('index'))

@app.route('/remove-from-cart/<int:book_id>')
@login_required
def remove_from_cart(book_id):
    cart = session.get('cart', [])
    cart = [item for item in cart if item['book_id'] != book_id]
    session['cart'] = cart
    flash('Item removed from cart', 'success')
    return redirect(url_for('cart'))

@app.route('/increase-quantity/<int:book_id>')
@login_required
def increase_quantity(book_id):
    book = Book.query.get_or_404(book_id)
    cart = session.get('cart', [])
    
    for item in cart:
        if item['book_id'] == book_id:
            if item['quantity'] >= book.stock:
                flash(f'Cannot add more! Only {book.stock} copies available.', 'error')
            else:
                item['quantity'] += 1
                session['cart'] = cart
                flash(f'Quantity increased to {item["quantity"]}', 'success')
            break
    
    return redirect(url_for('cart'))

@app.route('/decrease-quantity/<int:book_id>')
@login_required
def decrease_quantity(book_id):
    cart = session.get('cart', [])
    
    for item in cart:
        if item['book_id'] == book_id:
            if item['quantity'] > 1:
                item['quantity'] -= 1
                session['cart'] = cart
                flash(f'Quantity decreased to {item["quantity"]}', 'success')
            else:
                cart = [i for i in cart if i['book_id'] != book_id]
                session['cart'] = cart
                flash('Item removed from cart', 'success')
            break
    
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if current_user.is_admin():
        flash('Admins cannot purchase books', 'error')
        return redirect(url_for('index'))
    
    cart_items = session.get('cart', [])
    
    if not cart_items:
        flash('Your cart is empty', 'error')
        return redirect(url_for('cart'))
    
    if request.method == 'POST':
        total = 0
        low_stock_items = []
        
        for item in cart_items:
            book = Book.query.get(item['book_id'])
            quantity = item.get('quantity', 1)
            if book:
                if book.stock <= 0:
                    flash(f'Sorry, {book.title} is out of stock!', 'error')
                    return redirect(url_for('cart'))
                if quantity > book.stock:
                    flash(f'Sorry, only {book.stock} copies of {book.title} available!', 'error')
                    return redirect(url_for('cart'))
                
                remaining_stock = book.stock - quantity
                if book.stock <= 5 or remaining_stock <= 5:
                    low_stock_items.append(book.title)
                
                total += book.price * quantity
        
        if low_stock_items:
            order_status = 'Pending'
            auto_approve = False
        else:
            order_status = 'Approved'
            auto_approve = True
        
        order = Order(user_id=current_user.id, total_amount=total, status=order_status)
        db.session.add(order)
        db.session.flush()
        
        for item in cart_items:
            book = Book.query.get(item['book_id'])
            quantity = item.get('quantity', 1)
            if book:
                book.stock -= quantity
                
                if auto_approve:
                    library_entry = Library.query.filter_by(user_id=current_user.id, book_id=book.id).first()
                    if not library_entry:
                        library_entry = Library(user_id=current_user.id, book_id=book.id)
                        db.session.add(library_entry)
                
                order_item = OrderItem(
                    order_id=order.id,
                    book_id=book.id,
                    price_at_purchase=book.price,
                    quantity=quantity
                )
                db.session.add(order_item)
        
        db.session.commit()
        session['cart'] = []
        
        return redirect(url_for('order_success', order_id=order.id))
    
    cart_books = []
    total = 0
    
    for item in cart_items:
        book = Book.query.get(item['book_id'])
        if book:
            quantity = item.get('quantity', 1)
            row_total = book.price * quantity
            cart_books.append({
                'book': book,
                'quantity': quantity,
                'row_total': row_total
            })
            total += row_total
    
    return render_template('checkout.html', cart_books=cart_books, total=total)

@app.route('/order-success/<int:order_id>')
@login_required
def order_success(order_id):
    order = Order.query.get_or_404(order_id)
    
    if order.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    response = make_response(render_template('order_success.html', order=order))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.route('/my-library')
@login_required
def my_library():
    if current_user.is_admin():
        flash('Admin accounts do not have a library', 'info')
        return redirect(url_for('admin_dashboard'))
    
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.date.desc()).all()
    order_books = []
    for order in orders:
        for item in order.items:
            order_books.append({
                'book': item.book,
                'status': order.status,
                'order_id': order.id
            })
    
    return render_template('dashboard.html', order_books=order_books)

@app.route('/read/<int:book_id>')
@login_required
def read_book(book_id):
    library_entry = Library.query.filter_by(user_id=current_user.id, book_id=book_id).first()
    
    if not library_entry:
        flash('You do not own this book', 'error')
        return redirect(url_for('index'))
    
    book = Book.query.get_or_404(book_id)
    
    if book.file_path and os.path.exists(book.file_path):
        return send_file(book.file_path, mimetype='application/pdf')
    else:
        flash('PDF file not available for this book', 'error')
        return redirect(url_for('my_library'))

@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin():
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    from datetime import datetime as dt, timedelta
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    frequency = request.args.get('frequency', 'Daily')
    
    if not start_date:
        start_date = (dt.now().replace(day=1)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = dt.now().strftime('%Y-%m-%d')
    
    total_revenue = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0
    total_orders = Order.query.count()
    total_books = Book.query.count()
    total_users = User.query.filter_by(role='Customer').count()
    
    recent_orders = Order.query.order_by(Order.date.desc()).limit(10).all()
    books = Book.query.all()
    users = User.query.filter_by(role='Customer').all()
    
    start_dt = dt.strptime(start_date, '%Y-%m-%d')
    end_dt = dt.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
    
    orders = Order.query.filter(
        Order.status == 'Approved',
        Order.date >= start_dt,
        Order.date < end_dt
    ).order_by(Order.date).all()
    
    sales_data = {}
    for order in orders:
        if frequency == 'Daily':
            key = order.date.strftime('%Y-%m-%d')
        elif frequency == 'Monthly':
            key = order.date.strftime('%b %Y')
        elif frequency == 'Yearly':
            key = order.date.strftime('%Y')
        else:
            key = order.date.strftime('%Y-%m-%d')
        
        if key in sales_data:
            sales_data[key] += order.total_amount
        else:
            sales_data[key] = order.total_amount
    
    labels = list(sales_data.keys())
    values = list(sales_data.values())
    
    return render_template('admin.html', 
                         total_revenue=total_revenue,
                         total_orders=total_orders,
                         total_books=total_books,
                         total_users=total_users,
                         recent_orders=recent_orders,
                         books=books,
                         users=users,
                         labels=labels,
                         values=values,
                         start_date=start_date,
                         end_date=end_date,
                         frequency=frequency)

@app.route('/admin/upload', methods=['POST'])
@login_required
def admin_upload():
    if not current_user.is_admin():
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    title = request.form.get('title')
    author = request.form.get('author')
    price = float(request.form.get('price'))
    category = request.form.get('category')
    tag = request.form.get('tag') or None
    stock = int(request.form.get('stock', 50))
    brief_description = request.form.get('brief_description') or None
    
    cover_file = request.files.get('cover')
    pdf_file = request.files.get('pdf')
    
    cover_path = None
    pdf_path = None
    
    if cover_file and allowed_file(cover_file.filename):
        cover_filename = secure_filename(cover_file.filename)
        cover_path = os.path.join(app.config['UPLOAD_FOLDER'], 'covers', cover_filename)
        cover_file.save(cover_path)
        cover_path = f'/static/uploads/covers/{cover_filename}'
    
    if pdf_file and allowed_file(pdf_file.filename):
        pdf_filename = secure_filename(pdf_file.filename)
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], 'books', pdf_filename)
        pdf_file.save(pdf_path)
    
    book = Book(
        title=title,
        author=author,
        price=price,
        category=category,
        cover_image=cover_path or 'https://placehold.co/600x900',
        file_path=pdf_path,
        tag=tag,
        stock=stock,
        brief_description=brief_description
    )
    
    db.session.add(book)
    db.session.commit()
    
    flash(f'Book "{title}" uploaded successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin():
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    users = User.query.filter_by(role='Customer').all()
    return render_template('admin_users.html', users=users)

@app.route('/delete_book/<int:book_id>')
@login_required
def delete_book(book_id):
    if not current_user.is_admin():
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    book = Book.query.get_or_404(book_id)
    book_title = book.title
    
    db.session.delete(book)
    db.session.commit()
    
    flash(f'Book "{book_title}" has been deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/book/<int:book_id>')
def book_details(book_id):
    book = Book.query.get_or_404(book_id)
    reviews = Review.query.filter_by(book_id=book_id).order_by(Review.created_at.desc()).all()
    return render_template('book_details.html', book=book, reviews=reviews)

@app.route('/book/<int:book_id>/review', methods=['POST'])
@login_required
def add_review(book_id):
    book = Book.query.get_or_404(book_id)
    rating = int(request.form.get('rating'))
    comment = request.form.get('comment')
    
    existing_review = Review.query.filter_by(user_id=current_user.id, book_id=book_id).first()
    if existing_review:
        flash('You have already reviewed this book', 'info')
        return redirect(url_for('book_details', book_id=book_id))
    
    review = Review(user_id=current_user.id, book_id=book_id, rating=rating, comment=comment)
    db.session.add(review)
    db.session.commit()
    
    flash('Review added successfully!', 'success')
    return redirect(url_for('book_details', book_id=book_id))

@app.route('/admin/approve_order/<int:order_id>')
@login_required
def approve_order(order_id):
    if not current_user.is_admin():
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    order = Order.query.get_or_404(order_id)
    
    if order.status == 'Approved':
        flash('This order has already been approved', 'info')
        return redirect(url_for('admin_dashboard'))
    
    if order.status == 'Declined':
        flash('Cannot approve a declined order. Stock was already restored.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    if order.status != 'Pending':
        flash('Invalid order status', 'error')
        return redirect(url_for('admin_dashboard'))
    
    for item in order.items:
        book = Book.query.get(item.book_id)
        if book:
            library_entry = Library.query.filter_by(user_id=order.user_id, book_id=book.id).first()
            if not library_entry:
                library_entry = Library(user_id=order.user_id, book_id=book.id)
                db.session.add(library_entry)
    
    order.status = 'Approved'
    db.session.commit()
    
    flash(f'Order #{order.id} approved successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/decline_order/<int:order_id>')
@login_required
def decline_order(order_id):
    if not current_user.is_admin():
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    order = Order.query.get_or_404(order_id)
    
    if order.status == 'Approved':
        flash('Cannot decline an already approved order', 'error')
        return redirect(url_for('admin_dashboard'))
    
    if order.status == 'Declined':
        flash('This order has already been declined', 'info')
        return redirect(url_for('admin_dashboard'))
    
    if order.status != 'Pending':
        flash('Invalid order status', 'error')
        return redirect(url_for('admin_dashboard'))
    
    for item in order.items:
        book = Book.query.get(item.book_id)
        if book:
            book.stock += item.quantity
    
    order.status = 'Declined'
    db.session.commit()
    
    flash(f'Order #{order.id} declined and stock restored', 'info')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    if not current_user.is_admin():
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    
    if user.is_admin():
        flash('Cannot delete admin users', 'error')
        return redirect(url_for('admin_dashboard'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User "{username}" has been deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/sales_data')
@login_required
def sales_data():
    if not current_user.is_admin():
        return jsonify({'error': 'Access denied'}), 403
    
    orders = Order.query.filter_by(status='Approved').order_by(Order.date).all()
    
    daily_sales = {}
    for order in orders:
        date_key = order.date.strftime('%Y-%m-%d')
        if date_key in daily_sales:
            daily_sales[date_key] += order.total_amount
        else:
            daily_sales[date_key] = order.total_amount
    
    labels = list(daily_sales.keys())
    data = list(daily_sales.values())
    
    return jsonify({
        'labels': labels,
        'data': data
    })

@app.route('/api/stock/<int:book_id>')
def get_stock(book_id):
    book = Book.query.get_or_404(book_id)
    return jsonify({
        'stock': book.stock
    })

if __name__ == '__main__':
    with app.app_context():
        create_folders()
        db.create_all()
        seed_data()
    app.run(host='0.0.0.0', port=5000, debug=True)
