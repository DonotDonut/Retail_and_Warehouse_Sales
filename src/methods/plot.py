import psycopg2
import matplotlib.pyplot as plt


class Plot:
    @staticmethod
    def plot_retail_sales_by_month_year(
        database_username,
        database_password,
        database_host,
        database_port,
        database_name,
        table_name
    ):
        """
        Line chart: total retail sales by month, with one line per year.
        Requires columns: "year", "month", "retail sales"
        """
        conn = psycopg2.connect(
            host=database_host,
            port=database_port,
            dbname=database_name,
            user=database_username,
            password=database_password
        )

        try:
            with conn.cursor() as cur:
                cur.execute(f"""
                    SELECT "year", "month", SUM("retail sales") AS total_retail_sales
                    FROM public.{table_name}
                    GROUP BY "year", "month"
                    ORDER BY "year", "month";
                """)
                rows = cur.fetchall()

            if not rows:
                print("No data returned for retail sales by month/year.")
                return

            # Build year -> {month -> total} mapping
            year_to_months = {}
            for y, m, total in rows:
                year_to_months.setdefault(y, {})[m] = float(total)

            months = list(range(1, 13))

            plt.figure()
            for y in sorted(year_to_months.keys()):
                values = [year_to_months[y].get(m, 0.0) for m in months]
                plt.plot(months, values, marker="o", label=str(y))

            plt.xlabel("Month")
            plt.ylabel("Total Retail Sales (units)")
            plt.title("Retail Sales by Month (One Line per Year)")
            plt.xticks(months)
            plt.legend()
            plt.tight_layout()
            plt.show()

        finally:
            conn.close()

    @staticmethod
    def plot_item_type_sold_more_often(
        database_username,
        database_password,
        database_host,
        database_port,
        database_name,
        table_name,
        top_n
    ):
        """
        Stacked bar chart:
        - X axis: Item Type
        - Y axis: Retail Sales (units)
        - Each bar is stacked by year
        - Total units shown on top of each bar
        """

        import psycopg2
        import matplotlib.pyplot as plt
        from collections import defaultdict

        conn = psycopg2.connect(
            host=database_host,
            port=database_port,
            dbname=database_name,
            user=database_username,
            password=database_password
        )

        try:
            with conn.cursor() as cur:
                # Get top N item types overall
                cur.execute(f"""
                    SELECT "item type"
                    FROM public.{table_name}
                    GROUP BY "item type"
                    ORDER BY SUM("retail sales") DESC
                    LIMIT %s;
                """, (top_n,))
                item_types = [r[0] for r in cur.fetchall()]

                # Get retail sales broken out by year for those item types
                cur.execute(f"""
                    SELECT "item type", "year", SUM("retail sales") AS units
                    FROM public.{table_name}
                    WHERE "item type" = ANY(%s)
                    GROUP BY "item type", "year"
                    ORDER BY "year";
                """, (item_types,))
                rows = cur.fetchall()

            if not rows:
                print("No data returned.")
                return

            # Organize data: item_type -> year -> units
            data = defaultdict(dict)
            years = set()

            for item_type, year, units in rows:
                data[item_type][year] = float(units)
                years.add(year)

            years = sorted(years)
            item_types = list(data.keys())

            # Plot
            plt.figure(figsize=(12, 6))

            bottom = [0] * len(item_types)

            for year in years:
                values = [data[it].get(year, 0) for it in item_types]
                bars = plt.bar(item_types, values, bottom=bottom, label=str(year))
                bottom = [bottom[i] + values[i] for i in range(len(values))]

            # ---- ADD TOTAL VALUE LABELS ON TOP ----
            for i, total in enumerate(bottom):
                if total > 0:
                    plt.text(
                        i,
                        total,
                        f"{int(total):,}",
                        ha="center",
                        va="bottom",
                        fontsize=9,
                        fontweight="bold"
                    )

            plt.xlabel("Item Type")
            plt.ylabel("Total Retail Sales (units)")
            plt.title(f"Top {top_n} Item Types by Retail Sales (Stacked by Year)")
            plt.xticks(rotation=45, ha="right")
            plt.legend(title="Year")
            plt.tight_layout()
            plt.show()

        finally:
            conn.close()
