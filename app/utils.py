import pandas as pd
import logging
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
        df["Size_num"] = pd.to_numeric(
            df["Size"].str.extract(r"S(\d+)", expand=False), errors="coerce"
        )

        utc_now = datetime.utcnow()
        df = df[df["Time"].apply(lambda x: x > utc_now.time())]

        def calculate_time_remaining(event_time):
            event_datetime = datetime.combine(utc_now.date(), event_time)
            if event_datetime < utc_now:
                event_datetime += timedelta(days=1)
            delta = event_datetime - utc_now
            return delta.total_seconds() // 60

        df["Time_remaining"] = df["Time"].apply(calculate_time_remaining)

        def filter_by_size(df, sizes):
            for size in sizes:
                filtered = df[df["Size_num"] == size]
                if not filtered.empty:
                    return filtered
            return pd.DataFrame(columns=df.columns)

        df_filtered = filter_by_size(df, sizes=[10, 9])

        df_filtered = df_filtered.sort_values(
            by=["Size_num", "Time_remaining"], ascending=[False, True]
        )

        return df_filtered, None
    except Exception as e:
        return None, f"An error occurred while processing the data: {e}"


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("discord_bot.log"),
        logging.StreamHandler(),
    ],
)


def log_event(level: str, message: str, **kwargs):
    if kwargs:
        extra_info = " | ".join(f"{key}: {value}" for key, value in kwargs.items())
        message = f"{message} | {extra_info}"

    log_level_dict = {
        "info": logging.info,
        "warning": logging.warning,
        "error": logging.error,
        "debug": logging.debug,
    }

    log_func = log_level_dict.get(level.lower(), logging.info)
    log_func(message)
