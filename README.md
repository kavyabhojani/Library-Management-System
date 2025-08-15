# Library Management System

A full-featured library management system with both command-line and web interfaces.

## Features

### Core Features
- Book Management: Add, edit, and delete books (title, author, genre, publication year)
- Check-in/Check-out: Track borrowers and manage book availability
- Search: Find books by title, author, genre, or publication year
- Simple user authentication with role-based permissions (admin/user)

### Bonus Features
- Web-based interface using Flask
- Role-based access control (admins vs. regular users)
- Book recommendation system based on genre and author
- Session persistence with cache control
- Protection against unauthorized access

## Setup Instructions

### Prerequisites
- Python 3.6 or higher
- Flask (for web version)

### Installation

1. Clone or download this repository
2. Install required dependencies:
   ```bash
   pip install flask
   ```

### Running the Web Application

1. Make sure all files are in the correct places:
   - `web_library_system.py` in the root directory
   - All HTML template files in a `/templates` directory

2. Run the Flask application:
   ```bash
   python web_library_system.py
   ```

3. Access the web interface at:
   ```
   http://localhost:5000
   ```

### Login Credentials

- Admin User:
  - Username: `admin`
  - Password: `admin123`
  - Permissions: Full access to all features

- Regular User:
  - Username: `user`
  - Password: `user123`
  - Permissions: Limited to viewing, searching, and checking books in/out

## System Architecture

### Data Structure
- Books are stored as JSON objects with properties for title, author, genre, publication year, and checkout status
- Data persistence is managed through a JSON file storage system

### Web Interface
- Built with Flask for backend processing
- Frontend uses HTML templates with Bootstrap for styling
- Session management with Flask's built-in session handling

### Security Features
- Basic role-based access control
- Session validation to protect routes
- Cache control headers to prevent unauthorized access via browser back button

## Project Structure

```
library_system/
│
├── web_library_system.py     # Main web application
├── library_db.json           # Database file (auto-generated)
│
├── templates/                # Web interface templates
│   ├── base.html             # Base template with navigation
│   ├── login.html            # Login form
│   ├── index.html            # Book listing page
│   ├── add_book.html         # Form to add new books
│   ├── edit_book.html        # Form to edit existing books
│   ├── checkout_book.html    # Form to check out a book
│   ├── search_results.html   # Search results display
│   └── recommendations.html  # Book recommendations page
│
└── README.md                 # This documentation
```

## API Endpoints

The system provides RESTful API endpoints:

- `GET /api/books` - List all books
- `GET /api/books/<book_id>` - Get details for a specific book

## Future Enhancements

Features that could be added in the future:

- User registration system
- Integration with external authentication providers
- Advanced search with filters
- Book reservations and wait-listing
- Overdue book notifications
- Book cover image uploads
- Barcode scanning for physical books
- Statistics and reporting

## Technical Choices

- **Flask**: Lightweight web framework perfect for small to medium applications
- **JSON Storage**: Simple file-based storage appropriate for the scope of this assessment
- **Bootstrap**: Provides responsive design without additional frontend complexity
- **Jinja2 Templates**: Flask's native templating system for dynamic content
