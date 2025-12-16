
from flask import Flask, render_template, request, redirect, url_for
import os, json
from datetime import date
from utils.pdf2json import pdf2json
from datetime import date, datetime

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
JSON_FOLDER = "json_data"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(JSON_FOLDER, exist_ok=True)


jours_fr = {
    "Mon": "Lu",
    "Tue": "Ma",
    "Wed": "Me",
    "Thu": "Je",
    "Fri": "Ve",
    "Sat": "Sa",
    "Sun": "Di"
}

def get_json_data():
    files = os.listdir(JSON_FOLDER)
    if files:
        path = os.path.join(JSON_FOLDER, files[0])
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

# ✅ Filtre pour convertir texte en couleur hexadécimale
def text_to_color(text):
    ascii_values = [ord(c) for c in text.upper()]
    # Générer des couleurs très claires (pastel)
    r = ((ascii_values[0] * 2) % 64) + 192  # entre 192 et 255
    g = ((ascii_values[1] * 3) % 64) + 192 if len(ascii_values) > 1 else 220
    b = ((ascii_values[2] * 5) % 64) + 192 if len(ascii_values) > 2 else 230
    return f'#{r:02x}{g:02x}{b:02x}'

app.jinja_env.filters['text_to_color'] = text_to_color

@app.route('/')
def home():
    today = date.today().strftime("%Y-%m-%d")
    data = get_json_data()
    today_course = None
    next_courses = []
    if data:
        planning = list(data['groupes'].values())[0]['planning']
        # Ajout des infos jour + semaine        
        for p in planning:
            d = datetime.strptime(p['date'], "%Y-%m-%d")
            jour_en = d.strftime("%a")
            p['jour'] = jours_fr.get(jour_en, jour_en)
            p['semaine'] = d.isocalendar()[1]

        # Cours du jour
        today_course = next((p for p in planning if p['date'] == today), None)
        # Les 3 prochains cours
        next_courses = [p for p in planning if p['date'] > today][:3]
    return render_template('home.html', today=today, today_course=today_course, next_courses=next_courses)

@app.route('/planning')
def planning():
    today = date.today().strftime("%Y-%m-%d")
    data = get_json_data()

    # Cas où aucun fichier JSON n'existe
    if not data:
        return render_template('planning.html', data=None, today=today)

    groupes = data.get('groupes', {})
    # Cas où le JSON est vide ou mal structuré
    if not groupes:
        return render_template('planning.html', data=None, today=today)

    # Cas normal : on prépare les données
    group_name = list(groupes.keys())[0]
    group_data = groupes[group_name]

    # Ajout des infos jour + semaine    
    for p in group_data['planning']:
        d = datetime.strptime(p['date'], "%Y-%m-%d")
        jour_en = d.strftime("%a")  # Mon, Tue...
        p['jour'] = jours_fr.get(jour_en, jour_en)
        p['semaine'] = d.isocalendar()[1]

    # Retourne toujours un template
    return render_template('planning.html', group_name=group_name, data=group_data, today=today)

@app.route('/import', methods=['GET', 'POST'])
def import_pdf():
    if request.method == 'POST':
        file = request.files.get('pdf')
        if file:
            pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(pdf_path)
            json_data = pdf2json(pdf_path)
            json_filename = file.filename.replace('.pdf', '.json')
            json_path = os.path.join(JSON_FOLDER, json_filename)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)
            return redirect(url_for('planning'))
    return render_template('import.html')

if __name__ == '__main__':
    app.run(debug=True)
