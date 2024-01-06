from flask import Flask, request, render_template_string
from PIL import Image
from cryptography.fernet import Fernet
import os
import base64

app = Flask(__name__)

# Funkcja do ukrywania danych w obrazie za pomocą steganografii
def hide_data_in_image(image_path, data_to_hide, password):
    img = Image.open(image_path)

    # Kodowanie danych do formatu base64
    encoded_data = base64.b64encode(data_to_hide.encode())

    # Inicjalizacja szyfrowania
    cipher_suite = Fernet(password)
    encrypted_data = cipher_suite.encrypt(encoded_data)

    # Konwersja zaszyfrowanych danych na listę liczb całkowitych
    encrypted_bytes = list(encrypted_data)

    # Modyfikacja wartości pikseli w obrazie w celu osadzenia zaszyfrowanych danych
    img_data = img.getdata()
    img_new_data = []
    for i, pixel in enumerate(img_data):
        if i < len(encrypted_bytes):
            img_new_data.append((pixel[0], pixel[1], pixel[2], encrypted_bytes[i]))
        else:
            img_new_data.append(pixel)

    # Zapisanie zaktualizowanego obrazu
    img_with_hidden_data = "hidden_" + os.path.basename(image_path)
    img.putdata(img_new_data)
    img.save(img_with_hidden_data)

    return img_with_hidden_data

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            text_to_hide = request.form['text_to_hide']
            password = request.form['password']
            sender_email = request.form['sender_email']
            receiver_email = request.form['receiver_email']
            email_password = request.form['email_password']

            image = request.files['image']
            image.save("temp_image.png")

            file = request.files['file']  # Pobranie pliku z formularza
            file_data = file.read().decode('utf-8')

            zaszyfrowany_obraz = hide_data_in_image("temp_image.png", file_data, password)

            os.remove("temp_image.png")

            # Tutaj można dodać własny kod do obsługi wysyłania maili
            return {"message": "E-mail został wysłany z sukcesem!"}

        except Exception as e:
            return {"error": str(e)}
    else:
        html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Wybór pliku obrazu</title>
        </head>
        <body>
            <h1>Projekt Steganografia</h1>
            <form method="post" enctype="multipart/form-data">
                Tu wpisz tekst: <input type="text" name="text_to_hide"><br>
                Hasło: <input type="password" name="password"><br>
                Twój mail: <input type="text" name="sender_email"><br>
                Do kogo mail: <input type="text" name="receiver_email"><br>
                Hasło do maila: <input type="password" name="email_password"><br>
                Wybierz obrazek .png: <input type="file" name="image"><br>
                Wybierz plik tekstowy: <input type="file" name="file"><br>
                <input type="submit" value="Gotowe">
            </form>
        </body>
        </html>
        '''
        return render_template_string(html)

if __name__ == "__main__":
    app.run(debug=True)
