import datetime
import os
import hashlib
import re
import psycopg2
from embedding_models import load_embedding_model
import tomli


def sync(model, notes_directory, update_status_callback):
    vault = notes_directory.split("/")[-1]  # Extract vault name from directory path

    # Update status bar and print status
    def update_status(text):
        print(text)
        update_status_callback(text)


    with open("conf.toml", "rb") as f:
        config = tomli.load(f)

    conn = psycopg2.connect(**config["db_config"])  # Establish DB connection
    cur = conn.cursor()  # Create a cursor object

    # Create a table if it doesn't exist
    def create_table():
        cur.execute(f"""
            CREATE TABLE {vault} (
                id SERIAL PRIMARY KEY,
                original_filename TEXT,
                md5 VARCHAR(255),
                date_updated TEXT,
                part_number TEXT,
                embedding vector(1024),
                embedding_model VARCHAR(255),
                source TEXT,
                source_type TEXT,
                author TEXT,
                text TEXT
            )
        """)
        cur.execute(f"ALTER TABLE {vault} ALTER COLUMN embedding SET STORAGE PLAIN")
        cur.execute(f"CREATE INDEX ON {vault} USING ivfflat (embedding vector_cosine_ops)")
        conn.commit()


    # Process a file and update database
    def process_file(file_path, embedding_model):
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()  # Read file content
            content = re.sub(r"^---\n.*?\n---\n", "", content, flags=re.DOTALL)  # Remove front matter
            if len(content) < 10:
                return

            md5_hash = hashlib.md5(content.encode("utf-8")).hexdigest()  # Compute MD5 hash
            parts = content.split("\n\n")  # Split content into parts
            date_modified = datetime.datetime.now()  # Get current date and time
            source_type = "Note"
            relative_path = os.path.relpath(file_path, notes_directory)  # Get relative file path

            # Check if file already exists in database
            cur.execute(f"SELECT md5 FROM {vault} WHERE original_filename = %s", (relative_path,))
            result = cur.fetchone()

            if result and result[0] == md5_hash:
                return "existing"
            elif result:
                cur.execute(f"DELETE FROM {vault} WHERE original_filename = %s", (relative_path,))
                insert_parts(relative_path, parts, md5_hash, date_modified, file_path, source_type, embedding_model)
                return "modified"
            else:
                insert_parts(relative_path, parts, md5_hash, date_modified, file_path, source_type, embedding_model)
                return "new"

    # Insert parts of a file into the database
    def insert_parts(relative_path, parts, md5_hash, date_modified, source, source_type, embedding_model):
        for i, part in enumerate(parts):
            embedding = embedding_model.embed(part)  # Get embedding for part
            cur.execute(
                f"INSERT INTO {vault} (original_filename, md5, date_updated, source, source_type, part_number, text, embedding) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (relative_path, md5_hash, date_modified, source, source_type, i, part, embedding)
            )

    # Remove files from database that no longer exist
    def remove_deleted_files():
        cur.execute(f"SELECT original_filename FROM {vault}")
        db_files = [row[0] for row in cur.fetchall()]
        for db_file in db_files:
            full_path = os.path.join(notes_directory, db_file)
            if not os.path.exists(full_path):
                cur.execute(f"DELETE FROM {vault} WHERE original_filename = %s", (db_file,))

    # Walk through the directory and process each file
    def walk_directory(directory, embedding_model):
        total_files = sum(1 for root, dirs, files in os.walk(directory) for file in files if
                          file.endswith(".md") and not file.startswith("."))
        i = 1
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for file in files:
                if file.endswith(".md") and not file.startswith("."):
                    file_path = os.path.join(root, file)
                    status = process_file(file_path, embedding_model)
                    if status:
                        update_status(f"{i}/{total_files}: File {file} was {status}.")
                    else:
                        update_status(f"{i}/{total_files}: File {file} was not.")
                    i += 1

    # Check if table exists and create if not
    if not (lambda: (
            cur.execute(f"SELECT to_regclass('{vault}')")
            or
            cur.fetchone()[0] is not None))():
        create_table()

    embedding_model = load_embedding_model(model)  # Load embedding model
    walk_directory(notes_directory, embedding_model)  # Process files in directory
    remove_deleted_files()  # Remove deleted files from database
    embedding_model.unload()  # Unload the embedding model

    conn.commit()  # Commit changes
    cur.close()  # Close cursor
    conn.close()  # Close connection
