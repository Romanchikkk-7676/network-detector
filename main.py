from flask import Flask, render_template_string, request
import joblib
import numpy as np
import os

# Загружаем модель
rf = joblib.load('random_forest.pkl')
scaler = joblib.load('scaler.pkl')
feature_names = joblib.load('feature_names.pkl')

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Детектор сетевых атак</title>
    <style>
        body {font-family: Arial; max-width: 800px; margin: auto; padding: 20px; background: #f0f0f0;}
        .container {background: white; padding: 30px; border-radius: 10px;}
        h1 {color: #333; text-align: center;}
        input {width: 200px; padding: 5px; margin: 5px;}
        button {background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;}
        .normal {background: #d4edda; color: #155724; padding: 20px; text-align: center; font-size: 24px; margin-top: 20px;}
        .attack {background: #f8d7da; color: #721c24; padding: 20px; text-align: center; font-size: 24px; margin-top: 20px;}
        .quick-test {margin-top: 20px; padding: 15px; background: #e9ecef; border-radius: 5px;}
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ Детектор сетевых атак</h1>
        <p style="text-align:center">Модель Random Forest</p>
        
        <form method="POST">
            {% for f in features %}
            <div>
                <label style="display:inline-block; width:180px">{{ f }}:</label>
                <input type="text" name="{{ f }}" value="0">
            </div>
            {% endfor %}
            <button type="submit">🔍 Определить</button>
        </form>
        
        <div class="quick-test">
            <form method="POST" style="display:inline">
                <input type="hidden" name="quick_test" value="normal">
                <button type="submit">📡 Нормальный трафик</button>
            </form>
            <form method="POST" style="display:inline">
                <input type="hidden" name="quick_test" value="attack">
                <button type="submit">⚠️ DoS атака</button>
            </form>
        </div>
        
        {% if result %}
        <div class="{{ class_name }}">
            {{ result_text }}
            <div style="font-size: 14px;">Вероятность атаки: {{ prob }}%</div>
        </div>
        {% endif %}
    </div>
</body>
</html>
'''

# Примеры для теста
NORMAL = [0, 2, 1, 0, 100, 500, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 10, 5, 1, 0, 0, 0, 0, 0, 0]
ATTACK = [1, 2, 1, 0, 5000, 100, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 100, 50, 0.5, 0.3, 0, 0, 0.2, 0.8, 0.1, 200, 100, 0.5, 0.3, 0.1, 0.2, 0.1, 0.1, 0.1]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'quick_test' in request.form:
            if request.form['quick_test'] == 'normal':
                vals = NORMAL[:len(feature_names)]
            else:
                vals = ATTACK[:len(feature_names)]
        else:
            vals = []
            for f in feature_names:
                try:
                    vals.append(float(request.form.get(f, 0)))
                except:
                    vals.append(0)
        
        input_arr = np.array(vals).reshape(1, -1)
        input_scaled = scaler.transform(input_arr)
        pred = rf.predict(input_scaled)[0]
        prob = round(rf.predict_proba(input_scaled)[0][1] * 100, 2)
        
        if pred == 0:
            return render_template_string(HTML, features=feature_names[:10], result=True, class_name='normal', result_text='✅ НОРМАЛЬНЫЙ ТРАФИК', prob=prob)
        else:
            return render_template_string(HTML, features=feature_names[:10], result=True, class_name='attack', result_text='⚠️ ОБНАРУЖЕНА АТАКА', prob=prob)
    
    return render_template_string(HTML, features=feature_names[:10], result=False, class_name='', result_text='', prob=0)

if __name__ == '__main__':
    print('Сервер запущен! Открой браузер и перейди на http://127.0.0.1:5000')
    app.run(debug=True, port=5000)
