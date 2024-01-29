from flask import Flask, request, render_template_string
from PIL import Image
import os
import base64
import smtplib
from email.message import EmailMessage
import magic

app = Flask(__name__)

# Funkcja do ukrywania danych w obrazie za pomocą steganografii
def hide_data_in_image(image_path, data_to_hide, password):
    try:
        app.logger.info(f"Ukrywanie danych w obrazie {image_path}")

        # Sprawdzenie typu pliku za pomocą magic
        mime = magic.Magic()
        file_type = mime.from_file(image_path)

        # Sprawdzenie, czy plik jest obrazem
        if not file_type.startswith('image'):
            app.logger.error(f"Plik '{image_path}' nie jest obrazem")
            raise ValueError(f"Plik '{image_path}' nie jest obrazem")

        try:
            with open(image_path, "rb") as f:
                img = Image.open(f)
        except Exception as e:
            app.logger.error(f"Błąd podczas otwierania obrazu: {str(e)}")
            raise ValueError(f"Błąd podczas otwierania obrazu: {str(e)}")

        # Kodowanie danych do formatu base64
        encoded_data = base64.b64encode(data_to_hide.encode())

        # Modyfikacja wartości pikseli w obrazie w celu osadzenia zaszyfrowanych danych
        img_data = img.getdata()
        img_new_data = []
        for i, pixel in enumerate(img_data):
            if i < len(encoded_data):
                img_new_data.append((pixel[0], pixel[1], pixel[2], encoded_data[i]))
            else:
                img_new_data.append(pixel)

        # Zapisanie zaktualizowanego obrazu
        img_with_hidden_data = "hidden_" + os.path.basename(image_path)
        img.putdata(img_new_data)
        img.save(img_with_hidden_data)

        app.logger.info(f"Ukrywanie danych w obrazie zakończone. Nowy obraz zapisany jako {img_with_hidden_data}")

        return img_with_hidden_data
    except Exception as e:
        app.logger.error(f"Błąd podczas ukrywania danych w obrazie: {str(e)}")
        raise ValueError(f"Błąd podczas ukrywania danych w obrazie: {str(e)}")

# Funkcja do wysyłania e-maila
def send_email(sender_email, receiver_email, password, subject, body, attachment_path):
    try:
        app.logger.info("Rozpoczynanie wysyłania e-maila")
        
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = receiver_email

        # Ustawienie treści wiadomości
        msg.set_content(body)

        if attachment_path is not None:
            with open(attachment_path, 'rb') as f:
                file_data = f.read()
                # Dodanie załącznika
                msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=os.path.basename(attachment_path))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, password)
            smtp.send_message(msg)

        app.logger.info("Wysyłanie e-maila zakończone sukcesem")

    except Exception as e:
        app.logger.error(f"Błąd podczas wysyłania e-maila: {str(e)}")
        raise ValueError(f"Błąd podczas wysyłania e-maila: {str(e)}")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            app.logger.info("Przetwarzanie żądania POST")

            data_type = request.form['data_type']
            password = request.form['password']
            sender_email = request.form['sender_email']
            receiver_email = request.form['receiver_email']
            email_password = request.form['email_password']

            # Sprawdzenie, czy pola e-mail nie są puste
            if not sender_email or not receiver_email or not email_password:
                app.logger.error("Błąd: Puste pola e-mail")
                return {"error": "Uzupełnij pola e-mail"}

            if data_type == 'choose':
                app.logger.error("Błąd: Nie wybrano rodzaju danych do ukrycia")
                return {"error": "Wybierz rodzaj danych do ukrycia"}

            text_to_hide = request.form.get('text_to_hide', '')
            text_file = request.files.get('text_file')
            image = request.files.get('image')
            image_from_file = request.files.get('image_from_file')

            # Zapisanie pliku tymczasowego
            if text_file:
                text_file_path = "temp_file.txt"
                text_file.save(text_file_path)
                data_to_hide = open(text_file_path, 'rb').read()
            elif image_from_file:
                image_from_file_path = "temp_image_from_file.png"
                image_from_file.save(image_from_file_path)
                data_to_hide = image_from_file_path
            else:
                data_to_hide = text_to_hide

            # Sprawdzenie, czy obraz został dostarczony
            if 'image' in request.files:
                image = request.files['image']
            if image:

                image_path = "temp_image.png"
                image.save(image_path)
            else:
                app.logger.error("Błąd: Brak obrazu w formularzu")
                return {"error": "Wybierz obraz przed przesłaniem formularza"}

            zaszyfrowany_obraz = hide_data_in_image(image_path, data_to_hide, password)

            if text_file:
                os.remove(text_file_path)
            elif image_from_file:
                os.remove(image_from_file_path)

            if image:
                os.remove(image_path)

            send_email(sender_email, receiver_email, email_password, 'Obraz z ukrytym tekstem', 'Obraz zawierający ukryty tekst.', zaszyfrowany_obraz)
            
            app.logger.info("Przetwarzanie żądania POST zakończone sukcesem")

            return {"message": "E-mail został wysłany z sukcesem!"}

        except Exception as e:
            app.logger.error(f"Błąd podczas przetwarzania żądania POST: {str(e)}")
            return {"error": str(e)}
    else:
        html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Wybór pliku obrazu</title>
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
                    } else {  // Dodałem obsługę opcji "Wybierz"
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
                    Wybierz obrazek .png: <input type="file" name="image"><br>
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
