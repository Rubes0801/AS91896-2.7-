# This application provides a web interface to query and display information
# about New Zealand's wildlife species and their conservation status

# Import necessary libraries
from flask import Flask, g, render_template, request, redirect
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()

app = Flask(__name__)

# Define database file path
DATABASE = 'NZ_Wildlife.db'

def get_db():
    if not hasattr(g, '_database'):
        g._database = sqlite3.connect(DATABASE)
        g._database.row_factory = sqlite3.Row  
    return g._database


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/")
def home():
    db = get_db()
    cursor = db.cursor()
    
    # Get the selected field from the query parameter
    selected_field = request.args.get('field', default=None)
    
    # Get all data from the Species table
    cursor.execute("SELECT * FROM Species")
    species_results = cursor.fetchall()
    
    # Get all data from the Origin_Status table
    cursor.execute("SELECT * FROM Origin_Status")
    origin_status_results = cursor.fetchall()
    
    # Get all data from the Species_Type table
    cursor.execute("SELECT * FROM Species_Type")
    species_type_results = cursor.fetchall()
    
    # Get all data from the Status table
    cursor.execute("SELECT * FROM Status")
    status_results = cursor.fetchall()
    
    cursor.close()
    
    # Define mapping of field names to column indices for template use
    field_indices = {
        'species_name': 1,
        'scientific_name': 2,
        'species_type': 3,
        'origin_status': 4,
        'predator': 5,
        'prey': 6,
        'status': 7,
        'family': 8,
        'numbers': 9
    }
    
    return render_template(
        "index.html", 
        species=species_results,
        origin_status=origin_status_results,
        species_type=species_type_results,
        status=status_results,
        selected_field=selected_field,
        field_indices=field_indices
    )


@app.route("/species")
def species():
    cursor = get_db().cursor()
    search_query = request.args.get('name', default='', type=str).lower()
    
    if search_query:
        # Search across all relevant fields
        cursor.execute("""
            SELECT DISTINCT s.*, 
                   CASE 
                       WHEN LOWER(s.species_name) LIKE ? THEN 'Species Name'
                       WHEN LOWER(s.scientific_name) LIKE ? THEN 'Scientific Name'
                       WHEN LOWER(s.species_type) LIKE ? THEN 'Species Type'
                       WHEN LOWER(s.origin_status) LIKE ? THEN 'Origin Status'
                       WHEN LOWER(s.predator) LIKE ? THEN 'Predator'
                       WHEN LOWER(s.prey) LIKE ? THEN 'Prey'
                       WHEN LOWER(s.status) LIKE ? THEN 'Status'
                       WHEN LOWER(s.family) LIKE ? THEN 'Family'
                       WHEN LOWER(s.numbers) LIKE ? THEN 'Numbers'
                   END as matched_field
            FROM species s
            WHERE LOWER(s.species_name) LIKE ?
               OR LOWER(s.scientific_name) LIKE ?
               OR LOWER(s.species_type) LIKE ?
               OR LOWER(s.origin_status) LIKE ?
               OR LOWER(s.predator) LIKE ?
               OR LOWER(s.prey) LIKE ?
               OR LOWER(s.status) LIKE ?
               OR LOWER(s.family) LIKE ?
               OR LOWER(s.numbers) LIKE ?
        """, ['%' + search_query + '%'] * 18)  # 9 for CASE + 9 for WHERE
    else:
        # If no search query, display all species
        cursor.execute("SELECT *, NULL as matched_field FROM species")
    
    results = cursor.fetchall()
    cursor.close()
    return render_template("species.html", species=results, search_query=search_query)


@app.route('/add', methods=["GET", "POST"])
def add():
    if request.method == "POST":
        try:
            new_name = request.form.get("item_name")
            new_description = request.form.get("item_description")

            if new_name and new_description:  
                cursor = get_db().cursor()
                cursor.execute("INSERT INTO species (name, description) VALUES (?, ?)", (new_name, new_description))
                get_db().commit()
                cursor.close()
        except sqlite3.Error as e:
            print("Database error:", e)

    return redirect('/')

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Handle registration logic here 
        return redirect('/')  # Redirect to home after registration
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Handle login logic here 
        return redirect('/')  # Redirect to home after login
    return render_template("login.html")

@app.route("/api/search-suggestions")
def search_suggestions():
    query = request.args.get('q', '').lower().strip()
    if len(query) < 2:  # Only search if at least 2 characters
        return {'suggestions': []}
    
    cursor = get_db().cursor()
    
    # Search for matching species names and scientific names
    cursor.execute("""
        SELECT DISTINCT species_name, scientific_name 
        FROM species 
        WHERE LOWER(species_name) LIKE ? 
           OR LOWER(scientific_name) LIKE ?
        ORDER BY species_name
        LIMIT 10
    """, ['%' + query + '%', '%' + query + '%'])
    
    results = cursor.fetchall()
    cursor.close()
    
    suggestions = []
    for row in results:
        # Add species name if it matches
        if query in row[0].lower():
            suggestions.append({
                'text': row[0],
                'type': 'Species Name'
            })
        # Add scientific name if it matches and is different
        if query in row[1].lower() and row[1] != row[0]:
            suggestions.append({
                'text': row[1],
                'type': 'Scientific Name'
            })
    
    return {'suggestions': suggestions[:8]}  # Limit to 8 suggestions

if __name__ == "__main__":
    app.run(debug=True)
    