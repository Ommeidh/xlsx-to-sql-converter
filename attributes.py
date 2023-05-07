import pandas as pd
import configparser


def read_config():
    config = configparser.ConfigParser()
    with open("config.ini", "r", encoding="utf-8-sig") as f:
        config.read_file(f)
    column_b_mappings = dict(config.items("COLUMN_B_MAPPINGS"))
    print("Column B Mappings:", column_b_mappings)
    return column_b_mappings


def generate_sql_script(file_path, column_b_mappings):
    df = pd.read_excel(file_path, header=None)

    update_statements = []

    for idx_g, value_g in df[6].dropna().items():
        if idx_g < 3:  # Skip the first three rows
            continue

        update_fields = []

        for idx, value in df[[1, 3]].dropna().iterrows():
            if idx < 3:  # Skip the first three rows
                continue

            column_b = value[1].strip()
            column_d = value[3]

            if not isinstance(column_d, bool):  # Skip the row if column D is not True or False
                continue

            column_e = df.at[idx, 4]

            if value_g in str(column_e):
                column_d = not column_d

            db_value = column_b_mappings.get(column_b.strip().lower(), column_b)

            if db_value not in [item.split(" ")[0] for item in update_fields]:
                print("column_b:", column_b, "column_d:", column_d, "db_value:", db_value)
                update_fields.append(f"{db_value} = '{int(column_d)}'")  # Convert boolean to int (True -> 1, False -> 0) and surround with single quotes

        update_sql = f"UPDATE core.AccountType SET {', '.join(update_fields)} WHERE CoreName = '{value_g}';"
        update_statements.append(update_sql)

    return update_statements


def save_sql(update_statements, output_file_path):
    with open(output_file_path, 'w') as f:
        f.writelines([f"{line}\n" for line in update_statements])


if __name__ == '__main__':
    column_b_mappings = read_config()
    update_statements = generate_sql_script('example.xlsx', column_b_mappings)
    save_sql(update_statements, 'output.sql')