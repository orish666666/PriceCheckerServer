import os
import base64

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from ebaysdk.finding import Connection as Finding

from flaskr.query.query import *


load_dotenv()
app = Flask(__name__)


def create_app():
    api = Finding(appid=os.environ.get("APP_ID"), domain='svcs.sandbox.ebay.com', config_file=None)

    @app.route('/get-predict-categories', methods=['GET'])
    def get_predict_categories():
        results = get_categories()
        j = []

        for i in range(len(results)):
            with open(f"category_images/{str(results[i][0])}.png", "rb") as f:
                category_image = base64.b64encode(f.read()).decode('utf-8')

            j.append({
                "categoryId": str(results[i][0]),
                "categoryName": results[i][1],
                "CategoryImage": "data:image/png;base64," + category_image
            })

        return jsonify(j)

    @app.route('/get-prediction-graph', methods=['GET'])
    def get_prediction_graph():
        category_id = request.args.get('categoryId', "")
        freq = request.args.get('freq', "")
        if not category_id:
            return jsonify({ "error": "No category id provided" })
        elif not category_id.isdigit():
            return jsonify({ "error": "Category id must be a number" })

        if not freq:
            return jsonify({ "error": "No frequency provided" })
        elif freq.isdigit():
            return jsonify({ "error": "Frequency must not be a number" })

        results = get_prediction_graph_by_id(category_id, freq)
        if not results:
            return jsonify({ "error": "No predictions found" })

        graph_res = results[0]
        category_name = results[1]

        ret = {
            "CategoryName": category_name,
            "GraphImage": base64.b64encode(graph_res).decode('utf-8')
        }
        return jsonify(ret), 200

    @app.route('/category-to-predict', methods=['GET'])
    def category_to_predict():
        category_id = request.args.get('categoryId', "")
        if not category_id or category_id == "":
            return jsonify({ "error": "No category id provided" }), 400
        elif not category_id.isdigit():
            return jsonify({ "error": "Category id must be a number" }), 400

        data_to_insert = []
        page = 0

        while True:
            page += 1
            resp = api.execute('findItemsByCategory', {
                "categoryId": category_id,
                'paginationInput': {
                    'entriesPerPage': 100,
                    'pageNumber': page
                }
            })

            data = resp.dict()
            items = data.get('searchResult', {})

            if not items:
                break

            items = items.get('item', [])
            for item in items:
                if item['primaryCategory']['categoryName']:
                    data_to_insert.append((
                        item['itemId'],
                        category_id,
                        item['title'],
                        item['sellingStatus']['currentPrice']['value'],
                        item['listingInfo']['startTime'],
                        item['primaryCategory']['categoryName']
                    ))

            total_pages = int(data.get("paginationOutput").get("totalPages"))
            if page >= total_pages:
                break

        if not data_to_insert:
            return jsonify({ "error": "Couldn't collect any data for the given category id" }), 404

        # insert all the data to db
        insert_products(data_to_insert)

        return jsonify({ "message": "success" })

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", port=5001)
    
