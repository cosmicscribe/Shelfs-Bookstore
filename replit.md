# Shelfs - Modern Digital Bookstore

## Overview

Shelfs is a Flask-based e-commerce platform for purchasing and reading digital books. The application supports role-based access (Customers and Admins), allowing customers to browse books, manage shopping carts, complete purchases, and access their digital library. Administrators can upload books, manage inventory, process orders, and view analytics.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Application Framework
- **Framework**: Flask (Python web framework)
- **Rationale**: Flask provides lightweight, flexible routing and template rendering suitable for medium-sized applications
- **Architecture Pattern**: MVC (Model-View-Controller) with server-side rendering
- **Template Engine**: Jinja2 for dynamic HTML generation

### Authentication & Authorization
- **Solution**: Flask-Login with session-based authentication
- **Password Security**: Werkzeug's password hashing (generate_password_hash/check_password_hash)
- **Role System**: Two-tier role system (Admin/Customer) stored in User model
- **Session Management**: Flask's built-in session management with SECRET_KEY

### Database & ORM
- **Database**: SQLite (file-based database at `sqlite:///kitabghar.db`)
- **ORM**: Flask-SQLAlchemy
- **Rationale**: SQLite chosen for simplicity and portability; suitable for development and small-to-medium deployments
- **Schema Design**: 
  - Relational model with clear foreign key relationships
  - One-to-many relationships: User→Orders, User→Library, Book→Reviews
  - Many-to-many through OrderItem: Orders↔Books

### Data Models
1. **User**: Authentication, role management, relationships to orders and library
2. **Book**: Core product entity with pricing, inventory (stock), categorization, tags, brief description, and file storage
3. **Order**: Purchase records with status tracking ('Pending', 'Approved', 'Declined')
4. **OrderItem**: Junction table linking orders to books with quantity (Integer, default=1) and price_at_purchase
5. **Library**: User's purchased books collection
6. **Review**: Rating (1-5) and comment system with one review per user per book

**Recent Changes (November 21, 2025 - Version 5.0 Final Build):**
- **PRG Pattern Implementation**: Post-Redirect-Get pattern for checkout prevents duplicate orders on browser back button
- **Order Success Page**: Dedicated confirmation page with cache-control headers (no-store, no-cache) to prevent form resubmission
- **Advanced Search**: Hero section search bar with hybrid category filter using HTML5 datalist (type OR choose from dropdown)
- **Professional Footer**: 4-column dark footer with Brand, Quick Links, Categories, and Contact sections
- **About Us Page**: Full content page with hero section, story narrative, impact statistics, and feature highlights
- **Enhanced UI**: Amber pill badges for book tags (rounded-full design), improved Warm Library theme consistency
- **Smart Search**: Keyword search filters by title/author, category filter dynamically populated from database
- **Cart & Quantity**: Multi-copy purchase support with +/- controls, stock validation, smart increment on re-add
- **Stock Reservation System**: Immediate deduction on checkout prevents overselling
- **Hybrid Inventory Logic**: Auto-approve for high stock (>5), pending for low stock (≤5)
- **Order Status Guards**: Bulletproof transitions prevent double-processing of approvals/declines

### Frontend Architecture
- **CSS Framework**: Tailwind CSS (CDN-based)
- **Icons**: Font Awesome 6.4.0
- **Design System**: "Warm Library" theme
  - Color palette: Slate backgrounds, Amber accents, warm paper white
  - Responsive design with mobile-first approach
- **UI Patterns**: Card-based layouts, split-screen authentication, hero sections with overlays

### File Management
- **Upload Storage**: Local filesystem (`static/uploads/books/`, `static/uploads/covers/`)
- **Allowed Formats**: PDF for books, PNG/JPG/JPEG/GIF for covers
- **File Size Limit**: 16MB maximum
- **Security**: Werkzeug's secure_filename for sanitization

### Business Logic
- **Shopping Cart**: Session-based cart storage with quantity support (no database persistence until checkout)
  - **Quantity Feature**: Users can buy multiple copies of the same book
  - **Cart Controls**: +/- buttons to adjust quantities, automatic validation against stock levels
  - **Smart Increment**: Adding an already-in-cart book increases quantity instead of showing error
  - **Stock Validation**: Cannot add more than available stock, with real-time warnings
- **Hybrid Order Workflow**: Intelligent stock-based approval system with quantity support
  - **High Stock (>5 after purchase)**: Orders auto-approved, stock decremented immediately, books added to library instantly
  - **Low Stock (≤5 current or ≤5 after purchase)**: Orders set to 'Pending' status, awaiting admin approval, stock reserved immediately
  - **Out of Stock (0)**: Purchase blocked entirely with error message
  - Mixed carts trigger pending status for entire order if any item has/would have low stock
  - **Stock Reservation**: All orders (approved and pending) decrement stock immediately during checkout to prevent overselling
  - **Admin Decline**: Restores reserved stock back to inventory when order is rejected
  - **Admin Approve**: Grants library access to pending orders (stock already deducted during checkout)
- **Inventory Management**: Real-time stock tracking with automatic quantity-aware deduction on checkout, live stock updates via polling API every 5 seconds on product detail pages
- **Guest Browsing**: Anonymous users can view catalog with limited interactions; clicking book images, titles, or "View Now" redirects to login page for purchase access
- **Order Status System**: Three-tier status (Approved/Pending/Declined) with conditional library access, visual badges, and bulletproof status transition guards

### Admin Features
- **Dashboard Analytics**: Revenue, order count, book catalog size, user count with real-time data binding
- **Advanced Visual Analytics**: Interactive Chart.js-powered sales visualization with:
  - Date range filters (start date, end date) with default to current month
  - Dynamic grouping options (Daily, Monthly, Yearly revenue aggregation)
  - Real-time chart updates based on filter selections
  - Revenue trend visualization showing approved orders only
- **Book Management**: Upload new books with title, author, price, category, tags, brief descriptions, cover images, and PDF files; delete inventory
- **Order Processing**: Review all orders with hybrid approval workflow; approve/decline pending low-stock orders
- **User Management**: View all registered customers with username and email, delete accounts

## External Dependencies

### Python Packages
- **Flask**: Web framework
- **Flask-SQLAlchemy**: ORM integration
- **Flask-Login**: User session management
- **Werkzeug**: Security utilities and file handling

### Frontend Libraries (CDN)
- **Tailwind CSS**: Utility-first CSS framework for styling
- **Font Awesome**: Icon library for UI elements
- **Chart.js**: Data visualization for admin analytics dashboard

### Media Resources
- **Unsplash**: External image hosting for book covers and hero sections
  - Authentication pages: photo-1524995997946-a1c2e315a42f (cozy reading nook)
  - Storefront hero images
  - Book cover images (2:3 aspect ratio)
  - Fallback: Slate-800 background color for image load failures

### File System
- **Static File Storage**: Local directory structure for uploaded PDFs and cover images
- **Demo Content**: Auto-generated demo.pdf for immediate functionality