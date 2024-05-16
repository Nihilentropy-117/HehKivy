import os

import cohere
import psycopg2
import gradio as gr
import tomli
import tomli_w
from sync_notes import sync as syncnotes
from search import search as searchnotes


# List of embedding models to choose from
from embedding_models import embedding_models_list
# Configuration file name
settings_file = "conf.toml"

with open(settings_file, "rb") as f: default_settings = tomli.load(f)

# Initialize settings with default values
settings = default_settings.copy()


def sync_notes(status_bar):
    status_messages = []

    def update_status(text):
        status_messages.append(text)
        return "\n".join(status_messages)

    vaults = [os.path.join(settings["notes_directory"], d) for d in os.listdir(settings["notes_directory"]) if
              os.path.isdir(os.path.join(settings["notes_directory"], d)) and not d.startswith('.')]
    for vault in vaults:
        syncnotes(settings["active_embedding_model"], vault, update_status)
    return update_status("Notes synced successfully!")


def save_config(embedding_model, notes_directory):
    settings["active_embedding_model"] = embedding_model
    settings["notes_directory"] = notes_directory
    with open(settings_file, "wb") as f:
        tomli_w.dump(settings, f)
    return "Settings saved to conf.toml"





# Connect to PostgreSQL database
def get_table_names():
    # Load database configuration from TOML file
    with open("conf.toml", "rb") as f:
        config = tomli.load(f)
    db_config = config["db_config"]
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema='public'
    """)
    tables = cur.fetchall()
    conn.close()
    return [table[0] for table in tables]


def load_config():
    try:
        with open(settings_file, "rb") as f:
            global settings
            settings = tomli.load(f)
        return settings["active_embedding_model"], settings["notes_directory"], "Settings loaded from conf.toml"
    except FileNotFoundError:
        return default_settings["active_embedding_model"], default_settings[
            "notes_directory"], "conf.toml not found. Using default settings."
table_names = get_table_names()

import collections
# Function to handle search and return results
def handle_search(query, selected_tables, limit, embedding_model):
    return format_result_tables(
        searchnotes(query=query, tables=selected_tables, limit=limit, embedding_model=embedding_model))


tools = [
    {
        "name": "query_user_database",
        "description": "Searches the user content database for relevant information.",
        "parameter_definitions": {
            "search_terms": {
                "description": "Terms to search for in the user content database.",
                "type": "str",
                "required": True
            }
        }
    }
]

preamble = """
## Task & Context
You help people answer their questions and other requests interactively. You will be asked a very wide array of requests on all kinds of topics. You will be equipped with a wide range of search engines or similar tools to help you, which you use to research your answer. You should focus on serving the user's needs as best you can, which will be wide-ranging.

## Style Guide
Unless the user asks for a different style of answer, you should answer in full sentences, using proper grammar and spelling.
"""
co = cohere.Client(settings["cohere_api_key"])


def respond(message, chat_history, tables, limit=10):
    response = co.chat(
        message=message,
        tools=tools,
        preamble=preamble,
        model="command-r"
    )

    tool_calls = response.tool_calls
    if tool_calls:
        tool_results = []
        for tool_call in tool_calls:
            search_terms = tool_call.parameters['search_terms']
            search_result = handle_search(query=search_terms, selected_tables=tables, limit=limit,
                                          embedding_model='model_name')

            # Changed lines
            outputs = [{"search_result": search_result}]
            tool_results.append({
                "call": tool_call,
                "outputs": outputs
            })

        final_response = co.chat(
            message=message,
            tools=tools,
            tool_results=tool_results,
            preamble=preamble,
            model="command-r",
            temperature=0.3
        )
        bot_message = final_response.text
    else:
        bot_message = "I'm not sure how to help with that."

    chat_history.append((message, bot_message))
    return "", chat_history

def format_result_tables(result_tables):
    formatted_string = ""

    for table, results in sorted(result_tables.items()):
        formatted_string += f"# {table}\n"

        # Organize the results by original_filename and part_number
        sorted_results = collections.defaultdict(list)
        for result in results:
            original_filename = result["original_filename"]
            part_number = result["part_number"]
            text = result["text"]
            sorted_results[(original_filename, part_number)].append(text)

        # Sort by original_filename, then by part_number
        sorted_keys = sorted(sorted_results.keys(), key=lambda x: (x[0], int(x[1]) if x[1].isdigit() else x[1]))

        current_filename = None
        for (original_filename, part_number) in sorted_keys:
            if current_filename != original_filename:
                current_filename = original_filename
                formatted_string += f"\n## {original_filename}\n"

            formatted_string += f"\n### Part {part_number}\n"
            for text in sorted_results[(original_filename, part_number)]:
                formatted_string += f"{text}\n"

        formatted_string += "\n"

    return formatted_string


with gr.Blocks() as demolition:
    with gr.Tab("Sync Notes"):
        status_bar = gr.Textbox(label="Status", interactive=False)
        sync_button = gr.Button("Sync Notes to Database")
        sync_button.click(sync_notes, inputs=status_bar, outputs=status_bar)

    with gr.Tab("Search"):
        multiselect = gr.Dropdown(label="Select Tables", choices=table_names, multiselect=True)
        query_input = gr.Textbox(label="Enter Query")
        limit_input = gr.Slider(label="Limit", minimum=1, maximum=100, step=1, value=5)
        embedding_model_input = gr.Dropdown(label="Select Embedding Model", choices=embedding_models_list, value="GTELargeEnV15")
        search_button = gr.Button("Search")
        response_output = gr.Markdown(label="Response")

        search_button.click(
            fn=handle_search,
            inputs=[query_input, multiselect, limit_input, embedding_model_input],
            outputs=response_output
        )


    with gr.Tab("Chat"):
        chatbot = gr.Chatbot()
        msg = gr.Textbox()
        clear = gr.ClearButton([msg, chatbot])

        chat_select_tables = gr.Dropdown(label="Select Tables", choices=table_names, multiselect=True)
        chat_select_limit = gr.Slider(label="Limit", minimum=1, maximum=100, step=1, value=5)

        msg.submit(respond, [msg, chatbot, chat_select_tables, chat_select_limit], [msg, chatbot])


    with gr.Tab("Settings"):
        embedding_model = gr.Dropdown(choices=embedding_models_list, label="Embedding Model")
        notes_directory = gr.Textbox(label="Notes Directory")
        save_button = gr.Button("Save Settings")
        load_button = gr.Button("Load Settings")
        status = gr.Textbox(label="Status", interactive=False)

        save_button.click(save_config, [embedding_model, notes_directory], outputs=status)
        load_button.click(load_config, outputs=[embedding_model, notes_directory, status])



demolition.launch()
