from fpdf import FPDF

def generate_report_pdf(user_data, progress_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Заголовок
    pdf.cell(200, 10, txt="Отчет о прогрессе", ln=1, align='C')
    pdf.ln(10)
    
    # Данные пользователя
    pdf.cell(200, 10, txt=f"Пользователь: {user_data['username']}", ln=1)
    pdf.cell(200, 10, txt=f"Email: {user_data['email']}", ln=1)
    pdf.cell(200, 10, txt=f"Дата регистрации: {user_data['registration_date']}", ln=1)
    pdf.cell(200, 10, txt=f"Уровень: {user_data['level']}", ln=1)
    pdf.ln(10)
    
    # Прогресс
    pdf.cell(200, 10, txt="Прогресс по заданиям:", ln=1)
    for item in progress_data:
        pdf.cell(200, 10, txt=f"Задание: {item['task']}", ln=1)
        pdf.cell(200, 10, txt=f"  Выполнено: {item['completed']}", ln=1)
        pdf.cell(200, 10, txt=f"  Попытки: {item['attempts']}", ln=1)
        pdf.cell(200, 10, txt=f"  Последняя попытка: {item['last_attempt']}", ln=1)
        pdf.ln(5)
    
    # Сохраняем во временный файл
    import tempfile
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf.output(temp_file.name)
    return temp_file.name