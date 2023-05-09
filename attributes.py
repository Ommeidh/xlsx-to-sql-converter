import pandas as pd
import os
import configparser
import pymssql

def read_config(config_file=None):
    if config_file is None:
        config_file = os.path.join(os.getcwd(), 'config.ini')

    config = configparser.ConfigParser()
    with open(config_file, "r", encoding="utf-8-sig") as f:
        config.read_file(f)
    column_b_mappings = dict(config.items("COLUMN_B_MAPPINGS"))
    print("Column B Mappings:", column_b_mappings)
    return column_b_mappings

def get_current_data(server, username, password, database):
    with pymssql.connect(server, username, password, database) as conn:
        with conn.cursor(as_dict=True) as cursor:
            cursor.execute('SELECT * FROM core.AccountType')
            rows = cursor.fetchall()
            return {row['CoreName']: row for row in rows}

def generate_sql_script(file_path, column_b_mappings, server, username, password, database):
    df = pd.read_excel(file_path, header=None, engine='openpyxl')
    current_data = get_current_data(server, username, password, database)
    update_statements = []

    for idx_g, value_g in df[6].dropna().items():
        if idx_g < 3:  # Skip the first three rows
            continue

        current_row = current_data.get(value_g)
        if current_row is None:
            continue

        update_fields = []

        for idx, row in df.iterrows():
            if idx < 3:  # Skip the first three rows
                continue

            column_b = row[1]
            column_d = row[3]
            column_e = row[4]

            if not isinstance(column_b, str):  # Ensure column B value is a string
                continue

            db_value = column_b_mappings.get(column_b.strip().lower(), column_b)

            if isinstance(column_e, str) and str(value_g) in column_e:
                column_d = str(column_d).lower() == "true"

            if column_d != current_row[db_value]:
                update_fields.append(f"{db_value} = '{int(column_d)}'")  # Convert boolean to int (True -> 1, False -> 0) and surround with single quotes

        if update_fields:
            update_sql = f"UPDATE core.AccountType SET {', '.join(update_fields)} WHERE CoreName = '{value_g}';"
            update_statements.append(update_sql)

    return update_statements

def save_sql(update_statements, output_file_path):
    with open(output_file_path, 'w') as f:
        f.writelines([f"{line}\n" for line in update_statements])