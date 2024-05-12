def is_alphanumeric(char):
    return ('a' <= char <= 'z') or ('A' <= char <= 'Z') or ('0' <= char <= '9') or (char in 'ąćęłńóśźżĄĆĘŁŃÓŚŹŻ')

def tokenize_words(text):
    word = ''       #Zmienna word przechowuje aktualnie analizowane słowo
    tokens = []     #Pusta lista tokens, która będzie przechowywać tokeny.
    for char in text:
        if is_alphanumeric(char):  #Tą funkcją sprawdzamy czy znak jest alfanumeryczny
            word += char
        elif word:
            tokens.append(word) #Dodajemy słowo do listy
            word = ''
    if word:
        tokens.append(word)
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
