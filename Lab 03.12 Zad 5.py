from flask import Flask, request, jsonify

#localhost:5000/count_characters?text=przykladowytekst&words=przykladowy,test,slowo

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

def count_words(text, words):
    text = text.lower()
    words_count = {word: 0 for word in words}
    
    # Podział tekstu na słowa
    text_words = text.split()
    
    # Liczenie wystąpień każdego słowa
    for word in text_words:
        if word in words_count:
            words_count[word] += 1
    
    return words_count

@app.route('/count_characters', methods=['GET'])
def calculate_character_count():
    if request.method == 'GET':
        text = request.args.get('text')
        words = request.args.get('words')  # Dodanie pobierania drugiego parametru
        
        if text is not None and text != '' and words is not None and words != '':
            character_count = count_characters(text)
            sorted_characters = dict(sorted(character_count.items()))
            
            words_list = words.split(',')
            words_count = count_words(text, words_list)
            sorted_words = dict(sorted(words_count.items()))
            
            return jsonify({"characters_count": sorted_characters, "words_count": sorted_words})
        else:
            return jsonify({'error': 'Brak tekstu lub słów w zapytaniu GET lub tekst jest pusty'})
    else:
        return jsonify({'error': 'Metoda HTTP nieobsługiwana'})

if __name__ == '__main__':
    app.run(debug=True)
