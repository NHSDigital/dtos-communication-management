from app import create_app

app = create_app()

if __name__ == "__main__":
    # TODO: Update this to check for the environment specifically to decide when to run in debug mode
    app.run(debug=True)
