import psycopg2.extras
import tomli

from embedding_models import load_embedding_model
import psycopg2.sql as sql





def search(query=None, tables=None, limit=5, embedding_model="GTELargeEnV15"):

    if query is None:
        query = "The majestic eagle soared through the clear blue sky, its wings outstretched as it rode the thermals."

    result_tables = {}
    try:
        with open("conf.toml", "rb") as f:
            config = tomli.load(f)

        conn = psycopg2.connect(**config["db_config"])  # Establish DB connection
        cur = conn.cursor()  # Create a cursor object

        for table in tables:
            if table == "wikipedia":
                active_embedding_model = load_embedding_model('cohere-embed-multilingual-v3.0')
            else:
                active_embedding_model = load_embedding_model("GTELargeEnV15")
            query_embedding = active_embedding_model.embed(query)

            search_sql = sql.SQL("""
                    SELECT original_filename, md5, date_updated, source, source_type, part_number, text, embedding, (embedding <=> CAST(%s AS vector)) AS similarity
                    FROM {}
                    ORDER BY similarity ASC
                    LIMIT %s;
                """).format(sql.Identifier(table))

            # Execute the query with the query embedding cast to vector and the limit value
            cur.execute(search_sql, [query_embedding, limit])

            # Fetch all results
            results = cur.fetchall()

            # Convert results to a list of dictionaries
            columns = ["original_filename", "md5", "date_updated", "source", "source_type", "part_number", "text",
                       "embedding"]
            result_dicts = [dict(zip(columns, row)) for row in results]

            result_tables[table] = result_dicts


    except psycopg2.DatabaseError as e:
        print(f"Database error: {e}")

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


    return result_tables

if __name__ == "__main__":
    results = search()

    for result_table in results:
        for result in results[result_table]:
            print(result)
