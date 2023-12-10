from flask import Flask, request, jsonify

#localhost:5000/count_characters?text=przykladowytekst

app = Flask(__name__)

def count_characters(text):
    counts = [0] * 256  # Tworzenie listy o długości 256 (zakładając ASCII)
    
    # Liczenie wystąpień każdego znaku w tekście
    for char in text:
        counts[ord(char)] += 1
    
    # Tworzenie słownika zawierającego wystąpienia znaków
    characters_count = {}
    for i in range(256):
        if counts[i] > 0:
            characters_count[chr(i)] = counts[i]
    
    return characters_count

@app.route('/count_characters', methods=['GET'])
def calculate_character_count():
    if request.method == 'GET':
        text = request.args.get('text')
        if text is not None and text != '':
            character_count = count_characters(text)
            sorted_characters = dict(sorted(character_count.items()))
            return jsonify(sorted_characters)
        else:
            return jsonify({'error': 'Brak tekstu w zapytaniu GET lub tekst jest pusty'})
    else:
        return jsonify({'error': 'Metoda HTTP nieobsługiwana'})

if __name__ == '__main__':
    app.run(debug=True)
