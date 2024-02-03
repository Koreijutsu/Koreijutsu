from flask import Flask, request, render_template_string
from PIL import Image
import os
from flask_mail import Mail, Message
from stegano import lsb

app = Flask(__name__)

# Konfiguracja loggera
import logging
from logging.handlers import RotatingFileHandler

# Ustawienie poziomu logowania dla konsoli
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
app.logger.addHandler(console_handler)

# Ustawienia dla zapisu do pliku
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)

# Konfiguracja Flask-Mail
mail = Mail(app)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

# Funkcja do ukrywania danych w obrazie za pomocą steganografii
def hide_data_in_image(image_file, data_to_hide, password):
    try:
        app.logger.info("Ukrywanie danych w obrazie")

        # Sprawdzenie, czy plik jest obrazem
        try:
            img = Image.open(image_file)
        except Exception as e:
            error_msg = f"Błąd podczas otwierania obrazu: {str(e)}"
            app.logger.error(error_msg)
            raise ValueError(error_msg)

        # Ukrycie danych w obrazie
        secret_img = lsb.hide(img, data_to_hide)
        img_with_hidden_data = "hidden_" + os.path.basename(image_file.filename)
        secret_img.save(img_with_hidden_data)

        app.logger.info(f"Ukrywanie danych w obrazie zakończone. Nowy obraz zapisany jako {img_with_hidden_data}")

        return img_with_hidden_data
    except Exception as e:
        error_msg = f"Błąd podczas ukrywania danych w obrazie: {str(e)}"
        app.logger.error(error_msg)
        raise ValueError(error_msg)

# Funkcja do wysyłania e-maila z użyciem Flask-Mail
def send_email(sender_email, receiver_email, subject, body, attachment_path, app, mail):
    try:
        app.logger.info("Rozpoczynanie wysyłania e-maila")

        msg = Message(subject, sender=sender_email, recipients=[receiver_email])
        msg.body = body

        if attachment_path is not None:
            with app.open_resource(attachment_path) as attachment:
                msg.attach(os.path.basename(attachment_path), "application/octet-stream", attachment.read())

        mail.send(msg)

        app.logger.info("Wysyłanie e-maila zakończone sukcesem")

    except Exception as e:
        error_msg = f"Błąd podczas wysyłania e-maila: {str(e)}"
        app.logger.error(error_msg)
        raise ValueError(error_msg)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            app.logger.info("Przetwarzanie żądania POST")

            # Odczyt danych z formularza
            password = request.form['password']
            sender_email = request.form['sender_email']
            receiver_email = request.form['receiver_email']
            email_password = request.form['email_password']
            text_to_hide = request.form.get('text_to_hide', '')

            # Sprawdzenie, czy obraz został dostarczony
            image = request.files.get('image')
            if not image:
                app.logger.error("Błąd: Brak obrazu w formularzu")
                return {"error": "Wybierz obraz przed przesłaniem formularza"}

            # Konfiguracja Flask-Mail wewnątrz kontekstu żądania HTTP
            app.config['MAIL_USERNAME'] = sender_email  # Ustawiamy na podstawie danych z formularza
            app.config['MAIL_PASSWORD'] = email_password  # Ustawiamy na podstawie danych z formularza

            # Ukrycie danych w obrazie
            try:
                img_with_hidden_data = hide_data_in_image(image, text_to_hide, password)
            except Exception as e:
                return {"error": f"Błąd podczas ukrywania danych w obrazie: {str(e)}"}

            # Wysłanie e-maila
            try:
                send_email(sender_email, receiver_email, 'Obraz z ukrytym tekstem', 'Obraz zawierający ukryty tekst.', img_with_hidden_data, app, mail)
            except Exception as e:
                return {"error": f"Błąd podczas wysyłania e-maila: {str(e)}"}

            app.logger.info("Przetwarzanie żądania POST zakończone sukcesem")

            return {"message": "E-mail został wysłany z sukcesem!"}

        except Exception as e:
            error_msg = f"Błąd podczas przetwarzania żądania POST: {str(e)}"
            app.logger.error(error_msg)
            return {"error": error_msg}
    else:
        html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Wypełnij formularz, aby wysłać plik</title>
            <script>
                function showHideFields() {
                    var selectedValue = document.getElementById("data_type").value;
                    var textToHideField = document.getElementById("text_to_hide_field");
                    var textFileField = document.getElementById("text_file_field");
                    var imageField = document.getElementById("image_field");

                    if (selectedValue === "text") {
                        textToHideField.style.display = "block";
                        textFileField.style.display = "none";
                        imageField.style.display = "none";
                    } else if (selectedValue === "text_file") {
                        textToHideField.style.display = "none";
                        textFileField.style.display = "block";
                        imageField.style.display = "none";
                    } else if (selectedValue === "text_and_text_file") {
                        textToHideField.style.display = "block";
                        textFileField.style.display = "block";
                        imageField.style.display = "none";
                    } else if (selectedValue === "image") {
                        textToHideField.style.display = "none";
                        textFileField.style.display = "none";
                        imageField.style.display = "block";
                    } else { "Wybierz"
                        textToHideField.style.display = "none";
                        textFileField.style.display = "none";
                        imageField.style.display = "none";
                    }
                }
            </script>
        </head>
        <body>
            <h1>Projekt Steganografia</h1>
            <form method="post" enctype="multipart/form-data">
                Wybierz rodzaj danych do ukrycia:
                <select name="data_type" id="data_type" onchange="showHideFields()">
                    <option value="choose" selected>Wybierz</option>
                    <option value="text">Tekst</option>
                    <option value="text_file">Plik Tekstowy</option>
                    <option value="text_and_text_file">Tekst i Plik Tekstowy</option>
                </select><br>

                <div id="text_to_hide_field" style="display:none;">
                    Tu wpisz tekst: <input type="text" name="text_to_hide"><br>
                </div>

                <div id="text_file_field" style="display:none;">
                    Wybierz plik .txt: <input type="file" name="text_file"><br>
                </div>

                Hasło: <input type="password" name="password"><br>

                <div id="image_field" style="display:none;">
                    Wybierz obrazek .png: <input type="file" name="image" required><br>
                </div>

                Twój mail: <input type="text" name="sender_email"><br>
                Do kogo mail: <input type="text" name="receiver_email"><br>
                Twoje hasło do maila: <input type="password" name="email_password"><br>

                <input type="file" name="image_from_file"><br>

                <input type="submit" value="Gotowe">
            </form>
        </body>
        </html>
        '''

        return render_template_string(html)

if __name__ == "__main__":
    app.run(debug=True)
