# TU_Air/run.py
from tu_air import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)