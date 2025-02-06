from google.cloud import bigquery
from google.oauth2 import service_account
import uuid

from os import getenv

credentials = service_account.Credentials.from_service_account_file(
    getenv("GOOGLE_APPLICATION_CREDENTIALS")
)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

DATASET_ID = "estudos-444305.discord"
TABLE_TIMERS = "timers"
TABLE_STAR_NOTIFICATIONS = "star_notifications"
TABLE_CURSE_WORD_COUNTERS = "curse_word_counters"


async def add_timer(user_id, channel_id, ship_name, timer_end):
    query = f"""
        INSERT INTO `{DATASET_ID}.{TABLE_TIMERS}` (id, user_id, channel_id, ship_name, timer_end, notified)
        VALUES (@id, @user_id, @channel_id, @ship_name, @timer_end, FALSE)
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("id", "STRING", str(uuid.uuid4())),
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("channel_id", "STRING", channel_id),
            bigquery.ScalarQueryParameter("ship_name", "STRING", ship_name),
            bigquery.ScalarQueryParameter("timer_end", "TIMESTAMP", timer_end),
        ]
    )
    query_job = client.query(query, job_config=job_config)
    query_job.result()  # Espera a conclusão da query


async def get_active_timers(user_id):
    query = f"""
        SELECT ship_name, timer_end
        FROM `{DATASET_ID}.{TABLE_TIMERS}`
        WHERE user_id = @user_id and notified is FALSE
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
        ]
    )
    query_job = client.query(query, job_config=job_config)
    rows = query_job.result()
    return [dict(row) for row in rows]


async def get_expired_timers(current_time):
    query = f"""
        SELECT id, user_id, channel_id, ship_name
        FROM `{DATASET_ID}.{TABLE_TIMERS}`
        WHERE timer_end <= @current_time AND notified = FALSE
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("current_time", "TIMESTAMP", current_time),
        ]
    )
    query_job = client.query(query, job_config=job_config)
    rows = query_job.result()
    return [dict(row) for row in rows]


async def mark_timer_notified(timer_id):
    query = f"""
        UPDATE `{DATASET_ID}.{TABLE_TIMERS}`
        SET notified = TRUE
        WHERE id = @timer_id
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("timer_id", "STRING", timer_id),
        ]
    )
    query_job = client.query(query, job_config=job_config)
    query_job.result()


async def register_user(user_id, username):
    query = f"""
        INSERT INTO `{DATASET_ID}.{TABLE_STAR_NOTIFICATIONS}` (user_id, username)
        VALUES (@user_id, @username)
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "INT64", user_id),
            bigquery.ScalarQueryParameter("username", "STRING", username),
        ]
    )
    query_job = client.query(query, job_config=job_config)
    query_job.result()
    return f"{username} has been registered for star notifications!"


async def get_registered_users():
    query = f"""
        SELECT user_id, username
        FROM `{DATASET_ID}.{TABLE_STAR_NOTIFICATIONS}`
    """
    query_job = client.query(query)
    rows = query_job.result()
    return [dict(row) for row in rows]


async def delete_user(user_id):
    query = f"""
        DELETE FROM `{DATASET_ID}.{TABLE_STAR_NOTIFICATIONS}`
        WHERE user_id = @user_id
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "INT64", user_id),
        ]
    )
    query_job = client.query(query, job_config=job_config)
    query_job.result()
    return f"User with ID {user_id} has been deleted from notifications."


async def add_or_update_curse_counter(emoji, name):
    """
    Se o emoji já existir na tabela, incrementa o contador.
    Caso contrário, insere um novo registro com count = 1.
    """
    query = f"""
        MERGE `{DATASET_ID}.{TABLE_CURSE_WORD_COUNTERS}` AS target
        USING (SELECT @name AS name, 1 AS count) AS source
        ON SAFE_CAST(target.name AS STRING) = SAFE_CAST(source.name AS STRING)
        WHEN MATCHED THEN
            UPDATE SET count = target.count + 1
        WHEN NOT MATCHED THEN
            INSERT (emoji, name, count, created_at)
            VALUES (@emoji, @name, source.count, CURRENT_TIMESTAMP());
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("emoji", "STRING", emoji),
            bigquery.ScalarQueryParameter("name", "STRING", name),
        ]
    )
    query_job = client.query(query, job_config=job_config)
    query_job.result()


async def undo_last_curse_counter():
    """
    Reduz o contador da última entrada modificada.
    Se o contador for maior que 0, decrementa em 1.
    """
    query = f"""
        SELECT emoji, name, count
        FROM `{DATASET_ID}.{TABLE_CURSE_WORD_COUNTERS}`
        WHERE count > 0
        ORDER BY created_at DESC
        LIMIT 1
    """
    query_job = client.query(query)
    rows = list(query_job.result())

    if rows:
        row = rows[0]
        emoji, name, count = row["emoji"], row["name"], row["count"]

        if count > 0:
            update_query = f"""
                UPDATE `{DATASET_ID}.{TABLE_CURSE_WORD_COUNTERS}`
                SET count = count - 1
                WHERE emoji = @emoji
            """
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("emoji", "STRING", emoji),
                ]
            )
            update_job = client.query(update_query, job_config=job_config)
            update_job.result()

            return emoji, name, count - 1
    return None


async def get_curse_counters(name=None):
    query = f"""
        SELECT emoji, name, count
        FROM `{DATASET_ID}.{TABLE_CURSE_WORD_COUNTERS}`
        WHERE (@name IS NULL OR name = @name)
        ORDER BY count DESC
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("name", "STRING", name)
        ]
    )

    query_job = client.query(query, job_config=job_config)
    rows = query_job.result()

    return [dict(row) for row in rows]