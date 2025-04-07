import os
import json
import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import uuid
from flask import Flask, request, render_template, redirect, url_for, flash, session, jsonify, make_response
from functools import wraps

app = Flask(__name__)
app.secret_key = 'library_management_secret_key'

# Decorator to check if user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


# Decorator to check if user is admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login', next=request.url))
        if session.get('role') != 'admin':
            flash('You do not have permission to access this area', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


# Add cache control headers
@app.after_request
def add_no_cache(response):
    if request.path != '/static/':  # Don't cache dynamic content
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response


@dataclass
class Book:
    id: str
    title: str
    author: str
    genre: str
    publication_year: int
    is_checked_out: bool = False
    checked_out_by: Optional[str] = None
    checked_out_date: Optional[str] = None
    return_date: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)


class LibraryManagementSystem:
    def __init__(self, db_file="library_db.json"):
        self.db_file = db_file
        self.books = self._load_books()
        
    def _load_books(self) -> List[Book]:
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    books_data = json.load(f)
                    return [Book(**book) for book in books_data]
            except Exception as e:
                print(f"Error loading database: {e}")
                return []
        return []
    
    def _save_books(self):
        with open(self.db_file, 'w') as f:
            json.dump([book.to_dict() for book in self.books], f, indent=2)
    
    def add_book(self, title: str, author: str, genre: str, publication_year: int) -> Book:
        book_id = str(uuid.uuid4())
        new_book = Book(
            id=book_id,
            title=title,
            author=author,
            genre=genre,
            publication_year=publication_year
        )
        self.books.append(new_book)
        self._save_books()
        return new_book
    
    def edit_book(self, book_id: str, title: str = None, author: str = None, 
                genre: str = None, publication_year: int = None) -> Optional[Book]:
        for book in self.books:
            if book.id == book_id:
                if title:
                    book.title = title
                if author:
                    book.author = author
                if genre:
                    book.genre = genre
                if publication_year:
                    book.publication_year = publication_year
                self._save_books()
                return book
        return None
    
    def delete_book(self, book_id: str) -> bool:
        for i, book in enumerate(self.books):
            if book.id == book_id:
                del self.books[i]
                self._save_books()
                return True
        return False
    
    def check_out_book(self, book_id: str, borrower_name: str) -> Optional[Book]:
        for book in self.books:
            if book.id == book_id and not book.is_checked_out:
                book.is_checked_out = True
                book.checked_out_by = borrower_name
                book.checked_out_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                book.return_date = None
                self._save_books()
                return book
        return None
    
    def check_in_book(self, book_id: str) -> Optional[Book]:
        for book in self.books:
            if book.id == book_id and book.is_checked_out:
                book.is_checked_out = False
                book.return_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save_books()
                return book
        return None
    
    def search_books(self, query: str) -> List[Book]:
        query = query.lower()
        results = []
        
        for book in self.books:
            if (query in book.title.lower() or 
                query in book.author.lower() or 
                query in book.genre.lower() or 
                query in str(book.publication_year)):
                results.append(book)
                
        return results
    
    def get_all_books(self) -> List[Book]:
        return self.books
    
    def get_checked_out_books(self) -> List[Book]:
        return [book for book in self.books if book.is_checked_out]
    
    def get_available_books(self) -> List[Book]:
        return [book for book in self.books if not book.is_checked_out]
    
    def get_book_by_id(self, book_id: str) -> Optional[Book]:
        for book in self.books:
            if book.id == book_id:
                return book
        return None
    
    def recommend_books(self, liked_book_id: str, num_recommendations: int = 3) -> List[Book]:
        """Simple AI-like feature: recommend books based on genre and author"""
        liked_book = self.get_book_by_id(liked_book_id)
        if not liked_book:
            return []
            
        # First try to find books with the same genre and different author
        recommendations = [
            book for book in self.books 
            if book.id != liked_book_id and 
            book.genre == liked_book.genre and 
            book.author != liked_book.author
        ]
        
        # If we don't have enough, add books by the same author
        if len(recommendations) < num_recommendations:
            same_author_books = [
                book for book in self.books
                if book.id != liked_book_id and
                book.author == liked_book.author and
                book not in recommendations
            ]
            recommendations.extend(same_author_books[:num_recommendations - len(recommendations)])
        
        # If we still don't have enough, add other books
        if len(recommendations) < num_recommendations:
            other_books = [
                book for book in self.books
                if book.id != liked_book_id and
                book not in recommendations
            ]
            recommendations.extend(other_books[:num_recommendations - len(recommendations)])
            
        return recommendations[:num_recommendations]


# Initialize library
library = LibraryManagementSystem()

# Add sample books if the database is empty
if not library.get_all_books():
    library.add_book("To Kill a Mockingbird", "Harper Lee", "Fiction", 1960)
    library.add_book("1984", "George Orwell", "Science Fiction", 1949)
    library.add_book("Pride and Prejudice", "Jane Austen", "Romance", 1813)
    library.add_book("The Great Gatsby", "F. Scott Fitzgerald", "Fiction", 1925)
    library.add_book("Brave New World", "Aldous Huxley", "Science Fiction", 1932)
    print("Sample books added to the library.")


# Simple user authentication (in a real app, you'd use a proper authentication system)
users = {
    "admin": {"password": "admin123", "role": "admin"},
    "user": {"password": "user123", "role": "user"}
}

# Routes
@app.route('/')
@login_required
def index():
    books = library.get_all_books()
    return render_template('index.html', books=books, user_role=session.get('role'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users and users[username]['password'] == password:
            session['username'] = username
            session['role'] = users[username]['role']
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    response = make_response(redirect(url_for('login')))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/books/add', methods=['GET', 'POST'])
@admin_required
def add_book():
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        genre = request.form.get('genre')
        
        try:
            year = int(request.form.get('year'))
        except ValueError:
            flash('Publication year must be a number', 'danger')
            return render_template('add_book.html')
        
        library.add_book(title, author, genre, year)
        flash('Book added successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('add_book.html')


@app.route('/books/edit/<book_id>', methods=['GET', 'POST'])
@admin_required
def edit_book(book_id):
    book = library.get_book_by_id(book_id)
    if not book:
        flash('Book not found', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form.get('title') or None
        author = request.form.get('author') or None
        genre = request.form.get('genre') or None
        
        year_str = request.form.get('year')
        year = int(year_str) if year_str else None
        
        library.edit_book(book_id, title, author, genre, year)
        flash('Book updated successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('edit_book.html', book=book)


@app.route('/books/delete/<book_id>')
@admin_required
def delete_book(book_id):
    if library.delete_book(book_id):
        flash('Book deleted successfully!', 'success')
    else:
        flash('Failed to delete book', 'danger')
    
    return redirect(url_for('index'))


@app.route('/books/checkout/<book_id>', methods=['GET', 'POST'])
@login_required
def checkout_book(book_id):
    book = library.get_book_by_id(book_id)
    if not book:
        flash('Book not found', 'danger')
        return redirect(url_for('index'))
    
    if book.is_checked_out:
        flash('This book is already checked out', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        borrower = request.form.get('borrower')
        if library.check_out_book(book_id, borrower):
            flash(f'Book "{book.title}" checked out successfully to {borrower}', 'success')
        else:
            flash('Failed to check out the book', 'danger')
        
        return redirect(url_for('index'))
    
    return render_template('checkout_book.html', book=book)


@app.route('/books/checkin/<book_id>')
@login_required
def checkin_book(book_id):
    book = library.get_book_by_id(book_id)
    if not book:
        flash('Book not found', 'danger')
        return redirect(url_for('index'))
    
    if not book.is_checked_out:
        flash('This book is not checked out', 'danger')
        return redirect(url_for('index'))
    
    if library.check_in_book(book_id):
        flash(f'Book "{book.title}" checked in successfully', 'success')
    else:
        flash('Failed to check in the book', 'danger')
    
    return redirect(url_for('index'))


@app.route('/books/search')
@login_required
def search_books():
    query = request.args.get('query', '')
    books = library.search_books(query) if query else []
    
    return render_template('search_results.html', books=books, query=query)


@app.route('/books/recommend/<book_id>')
@login_required
def recommend_books(book_id):
    book = library.get_book_by_id(book_id)
    if not book:
        flash('Book not found', 'danger')
        return redirect(url_for('index'))
    
    recommendations = library.recommend_books(book_id)
    
    return render_template('recommendations.html', book=book, recommendations=recommendations)


@app.route('/api/books')
@login_required
def api_books():
    books = library.get_all_books()
    return jsonify([book.to_dict() for book in books])


@app.route('/api/books/<book_id>')
@login_required
def api_book(book_id):
    book = library.get_book_by_id(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book.to_dict())


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)