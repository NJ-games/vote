from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import json
import os
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure secret key
votes_file = 'votes.json'
candidates_file = 'candidates.json'
password = 'shemi123'  # Replace with the desired password
last=None

def load_candidates():
    try:
        with open(candidates_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_candidates(candidates):
    with open(candidates_file, 'w') as file:
        json.dump(candidates, file)


def load_votes():
    try:
        with open(votes_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        votes = {name: 0 for name in load_candidates()}
        save_votes(votes)
def save_votes(votes):
    with open(votes_file, 'w') as file:
        json.dump(votes, file)

def reset_votes():
    votes = {name: 0 for name in load_candidates()}
    save_votes(votes)

def is_authenticated():
    return session.get('authenticated')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/total_votes', methods=['GET', 'POST'])
def total_votes():
    if not is_authenticated():
        return redirect(url_for('login', next=url_for('total_votes')))
    votes = load_votes()
    total = sum(votes.values())
    session['authenticated'] = False
    return render_template('total_votes.html', total=total)

@app.route('/results', methods=['GET', 'POST'])
def results():
    if not is_authenticated():
        return redirect(url_for('login', next=url_for('results')))
    votes = load_votes()
    return render_template('results.html', votes=votes)
    # if request.method == 'POST':
    #     input_password = request.form.get('password')
    #     if input_password == password:
    #         session['authenticated'] = True
    #         return redirect(url_for('results'))
    #     else:
    #         return render_template('results.html', error='Incorrect password')
    # if is_authenticated():
    #     votes = load_votes()
    #     return render_template('results.html', votes=votes)
    # else:
    #     return render_template('results.html')

@app.route('/reset_votes', methods=['POST'])
def reset_votes_route():
    reset_votes()
    session['authenticated'] = False
    return redirect(url_for('index'))

@app.route('/vote')
def vote_page():
    candidates = load_candidates()
    votes = load_votes()
    return render_template('vote.html', candidates=candidates, votes=votes)

@app.route('/vote', methods=['POST'])
def vote():
    button = request.json.get('button')
    global last
    last=button
    votes = load_votes()
    if button in votes:
        votes[button] += 1
        save_votes(votes)
        return jsonify({'success': True, 'redirect': "/wait"})
    return jsonify(success=False, error='Invalid button'), 400






@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        input_password = request.form.get('password')
        if input_password == password:
            session['authenticated'] = True
            next_url = request.form.get('next') or url_for('index')
            return redirect(next_url)
        else:
            next_url = request.form.get('next') or url_for('index')
            return render_template('login.html', error='Incorrect password', next=next_url)
    next_url = request.args.get('next') or url_for('index')
    return render_template('login.html', next=next_url)




@app.route('/manage_candidates', methods=['GET'])

def manage_candidates():
    if not is_authenticated():
        return redirect(url_for('login', next=url_for('manage_candidates')))
    candidates = load_candidates()
    session['authenticated'] = False
    return render_template('manage_candidates.html', candidates=candidates)

@app.route('/add_candidate', methods=['GET', 'POST'])

def add_candidate():
    if request.method == 'POST':
        name = request.form.get('name')
        photo = request.files.get('photo')
        icon = request.files.get('icon')
        
        if not name or not photo or not icon:
            return render_template('add_candidate.html', error='All fields are required')
        
        # Save photo and icon
        photo_filename = f'{name}_photo.jpg'
        icon_filename = f'{name}_icon.jpg'
        photo_path = os.path.join('static/uploads/', photo_filename)
        icon_path = os.path.join('static/uploads/', icon_filename)
        
        photo.save(photo_path)
        icon.save(icon_path)
        
        candidates = load_candidates()
        candidates[name] = {'photo': photo_path, 'icon': icon_path}
        save_candidates(candidates)
        return redirect(url_for('manage_candidates'))
    
    return render_template('add_candidate.html')

@app.route('/edit_candidate/<name>', methods=['GET', 'POST'])

def edit_candidate(name):
    candidates = load_candidates()
    if request.method == 'POST':
        new_name = request.form.get('name')
        new_photo = request.files.get('photo')
        new_icon = request.files.get('icon')
        
        if not new_name:
            return render_template('edit_candidate.html', error='Name is required', candidate=candidates[name])
        
        # Update photo and icon if provided
        if new_photo:
            photo_filename = f'{new_name}_photo.jpg'
            photo_path = os.path.join('static/uploads/', photo_filename)
            new_photo.save(photo_path)
            candidates[new_name]['photo'] = photo_path
        
        if new_icon:
            icon_filename = f'{new_name}_icon.jpg'
            icon_path = os.path.join('static/uploads/', icon_filename)
            new_icon.save(icon_path)
            candidates[new_name]['icon'] = icon_path

        if new_name != name:
            del candidates[name]
            candidates[new_name] = candidates.pop(new_name)
        
        save_candidates(candidates)
        return redirect(url_for('manage_candidates'))
    
    candidate = candidates.get(name)
    if not candidate:
        return redirect(url_for('manage_candidates'))
    
    return render_template('edit_candidate.html', candidate=candidate)

@app.route('/delete_candidate/<name>', methods=['POST'])

def delete_candidate(name):
    candidates = load_candidates()
    if name in candidates:
        os.remove(candidates[name]['photo'])
        os.remove(candidates[name]['icon'])
        del candidates[name]
        save_candidates(candidates)
    return redirect(url_for('manage_candidates'))


@app.route('/wait',methods=['GET', 'POST'])
def wait_page():
    return render_template('wait.html',name=last)





if __name__ == '__main__':
    if not os.path.exists('static/uploads'):
        os.makedirs('static/uploads')
    app.run(debug=True)



