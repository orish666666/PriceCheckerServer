from io import BytesIO

import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

import numpy as np

from flaskr.query.query import get_products, insert_predictions, delete_predictions


def main():
    data_to_insert = []
    data = get_products()
    df = pd.DataFrame(data, columns=['category_id', 'category_name', 'price', 'date'])
    periods = {
        "h": 24,
        "D": 7,
        "W": 4,
        "ME": 12
    }

    # grouping the data by each category id
    grouped_data = df.groupby('category_id')

    for category_id, group_df in grouped_data:
        for freq, period in periods.items():
            print("Predicting for category:", category_id, "on", freq)
            train_data = []
            category_name = ""
            # get only the price and date on the products
            for i, row in group_df.iterrows():
                if category_name == "" and row.category_name:
                    category_name = row.category_name
                train_data.append((row.price, row.date))

            df_train = pd.DataFrame(train_data, columns=['y', 'ds'])

            # Apply log transform to prevent negative values
            df_train['y'] = df_train['y'].astype(float)
            df_train['y'] = df_train['y'].apply(lambda x: max(x, 1))  # avoid log(0) or negative
            df_train['y'] = np.log(df_train['y'])

            df_train['ds'] = pd.to_datetime(df_train['ds'], utc=True)

            # prophet doesn't like timezone in the date so just localizing it and removing it
            df_train['ds'] = df_train['ds'].dt.tz_localize(None)

            m = Prophet()
            m.fit(df_train)

            # predict a specific period of time
            future = m.make_future_dataframe(periods=period, freq=freq)
            forecast = m.predict(future)
            last_date = df_train['ds'].max()

            # get only prediction of a specific period of time
            future_predictions = forecast[forecast['ds'] > last_date]

            dates = future_predictions['ds']
            # Apply exponential but clip extreme predictions
            prices = np.exp(future_predictions['yhat'].clip(upper=9.6))  # limit to 10,000

            # create the graph
            plt.figure(figsize=(10, 5))
            plt.plot(dates, prices)

            plt.xlabel('Date (YYYY-MM)')
            plt.ylabel('Price ($)')
            plt.ticklabel_format(style='plain', axis='y')  # disable scientific notation on y-axis

            # add ',' to make numbers more readable
            plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))

            plt.title(f'{period}-{freq} Graph')
            plt.xticks(rotation=20)
            plt.tight_layout()

            image_raw = BytesIO()
            plt.savefig(image_raw, format='png')
            image_raw.seek(0)

            data_to_insert.append((str(category_id), category_name, freq, image_raw.getvalue()))

    delete_predictions()
    insert_predictions(data_to_insert)


if __name__ == '__main__':
    main()

