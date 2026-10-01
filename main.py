from flask import Flask, render_template_string, request, jsonify
import urllib.request
from deep_translator import GoogleTranslator

app = Flask(__name__)

# واجهة المستخدم HTML
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>أداة جلب وترجمة النصوص</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 30px; background-color: #f4f4f9; }
        .container { max-width: 700px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        input[type="text"] { width: 70%; padding: 10px; margin-bottom: 10px; border: 1px solid #ccc; border-radius: 4px; }
        button { padding: 10px 15px; background-color: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background-color: #218838; }
        textarea { width: 100%; height: 150px; margin-top: 10px; border: 1px solid #ccc; border-radius: 4px; padding: 10px; box-sizing: border-box; }
        .btn-translate { background-color: #007bff; margin-top: 10px; }
        .btn-translate:hover { background-color: #0069d9; }
    </style>
</head>
<body>
    <div class="container">
        <h2>جلب وترجمة نصوص Pastebin</h2>
        <div>
            <input type="text" id="pastebinUrl" placeholder="أدخل رابط Pastebin Raw هنا (e.g. https://pastebin.com/raw/...)">
            <button onclick="fetchText()">جلب النص</button>
        </div>
        
        <textarea id="fetchedText" placeholder="النصر المجلوب سيظهر هنا..."></textarea>
        <button class="btn-translate" onclick="translateText()">ترجمة النص</button>

        <h3>النتيجة:</h3>
        <textarea id="translatedText" placeholder="النتيجة المترجمة ستظهر هنا بصيغة (Original, الترجمة)..." readonly></textarea>
    </div>

    <script>
        async function fetchText() {
            const url = document.getElementById('pastebinUrl').value;
            if(!url) return alert('رجاءً أدخل الرابط');
            
            const response = await fetch('/fetch', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ url: url })
            });
            const data = await response.json();
            if(data.text) {
                document.getElementById('fetchedText').value = data.text;
            } else {
                alert('حدث خطأ أثناء جلب النص: ' + (data.error || ''));
            }
        }

        async function translateText() {
            const text = document.getElementById('fetchedText').value;
            if(!text) return alert('لا يوجد نص لترجمته');

            const response = await fetch('/translate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ text: text })
            });
            const data = await response.json();
            if(data.result) {
                document.getElementById('translatedText').value = data.result;
            } else {
                alert('حدث خطأ أثناء الترجمة');
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/fetch', methods=['POST'])
def fetch_pastebin():
    data = request.json
    url = data.get('url', '')
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req) as response:
            content = response.read().decode('utf-8')
        return jsonify({'text': content})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/translate', methods=['POST'])
def translate():
    data = request.json
    text = data.get('text', '')
    
    # تقسيم النص إلى أسطر لترجمة كل سطر على حدة
    lines = text.splitlines()
    translated_lines = []
    
    translator = GoogleTranslator(source='auto', target='ar')
    
    for line in lines:
        stripped = line.strip()
        if stripped:
            translated_text = translator.translate(stripped)
            translated_lines.append(f"{stripped},{translated_text}")
        else:
            translated_lines.append("")
            
    result = "\n".join(translated_lines)
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=True)
