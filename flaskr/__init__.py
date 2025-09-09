from flask import Flask


app = Flask(__name__)


def create_app():

    @app.route('/', methods=['GET'])
    def hello():
        print('hello')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", port=5001)
