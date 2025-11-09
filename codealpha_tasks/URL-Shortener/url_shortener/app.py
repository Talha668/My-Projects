from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, URLMapping
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///url_shortener.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    """Home page with URL shortening form"""
    short_url = None
    if request.method == 'POST':
        long_url = request.form.get('long_url')
        
        if not long_url:
            flash('Please enter a URL', 'error')
        else:
            # Add http:// if missing
            if not long_url.startswith(('http://', 'https://')):
                long_url = 'http://' + long_url
            
            # Check if URL already exists
            existing_mapping = URLMapping.query.filter_by(long_url=long_url).first()
            
            if existing_mapping:
                short_url = f"http://localhost:5000/{existing_mapping.short_code}"
                flash('URL already shortened!', 'info')
            else:
                # Create new URL mapping
                new_mapping = URLMapping(long_url=long_url)
                db.session.add(new_mapping)
                db.session.commit()
                short_url = f"http://localhost:5000/{new_mapping.short_code}"
                flash('URL shortened successfully!', 'success')
    
    return render_template('index.html', short_url=short_url)

@app.route('/<short_code>')
def redirect_to_long_url(short_code):
    """Redirect short URL to original long URL"""
    mapping = URLMapping.query.filter_by(short_code=short_code).first()
    
    if mapping:
        # Increment click counter
        mapping.clicks += 1
        db.session.commit()
        return redirect(mapping.long_url)
    else:
        flash('Short URL not found!', 'error')
        return redirect(url_for('index'))

@app.route('/stats')
def stats():
    """Show statistics of all shortened URLs"""
    all_urls = URLMapping.query.order_by(URLMapping.created_at.desc()).all()
    return render_template('stats.html', urls=all_urls)

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)