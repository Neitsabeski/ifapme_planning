import re
import json
from datetime import datetime
import pdfplumber
from pypdf import PdfReader

def extract_text_any(pdf_path):
    # Try pdfplumber
    try:
        with pdfplumber.open(pdf_path) as pdf:
            pages = [p.extract_text() for p in pdf.pages]
            if any(p for p in pages):
                return "\n".join([p for p in pages if p])
    except:
        pass

    # Try pypdf
    try:
        reader = PdfReader(pdf_path)
        pages = [p.extract_text() for p in reader.pages]
        if any(p for p in pages):
            return "\n".join([p for p in pages if p])
    except:
        pass

    return ""


def parse_pdf_to_json(pdf_path, output_json_path):
    raw = extract_text_any(pdf_path)
    lines = [l.strip() for l in raw.split("\n") if l.strip()]

    planning = []
    professeurs = {}
    classe = None
    annee = None

    # Regex adaptés à TON PDF
    regex_classe = re.compile(r"Classe\s*:\s*(.+)")
    regex_annee = re.compile(r"Année\s*:\s*(\d{4}-\d{4})")
    regex_prof = re.compile(r"^([A-Z]{3})\s+X.*?\s+\d+\s+(.+?)\s+\d{2}-\d{2}-\d{2}", re.IGNORECASE)

    # Lignes du planning : ID DATE JOUR HEURE MATIERE
    regex_planning = re.compile(
        r"^(\d+)\s+(\d{2}-\d{2}-\d{2})\s+[A-Za-z]{2}\s+(\d{2}:\d{2})\s+([A-Z]{3})"
    )

    for line in lines:

        # Classe
        m = regex_classe.search(line)
        if m:
            classe = m.group(1).strip()

        # Année
        m = regex_annee.search(line)
        if m:
            annee = m.group(1).strip()

        # Professeurs (bloc du bas)
        m = regex_prof.match(line)
        if m:
            matiere = m.group(1)
            prof = m.group(2).strip()
            # Si pas de nom clair → Prof inconnu
            if not re.search(r"[A-Za-z]+\s+[A-Za-z]+", prof):
                prof = "Prof inconnu"
            professeurs[matiere] = prof


        # Planning
        m = regex_planning.match(line)
        if m:
            id_ = int(m.group(1))
            date_str = m.group(2)
            heure_debut = m.group(3)
            cours = m.group(4)

            # Convertir date 20-10-25 → 2025-10-20
            d = datetime.strptime(date_str, "%d-%m-%y")
            date_iso = d.strftime("%Y-%m-%d")

            planning.append({
                "id": id_,
                "date": date_iso,
                "cours": cours,
                "heure_debut": heure_debut
            })

    json_data = {
        "groupes": {
            classe or "GROUPE_INCONNU": {
                "annee": annee or "ANNEE_INCONNUE",
                "professeurs": professeurs,
                "planning": planning
            }
        }
    }

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4, ensure_ascii=False)

    return json_data


# --- EXECUTION DIRECTE ---
if __name__ == "__main__":
    input_pdf = "./file.pdf"
    output_json = "./planning.json"
    parse_pdf_to_json(input_pdf, output_json)
