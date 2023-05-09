import pandas as pd
import os
import configparser
import pyodbc

def read_config(config_file=None):
    if config_file is None:
        config_file = os.path.join(os.getcwd(), 'config.ini')

    config = configparser.ConfigParser()
    with open(config_file, "r", encoding="utf-8-sig") as f:
        config.read_file(f)
    column_b_mappings = dict(config.items("COLUMN_B_MAPPINGS"))
    print("Column B Mappings:", column_b_mappings)
    return column_b_mappings

def connect_to_db(server, database, user, password):
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={user};"
        f"PWD={password}"
    )
    conn = pyodbc.connect(conn_str)
    return conn

def get_existing_data(conn):
    query = "SELECT CoreName, * FROM core.AccountType"
    df = pd.read_sql(query, conn)
    return df.set_index("CoreName").T.to_dict("dict")

def generate_sql_script(file_path, column_b_mappings, conn):
    df = pd.read_excel(file_path, header=None, engine='openpyxl')
    existing_data = get_existing_data(conn)
    update_statements = []

    for idx_g, value_g in df[6].dropna().items():
        if idx_g < 3:
            continue

        update_fields = []

        for idx, row in df.iterrows():
            if idx < 3:
                continue

            column_b = row[1]
            column_d = row[3]
            column_e = row[4]

            if not isinstance(column_b, str):
                continue

            if str(column_d).lower() == "true":
                update_fields.append(f"{db_value} = '1'")
            elif str(column_d).lower() == "false":
                update_fields.append(f"{db_value} = '0'")

            if isinstance(column_e, str) and str(value_g) in column_e:
                column_d = str
                column_d = str(column_d).lower() == "true"

            db_value = column_b_mappings.get(column_b.strip().lower(), column_b)

            if db_value not in [item.split(" ")[0] for item in update_fields]:
                update_fields.append(f"{db_value} = '{int(column_d)}'")  # Convert boolean to int (True -> 1, False -> 0) and surround with single quotes

        existing_record = existing_data.get(value_g)
        if existing_record:
            update_fields = [f for f in update_fields if existing_record[f.split(" ")[0]] != int(f.split(" ")[2].strip("'"))]

        if update_fields:
            update_sql = f"UPDATE core.AccountType SET {', '.join(update_fields)} WHERE CoreName = '{value_g}';"
            update_statements.append(update_sql)

    return update_statements

def save_sql(update_statements, output_file_path):
    with open(output_file_path, 'w') as f:
        f.writelines([f"{line}\n" for line in update_statements])