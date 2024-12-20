import pandas as pd
from datetime import datetime, timedelta

CSV_URL = "https://docs.google.com/spreadsheets/d/1ctBuqO42ZYYheuEIsbJO1NFPAJsoMrJv9oWxyhsBH9g/export?format=csv&gid=1852026355"


async def get_star_data():
    try:
        df = pd.read_csv(CSV_URL)

        required_columns = ["World", "Region", "Time", "Size"]
        if not all(column in df.columns for column in required_columns):
            return None, "The sheet is updating. Please try again later."

        df = df[df["Region"].notna()]
        df["Time"] = pd.to_datetime(df["Time"], format="%H:%M", errors="coerce").dt.time
        df = df[df["Time"].notna()]

        utc_now = datetime.utcnow()

        df = df[df["Time"].apply(lambda x: x > utc_now.time())]

        df["Size_num"] = pd.to_numeric(
            df["Size"].str.extract(r"S(\d+)", expand=False), errors="coerce"
        )
        df = df[df["Size_num"].isin([10, 9])]

        df = df.sort_values(by="Size_num", ascending=False)

        def calculate_time_remaining(event_time):
            event_datetime = datetime.combine(utc_now.date(), event_time)
            if event_datetime < utc_now:
                event_datetime += timedelta(days=1)
            delta = event_datetime - utc_now
            hours, remainder = divmod(int(delta.total_seconds()), 3600)
            minutes, _ = divmod(remainder, 60)
            return hours * 60 + minutes

        df["Time_remaining"] = df["Time"].apply(calculate_time_remaining)

        return df, None
    except Exception as e:
        return None, f"An error occurred while processing the data: {e}"
