def is_alphanumeric(char):
    return ('a' <= char <= 'z') or ('A' <= char <= 'Z') or ('0' <= char <= '9') or (char in 'ąćęłńóśźżĄĆĘŁŃÓŚŹŻ')

def normalize_token(token):
    # Normalizacja na małe litery
    # ord(char) zwraca kod ASCII dla znaku. Dodajemy do niego 32 (różnica między kodami ASCII dla wielkiej i małej litery), a następnie używamy chr() do konwersji kodu ASCII z powrotem na znak.
    normalized_token = ''
    for char in token:
        if 'A' <= char <= 'Z':
            normalized_token += chr(ord(char) + 32)  # Zamiana dużej litery na małą literę 
        elif char in 'ĄĆĘŁŃÓŚŹŻ':
            normalized_token += chr(ord(char) + 32)  # Zamiana dużej litery diakrytycznej na małą literę
        else:
            normalized_token += char

    # Usunięcie diakrytyków
    normalized_token = normalized_token.replace('ą', 'a').replace('ć', 'c').replace('ę', 'e').replace('ł', 'l').replace('ń', 'n').replace('ó', 'o').replace('ś', 's').replace('ź', 'z').replace('ż', 'z')
    normalized_token = normalized_token.replace('Ą', 'A').replace('Ć', 'C').replace('Ę', 'E').replace('Ł', 'L').replace('Ń', 'N').replace('Ó', 'O').replace('Ś', 'S').replace('Ź', 'Z').replace('Ż', 'Z')

    return normalized_token


def tokenize_words(text):
    word = ''       # Zmienna word przechowuje aktualnie analizowane słowo
    tokens = []     # Pusta lista tokens, która będzie przechowywać tokeny
    for char in text:
        if is_alphanumeric(char):  # Tą funkcją sprawdzamy czy znak jest alfanumeryczny
            word += char
        else:
            if word:  # Dodajemy słowo tylko jeśli nie jest puste
                tokens.append(normalize_token(word)) # Dodajemy znormalizowane słowo do listy/ Wywołujemy funkcję normalize_token
                word = ''  # Resetujemy zmienną word
    if word:
        tokens.append(normalize_token(word))
    return tokens

# Przykładowe użycie
text = "To- jest @ mój : przykładowy % token."
#text = "I can't do programming."
print(tokenize_words(text))

    # Dlaczego wybraliście taką metodę?

    # Wybrałem tokenizację słów, ponieważ jest ona jedną z najczęściej stosowanych oraz ma wiele zastosowań np. w analizie tekstu czy uczeniu maszynowym.

    # Jak to zaimplementowaliście?

    # W tej implementacji iterujemy po każdym znaku w tekście. Jeśli napotkamy znak alfanumeryczny, dodajemy go do zmiennej word. 
    # Jeśli napotkamy inny znak (np. spacje, znaki interpunkcyjne),to dodajemy bieżące słowo do listy tokens i resetujemy zmienną word. 
    # Na końcu, jeśli istnieje bieżące słowo po zakończeniu iteracji, również dodajemy go do listy tokens.

    # Jakie klopoty z implementacją zauważacie?

    # 1. W tej implementacji brakuje obsługi znaków specjalnych. Program traktuje je jako separatory.
    #    Problemem będzie jeżeli program będzie analizował adres URL, lub tekst będzie w języku angielskim np. słowa typu i'm czy can't.
