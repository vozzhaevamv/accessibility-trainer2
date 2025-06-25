from app import create_app

app = create_app()

if __name__ == '__main__':
    print("Запуск приложения...")
    print("Доступные маршруты:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.methods} {rule.rule} -> {rule.endpoint}")
    app.run(debug=True)