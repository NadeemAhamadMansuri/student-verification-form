from flask import Flask, render_template, request
import firebase_admin
import datetime  
from firebase_admin import credentials, firestore
import os
import pandas as pd

app = Flask(__name__)

# Firebase credentials load करो
cred = credentials.Certificate('firebase_config.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

# Excel file ka path
EXCEL_FILE_PATH = 'students.xlsx'

# Excel data read karo
df = pd.read_excel(EXCEL_FILE_PATH, sheet_name='Sheet1')

# ✅ Columns ke naam strip करो (trailing spaces हटाने के लिए)
df.columns = df.columns.str.strip()

# ✅ Debug: print karo actual column names
print("Excel Columns (AFTER STRIP):", df.columns.tolist())
print(df.head())

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        
        admission_number = request.form.get('admission_search').strip()

        # Convert both sides to string for reliable comparison
        df['Admission Number'] = df['Admission Number'].astype(str)

        # Debugging (optional)
        print("Searching for:", admission_number)
        print("Available Admission Numbers:", df['Admission Number'].tolist())

        # Matching row
        student_row = df[df['Admission Number'] == admission_number]

        if not student_row.empty:
            # Row ko dict me convert karo
            student_data = student_row.iloc[0].to_dict()
            # ✅ Mapping with safe str() conversion
            mapped_data = {
                'student_class': str(student_data.get('Class', '') or ''),
                'section': str(student_data.get('Section', '') or ''),
                'name': str(student_data.get('Name', '') or ''),
                'gender': str(student_data.get('Gender', '') or ''),
                'aadhar': '',  # Form me parent bharenge
                
                'father_name': str(student_data.get('Father Name', '') or ''),
                'mother_name': str(student_data.get('Mother Name', '') or ''),
                'mobile': str(int(student_data.get('Mobile', 0))) if student_data.get('Mobile') else '',
                'dob': student_data.get('Date of Birth').strftime('%Y-%m-%d') if isinstance(student_data.get('Date of Birth'), datetime.datetime) else '',
                'samagra_id': '',          # blank by default
            }

                
            return render_template('index.html', **mapped_data)
        else:
            return "Student not found!"

    # ---------- HERE IS THE NEW SEARCH PAGE ----------
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Search Student</title>
  <style>
    body {
      margin: 0;
      font-family: 'Segoe UI', sans-serif;
      background: linear-gradient(135deg, #6D5BBA, #8D58BF);
      height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
    }
    .container {
      background: #ffffffee;
      padding: 40px;
      border-radius: 15px;
      width: 100%;
      max-width: 450px;
      text-align: center;
      box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    .container img {
      max-width: 120px;
      margin-bottom: 20px;
    }
    h2 {
      color: #4A3E8C;
      margin-bottom: 20px;
      font-size: 28px;
    }
    input[type="text"] {
      width: 100%;
      padding: 12px 15px;
      margin-top: 10px;
      border: 1px solid #ccc;
      border-radius: 8px;
      font-size: 16px;
      box-sizing: border-box;
    }
    button {
      background: linear-gradient(to right, #6D5BBA, #8D58BF);
      color: #fff;
      border: none;
      padding: 12px;
      font-size: 16px;
      border-radius: 8px;
      cursor: pointer;
      width: 100%;
      margin-top: 20px;
      transition: background 0.3s ease;
    }
    button:hover {
      background: linear-gradient(to right, #8D58BF, #6D5BBA);
    }
    .container img {
    max-width: 450px;
    height: auto;
    margin-bottom: 5px;
}
  </style>
</head>
<body>
  <div class="container">
    <img src="/static/CARMEL.png" alt="School Logo" />
    <h2>Students Varification Form</h2>
    <form method="POST">
      <input type="text" name="admission_search" placeholder="Enter Admission Number" required />
      <button type="submit">Search</button>
    </form>
  </div>
</body>
</html>
    '''

@app.route('/submit', methods=['POST'])
def submit():
    # Form से data लो
    data = {
        'student_class': request.form.get('student_class'),
        'section': request.form.get('section'),
        'name': request.form.get('name'),
        'gender': request.form.get('gender'),
        'aadhar': request.form.get('aadhar'),
        'father_name': request.form.get('father_name'),
        'mother_name': request.form.get('mother_name'),
        'mobile': request.form.get('mobile'),
        'dob': request.form.get('dob'),
        'samagra_id': request.form.get('samagra_id'),
    }

    # Firestore में save करो
    doc_ref = db.collection('students').document(data['aadhar'])
    doc_ref.set(data)

    return f"Data saved successfully for {data['name']}!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
