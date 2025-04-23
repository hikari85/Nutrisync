from flask import Flask, render_template, request, redirect, session, url_for
from flask_pymongo import PyMongo

app = Flask(__name__)
app.secret_key = 'nutrisync_secret_key'

# MongoDB config — replace "nutrisyncDB" if you want a different DB name
app.config["MONGO_URI"] = "mongodb://localhost:27017/nutrisyncDB"
mongo = PyMongo(app)

# Homepage
@app.route('/')
def home():
    return render_template('index.html')

# About Page
@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = {
            "name": request.form['name'],
            "gender": request.form['gender'],
            "dob": request.form['dob'],
            "height": request.form['height'],
            "weight": request.form['weight'],
            "goal_weight": request.form['goal_weight'],
            "phone": request.form.get('phone'),  # Optional field
            "username": request.form['username'],
            "password": request.form['password'],
            "fitness_goal": request.form['fitness_goal'],
            "activity_level": request.form['activity_level']
        }

        # Check if username already exists
        existing_user = mongo.db.users.find_one({'username': user['username']})
        if existing_user:
            return "Username already exists. Please try another."

        mongo.db.users.insert_one(user)
        return redirect(url_for('login'))

    return render_template('register.html')

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = mongo.db.users.find_one({'username': username, 'password': password})
        if user:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

# User Profile
@app.route('/user')
def user_profile():
    if 'username' in session:
        user = mongo.db.users.find_one({'username': session['username']})
        updated = request.args.get('updated', 'false')
        return render_template('user.html', user=user)
    else:
        return redirect(url_for('login'))

# Update User Info
@app.route('/update_user', methods=['POST'])
def update_user():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    updated_data = {
        'age': request.form['age'],
        'height': request.form['height'],
        'weight': request.form['weight']
    }

    mongo.db.users.update_one(
        {'username': username},
        {'$set': updated_data}
    )

    return redirect(url_for('user_profile',updated='true'))

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        user = mongo.db.users.find_one({'username': session['username']})
        return render_template('dashboard.html', user=user)
    else:
        return redirect(url_for('login'))

# Logout (optional)
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
