from io import BytesIO
import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from flaskr.query.query import get_products, insert_predictions, delete_predictions


def main():
    data_to_insert = []
    data = get_products()

    df = pd.DataFrame(data, columns=['category_id', 'category_name', 'price', 'date'])

    periods = {
        "h": 24,  # day
        "D": 7,   # week
        "W": 4,   # month
        "ME": 12  # year
    }

    grouped_data = df.groupby('category_id')

    for category_id, group_df in grouped_data:
        # prepare data
        df_train = group_df[['price', 'date']].copy()
        df_train.columns = ['y', 'ds']
        df_train['y'] = pd.to_numeric(df_train['y'], errors='coerce')
        df_train['ds'] = pd.to_datetime(df_train['ds'], utc=True).dt.tz_localize(None)
        df_train = df_train.dropna().sort_values('ds')

        if df_train.empty:
            continue

        category_name = group_df['category_name'].iloc[0]

        for freq, period in periods.items():
            m = Prophet(
                yearly_seasonality=False,
                weekly_seasonality=False,
                daily_seasonality=False,
                changepoint_prior_scale=0.05
            )
            m.fit(df_train)

            # predict
            future = m.make_future_dataframe(periods=period, freq=freq)
            forecast = m.predict(future)

            # filter to show only the future prediction
            last_historical_date = df_train['ds'].max()
            plot_data = forecast[forecast['ds'] >= last_historical_date]

            # generate the graph
            fig, ax = plt.subplots(figsize=(10, 5))

            # create the line
            ax.plot(plot_data['ds'], plot_data['yhat'].clip(lower=0),
                    color='#007bff', linewidth=2, marker='o', markersize=4)

            # prevent overlapping text
            locator = mdates.AutoDateLocator()
            ax.xaxis.set_major_locator(locator)
            ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))

            # format price to $
            ax.yaxis.set_major_formatter(mticker.StrMethodFormatter('${x:,.0f}'))

            plt.title(f"Price Prediction: {category_name} ({period}{freq})")
            plt.grid(True, linestyle='--', alpha=0.5)
            plt.tight_layout()

            # save
            image_raw = BytesIO()
            plt.savefig(image_raw, format='png')
            image_raw.seek(0)
            plt.close(fig)

            data_to_insert.append((str(category_id), category_name, freq, image_raw.getvalue()))

    delete_predictions()
    insert_predictions(data_to_insert)


if __name__ == '__main__':
    main()
