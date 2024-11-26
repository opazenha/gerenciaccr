from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=7070, host='0.0.0.0')

# https://www.youtube.com/watch?v=Xw9aco1aMrc
# https://www.youtube.com/watch?v=rbemoBGIXGU