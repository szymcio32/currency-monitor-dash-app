from app import app
from layouts import layout
import callbacks


app.layout = layout

if __name__ == '__main__':
    app.run_server()
