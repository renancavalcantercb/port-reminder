import pandas as pd
from datetime import datetime, timedelta
from discord import Embed


import pandas as pd
from datetime import datetime, timedelta
from discord import Embed


async def list_stars(ctx):
    CSV_URL = "https://docs.google.com/spreadsheets/d/1ctBuqO42ZYYheuEIsbJO1NFPAJsoMrJv9oWxyhsBH9g/export?format=csv&gid=1852026355"

    try:
        # Carrega o CSV
        df = pd.read_csv(CSV_URL)

        # Verifica se as colunas esperadas existem
        required_columns = ["World", "Region", "Time", "Size"]
        if not all(column in df.columns for column in required_columns):
            await ctx.send("The sheet is updating. Please try again later.")
            return

        # Filtra os dados
        df = df[df["Region"].notna()]
        df["Time"] = pd.to_datetime(df["Time"], format="%H:%M", errors="coerce").dt.time
        df = df[df["Time"].notna()]

        # Hora atual em UTC
        utc_now = datetime.utcnow()

        # Filtra os horários futuros
        df = df[df["Time"].apply(lambda x: x > utc_now.time())]

        # Extrai números da coluna "Size" e mantém apenas S10 e S9
        df["Size_num"] = pd.to_numeric(
            df["Size"].str.extract(r"S(\d+)", expand=False), errors="coerce"
        )
        df = df[df["Size_num"].isin([10, 9])]

        # Ordena por tamanho e calcula o tempo restante
        df = df.sort_values(by="Size_num", ascending=False)

        def calculate_time_remaining(event_time):
            event_datetime = datetime.combine(utc_now.date(), event_time)
            if event_datetime < utc_now:
                event_datetime += timedelta(days=1)
            delta = event_datetime - utc_now
            hours, remainder = divmod(int(delta.total_seconds()), 3600)
            minutes, _ = divmod(remainder, 60)
            return f"{hours}h {minutes}m"

        df["Time_remaining"] = df["Time"].apply(calculate_time_remaining)

        # Verifica se há resultados
        if df.empty:
            await ctx.send("No available stars of S10 or S9.")
            return

        # Cria o embed
        embed = Embed(title="Upcoming Stars (S10 and S9)", color=0x1F8B4C)
        for _, row in df.iterrows():
            embed.add_field(
                name=f"{row['Size']} - {row['Region']}",
                value=(
                    f"**World:** {row['World']} | "
                    f"**Time Remaining:** {row['Time_remaining']} | "
                    f"**Time:** {row['Time']}"
                ),
                inline=False,
            )

        footer = "Made by @CuTGuArDiAn"
        embed.set_footer(text=footer)

        # Envia o embed
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"An error occurred while processing the command: {e}")
