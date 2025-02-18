from flask import Flask, render_template, request, send_file, redirect, url_for, session, jsonify
from flask_bcrypt import Bcrypt
from flask_caching import Cache
from scripts.db import insert_user, get_user, get_all_users, get_liked_Meals_db, insert_liked_Meals, remove_liked_Meals, insert_user_Data, insert_login_log, get_login_log, get_user_data, insert_reset_token, get_username_from_token, update_password, get_token_details
from scripts.check_input import sanitize_input, is_valid_username
from scripts.geo import fetch_geo
from datetime import datetime, timedelta
import uuid
import secrets
from io import BytesIO


app = Flask(__name__)
bcrypt = Bcrypt(app)
# Configure Flask-Caching
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

csp_header = {
    'default-src': "'self'",
    'style-src': "'self' 'unsafe-inline' https://fonts.googleapis.com",
    'font-src': "'self' https://fonts.gstatic.com",
    'img-src': "'self' https://www.themealdb.com data:",
    'connect-src': "'self' https://www.themealdb.com",
    'frame-src': "'self' https://www.youtube.com/",
}

# Set the Content Security Policy header for all responses with a dynamic nonce using secrets
@app.after_request
def set_csp_header(response):
    csp_value = '; '.join([f"{key} {value}" for key, value in csp_header.items()])
    response.headers['Content-Security-Policy'] = csp_value
    return response

# Adding X-Frame-Options header for all responses
@app.after_request
def add_security_headers(response):
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    return response

# Set HSTS header for all responses
@app.after_request
def add_hsts_header(response):
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    return response

# Adding X-Content-Type-Options header for all responses
@app.after_request
def add_content_type_header(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

# Replace with a strong, randomly generated secret key
app.secret_key = 'your_secret_key_here'
app.static_folder = 'static'
# app.config['SESSION_TYPE'] = 'filesystem'  # Use filesystem-based session storage
# app.config['SESSION_PERMANENT'] = False  # Ensure the session is not permanent
# app.config['SESSION_USE_SIGNER'] = True  # Enable session signing
# app.config['SESSION_COOKIE_SECURE'] = False  # Set to False for testing over non-HTTPS

@app.route('/')
def index():
    return render_template('index.html')


##########################################################################################################
# Account
@app.route('/account')
def account():
    if 'username' in session:
        # User is logged in, display their account page
        username = session['username']

        return render_template('account.html', username=username)
    else:
        # User is not logged in, redirect to the login page
        return redirect(url_for('login'))


# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    csrf_token = session.get('csrf_token') or secrets.token_hex(16)
    session['csrf_token'] = csrf_token

    if request.method == 'GET':
        print(f"Generated CSRF Token: {csrf_token}")
        # Serve the CSRF token without setting it in the cookie
        return render_template('register.html', csrf_token=session['csrf_token'])

    if request.method == 'POST':
        submitted_token = request.form.get('csrf_token')
        session_token = session.get('csrf_token')
        print(f"Submitted CSRF Token: {submitted_token} , Session Token: {session_token}")
        if csrf_token != submitted_token:
            return "CSRF token validation failed. Please try again."
        
        username = sanitize_input(request.form.get('username'))
        password = sanitize_input(request.form.get('password'))

        if username and password:
            # Validate username and password  place it after username if needed - and is_valid_password(password)
            if is_valid_username(username):
                # Check if the username already exists
                existing_user = get_user(username)

                if existing_user:
                    return "Registration failed. Username already exists. <a href='/register'>Try again</a>"

                # If the username is unique and the input is valid, insert the new user
                # Hash Password
                hashed_password = bcrypt.generate_password_hash(
                    password).decode('utf-8')
                # user_ip = request.remote_addr
                user_ip = request.access_route[-1]
                # Login Log
                insert_login_log(username, user_ip)
                # Enable After Live Upload
                query_status, user_country, user_region, user_city, user_zip, user_latitude, user_longitude, user_isp, user_timezone = fetch_geo(user_ip)
                insert_user_Data(username, user_ip, user_country, user_region, user_city,
                                 user_zip, user_latitude, user_longitude, user_timezone, user_isp)
                # Create new User
                insert_user(username, hashed_password, user_ip)
                # Cookie
                session['username'] = username  # Set new login data
                session.pop('csrf_token') # POP the csrf token after sucessfull login
                return redirect(url_for('index'))

            else:
                return "Invalid username or password. Please check your input."

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    csrf_token = session.get('csrf_token') or secrets.token_hex(16)
    session['csrf_token'] = csrf_token

    if request.method == 'GET':
        print(f"Generated CSRF Token: {csrf_token}")
        # Serve the CSRF token without setting it in the cookie
        return render_template('login.html', csrf_token=session['csrf_token'])

    if request.method == 'POST':
        # Validate CSRF token
        submitted_token = request.form.get('csrf_token')
        session_token = session.get('csrf_token')
        print(f"Submitted CSRF Token: {submitted_token} , Session Token: {session_token}")
        if csrf_token != submitted_token:
            return "CSRF token validation failed. Please try again."

        username = sanitize_input(request.form.get('username'))
        password = sanitize_input(request.form.get('password'))

        if username and password:
            # Validate username and password
            user_data = get_user(username)

            if user_data and bcrypt.check_password_hash(user_data['password'], password):
                # Successful login
                user_ip = request.access_route[-1]
                
                # Login Log
                query_status, user_country, user_region, user_city, user_zip, user_latitude, user_longitude, user_isp, user_timezone = fetch_geo(user_ip)
                insert_user_Data(username, user_ip, user_country, user_region, user_city,
                                 user_zip, user_latitude, user_longitude, user_timezone, user_isp)
                
                insert_login_log(username, user_ip)

                # Set the username in the session after successful login
                session['username'] = username
                session.pop('csrf_token') # POP the csrf token after sucessfull login

                return redirect(url_for('index'))
            else:
                return "Login failed. Please check your credentials."
        else:
            return "Invalid username or password. Please check your input."

# Password Reset url generate by admin
@app.route('/reset-password', methods=['POST'])
def reset_password():
    if request.method == 'POST':
        username = request.json.get('username')  # Change to json

        # Check if the username exists in your database
        admin_check = session.get('username')
        if admin_check == 'admin':
            user_data = get_user(username)

            if user_data:
                # Generate a unique token and set its expiration time
                reset_token = str(uuid.uuid4())
                reset_token_expiry = datetime.now() + timedelta(minutes=30)

                # Insert the reset token into the reset_tokens table
                insert_reset_token(username, reset_token, reset_token_expiry)

                # Return the token in the JSON response
                return jsonify({'success': True, 'token': reset_token, 'message': 'Password reset link generated successfully.'})
            else:
                return jsonify({'success': False, 'message': 'User not found.'})

def is_valid_token(token):
    data = get_token_details(token)

    if data:
        expiration_time = datetime.strptime(data[3], '%Y-%m-%d %H:%M:%S.%f')
        current_time = datetime.now() + timedelta(milliseconds=2)
        return expiration_time > current_time
    else:
        return False

# Reset password through unique url
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'GET':
        # Display the password reset form with the token input field
        token = sanitize_input(request.args.get('token'))
        username = get_username_from_token(token)
        if is_valid_token(token):
            return render_template('reset_password.html', token=token, username=username)
        else:
            return jsonify({'error':'Token has expired or is Invalid'})
        
    elif request.method == 'POST':
        token = request.form.get('token')
        password = sanitize_input(request.form.get('password1'))
        password2 = sanitize_input(request.form.get('password2'))

        # Check if the token is valid
        if is_valid_token(token):
            username = get_username_from_token(token)
        else:
            return jsonify({'error':'Token has expired or is Invalid'})

        if username and password == password2:
            user_ip = request.access_route[-1]
            # Delete the token and update the password
            # delete_token(token)
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            update_password(username, hashed_password, user_ip)
            user_ip = request.access_route[-1]
                # Login Log
            insert_login_log(username, user_ip)
            query_status, user_country, user_region, user_city, user_zip, user_latitude, user_longitude, user_isp, user_timezone = fetch_geo(user_ip)
            insert_user_Data(username, user_ip, user_country, user_region, user_city,
                                 user_zip, user_latitude, user_longitude, user_timezone, user_isp)
            return "Your password is reset"
        else:
            return "Invalid or expired token. Please try again, or your password not match"
        
    return "Invalid token"

# Reset token test api
@app.route('/token-test')
def token_user():
    try:
        token = request.args.get('token')
        # decoded_token = unquote(token)  # Decode the URL-encoded token
        data = get_token_details(token)
        # print(f"Token: {token}, Decoded Token: {token}, Username: {username}")
        # return jsonify({'username': username})
        return jsonify({'data': data})
    except Exception as e:
        print(f"Error in token_user route: {e}")
        return jsonify({'error': str(e)})

# Admin User Profile check endpoint
@app.route('/<string:username>', methods=['GET'])
def user(username):
    nonce = secrets.token_hex(8)
    if 'username' in session:
        logged_in_username = session['username']

        if logged_in_username == 'admin':
            csp_header['script-src'] = f"'self' 'nonce-{nonce}'"
            username = sanitize_input(username)
            liked_meals = get_liked_Meals_db(username)
            user_data = get_user_data(username)
            user_login_info = get_user(username)
            login_log = get_login_log(username)
            meal = [meal[2] for meal in liked_meals]

            return render_template('admin/user_details.html',
                       username=username,
                       loginDetails=user_login_info,
                       liked_meal_ids=meal,  # Pass the likedMeals data
                       loginLog=login_log,
                       userData=user_data,
                       nonce=nonce)
            
        return redirect(url_for('account'))  # HTTP 403 Forbidden for non-admin users
    else:
        return redirect(url_for('login'))

# Logout
@app.route('/logout')
def logout():
    session.clear()  # Clear the session data
    return redirect(url_for('login'))

#########################################################################################################
# Database API
# Add Liked meals to database
@app.route('/add_meal', methods=['POST'])
def add_meal():
    if 'username' in session:
        # username = session['username']
        username = session.get('username')

        meal_data = request.json  # Extract JSON data from the request body

        if 'idMeal' in meal_data:
            idMeal = meal_data['idMeal']

            # Check if the meal is already liked by the user
            liked_meals = get_liked_Meals_db(username)
            meal = [meal[2] for meal in liked_meals]

            if idMeal in meal:
                return jsonify({'message': 'Meal already liked'})
            else:
                # if username:
                # Insert the liked meal into the database
                insert_liked_Meals(username, idMeal)
                return jsonify({'message': 'Meal added successfully'})
        else:
            return jsonify({'error': 'Invalid request data'})
    else:
        return jsonify({'error': 'User not logged in'})

# Fetch Liked meals from database
@app.route('/get_liked_meals', methods=['GET'])
def get_liked_meals():
    # Retrieve liked meals from the data store
    username = session.get('username')
    liked_meals = get_liked_Meals_db(username)

    # Extract the third value from each liked meal
    meal = [meal[2] for meal in liked_meals]

    return jsonify({'likedMeals': meal,
                    'username': username})

# Remove liked meals from database
@app.route('/remove_liked_meals', methods=['POST'])
def remove_liked_meals():
    meal_data = request.json

    if 'idMeal' in meal_data:
        username = session.get('username')
        idMeal = meal_data['idMeal']

        # Check if the meal is already liked by the user
        liked_meals = get_liked_Meals_db(username)
        meal = [meal[2] for meal in liked_meals]

        if idMeal in meal:
            remove_liked_Meals(username, idMeal)
            return jsonify({'message': 'Meal removed Successfully'})
        else:
            return jsonify({'message': 'Meal Not in liked meals'})
    else:
        return jsonify({'error': 'Invalid request data'})
    

# admin user panel
@app.route('/admin/dashboard')
def admin_dashboard():
    username = session.get('username')
    if username == 'admin':
        users = get_all_users() 
        cookies = request.cookies
        return render_template('admin/admin_dashboard.html', users=users, cookies=cookies)
    else:
        return jsonify({'error':'Not an admin'}), 403 


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)