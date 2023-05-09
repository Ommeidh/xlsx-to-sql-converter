import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
import os
import json
import datetime
import attributes
import pyperclip

CONFIG_FILE = 'config.json'

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def process_file_path():
    file_path = file_path_entry.get()
    output_folder = output_folder_entry.get()
    server = server_entry.get()
    username = username_entry.get()
    password = password_entry.get()
    database = database_entry.get()

    try:
        column_b_mappings = attributes.read_config()
        update_statements = attributes.generate_sql_script(file_path, column_b_mappings, server, username, password, database)
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        output_file_path = os.path.join(output_folder, f'sql_scripts_{timestamp}.sql')
        attributes.save_sql(update_statements, output_file_path)

        config = {
            'file_path': file_path,
            'output_folder': output_folder
        }
        save_config(config)

        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "\n".join(update_statements))
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def select_file():
    file_path = filedialog.askopenfilename()
    file_path_entry.delete(0, tk.END)
    file_path_entry.insert(0, file_path)

def select_output_folder():
    output_folder = filedialog.askdirectory()
    output_folder_entry.delete(0, tk.END)
    output_folder_entry.insert(0, output_folder)

def select_all(event):
    result_text.tag_add(tk.SEL, "1.0", tk.END)
    result_text.mark_set(tk.INSERT, "1.0")
    result_text.mark_set(tk.INSERT, tk.END)
    return "break"

def copy_to_clipboard():
    selected_text = result_text.selection_get()
    pyperclip.copy(selected_text)

root = tk.Tk()
root.title("Account Type Fixer")

config = load_config()

file_path_label = tk.Label(root, text="File path:")
file_path_label.pack()

file_path_entry = tk.Entry(root, width=50)
file_path_entry.insert(0, config.get('file_path', ''))
file_path_entry.pack()

select_file_button = tk.Button(root, text="Select File", command=select_file)
select_file_button.pack()

output_folder_label = tk.Label(root, text="Output folder:")
output_folder_label.pack()

output_folder_entry = tk.Entry(root, width=50)
output_folder_entry.insert(0, config.get('output_folder', ''))
output_folder_entry.pack()

select_output_folder_button = tk.Button(root, text="Select Output Folder", command=select_output_folder)
select_output_folder_button.pack()

# Add Server, Username, Password, and Database input fields
server_label = tk.Label(root, text="Server:")
server_label.pack()
server_entry = tk.Entry(root, width=50)
server_entry.pack()

username_label = tk.Label(root, text="Username:")
username_label.pack()
username_entry = tk.Entry(root, width=50)
username_entry.pack()

password_label = tk.Label(root, text="Password:")
password_label.pack()
password_entry = tk.Entry(root, width=50, show='*')
password_entry.pack()

database_label = tk.Label(root, text="Database:")
database_label.pack()
database_entry = tk.Entry(root, width=50)
database_entry.pack()

process_button = tk.Button(root, text="Process file", command=process_file_path)
process_button.pack()

copy_button = tk.Button(root, text="Copy to clipboard", command=copy_to_clipboard)
copy_button.pack()

result_text = tk.Text(root, wrap=tk.WORD, width=80, height=20)
result_text.pack()

result_text.bind("<Control-a>", select_all)
result_text.bind("<Control-A>", select_all)

root.mainloop()
