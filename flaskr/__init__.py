import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from ebaysdk.finding import Connection as Finding

from flaskr.query.query import *


load_dotenv()
app = Flask(__name__)


def create_app():
    api = Finding(appid=os.environ.get("APP_ID"), domain='svcs.sandbox.ebay.com', config_file=None)

    @app.route('/category-to-predict', methods=['GET'])
    def category_to_predict():
        category_id = request.args.get('categoryId', "")
        if not category_id or category_id == "":
            return jsonify({ "error": "No category id provided" }), 400
        elif not category_id.isdigit():
            return jsonify({ "error": "Category id must be a number" }), 400

        data_to_insert = []
        page = 0

        while page < 3:
            page += 1
            resp = api.execute('findItemsByCategory', {
                "categoryId": category_id,
                'paginationInput': {
                    'entriesPerPage': 1,
                    'pageNumber': page
                }
            })

            data = resp.dict()
            items = data.get('searchResult', {})

            if not items:
                break

            items = items.get('item', [])
            for item in items:
                print(item)
                if item['primaryCategory']['categoryName']:
                    data_to_insert.append((
                        item['itemId'],
                        category_id,
                        item['title'],
                        item['listingInfo']['startTime'],
                        item['sellingStatus']['currentPrice']['value'],
                        item['primaryCategory']['categoryName']
                    ))

            total_pages = int(data.get("paginationOutput").get("totalPages"))
            if page >= total_pages:
                break

        if not data_to_insert:
            return jsonify({ "error": "Couldn't collect any data for the given category id" }), 404

        # insert all the data to db
        print(data_to_insert)
        # insert_products(data_to_insert)

        return jsonify({ "message": "success" })

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", port=5001)
