import sys
import sqlite3 as sql
from datetime import datetime
import time
import logging
from rich import print 

# ? CREATE, INITIATE, AND CONNECT DB ADD TABLE IF IT DOESN'T YET EXIST
def connect_db():
    conn = sql.connect("./Expense_Tracker/transaction.db")
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Categories(
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
            UNIQUE(name, type)
        );
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Transactions(
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
            category_id INTEGER NOT NULL,
            date DATE NOT NULL,
            description TEXT NOT NULL,
            FOREIGN KEY (category_id) REFERENCES Categories(category_id)
        );
        """
    )
    conn.commit()

    return conn

# ? INSERT CATEGORY
def insert_category(category:str, category_type:str, conn):
    cur = conn.cursor()

    category = category.lower()
    category_type = category_type.lower()
    category_types = ['income', 'expense']

    if category_type not in category_types:
        return "You can only choose between 'income' or 'expense"
    
    categories = cur.execute("""SELECT name, type FROM Categories;""")
    categories_fetch = categories.fetchall()

    if (category, category_type) not in categories_fetch:
        cur.execute("""INSERT INTO Categories(name, type) VALUES (?, ?)""", (category, category_type, ))
        conn.commit()

    elif (category, category_type) in categories_fetch:
        return print("category already exist")

# ? QUERY A FULL TABLE
def query_all(transc_type:str, table:str, conn):
    cur = conn.cursor()

    transaction_types = ["income", "expense"]
    tables = ["Categories", "Transactions"]

    if transc_type not in transaction_types:
        return "Transaction type given as input is not support, try again with correct input."
    
    if table not in tables:
        return "Table does not exist in database. Try again with correct table"

    query = cur.execute(
        f"""
        SELECT name
        FROM {table}
        WHERE type = ?;
        """, (transc_type, ))
    
    query_result = query.fetchall()
    len_query_result = len(query_result)

    if len_query_result == 0:
        return None
    
    query_result = list(query_result)
    return query_result

# ? GET CATEGORY ID
def get_category_id(category_name:str, category_type:str, conn):
    cur = conn.cursor()

    category_name = category_name.lower()
    category_type = category_type.lower()

    query = cur.execute("""
                    SELECT category_id
                    FROM Categories 
                    WHERE name = ? AND type = ?;
                    """, (category_name, category_type))

    category_id = query.fetchone()
    
    if category_id is None:
        return None
    
    return category_id

# ? DELETE_CATEGORY
def remove_category(category:str, category_type:str, conn):
    cur = conn.cursor()

    category = category.lower()
    category_type = category_type.lower()

    categories = cur.execute("""SELECT name, type FROM Categories;""")
    categories_fetch = categories.fetchall()

    if categories_fetch is None:
        return None

    if (category, category_type) in categories_fetch:
        cur.execute("""DELETE FROM Categories WHERE name = ? AND type = ?""", (category, category_type))
        conn.commit()
        return "Successful removed"

    elif (category, category_type) not in categories_fetch:
        return "Caterogy does not exist, create the category first."

# ? INSERT TRANSACTION
def insert_transaction(title:str, amount:int, transc_type:str, category_id:int, date_time:str, desc:str, conn):
    cur = conn.cursor()

    transc_type = transc_type.lower()
    title = title.lower()
    transaction_types = ['income', 'expense']

    if len(title) == 0:
        return "Please enter a title for this transaction."
    if transc_type not in transaction_types:
        return "You can only choose between 'income' or 'expense"
    if amount < 1:
        return "Amount cannot be negative and must be greater than 1."
    if len(desc) == 0:
        return "Please enter desciption for Expense/Income Amount."

    category_query = cur.execute("""
            SELECT category_id
            FROM Categories 
            WHERE category_id = ?;""", (category_id,))
    
    category_result = category_query.fetchall()
    
    if category_result is None:
        return "Category does not yet exist, create category and try again."

    transaction_query = cur.execute("""SELECT title, amount, type, category_id, description FROM Transactions;""")
    transactions_fetch = transaction_query.fetchall()

    if (title, amount, transc_type, category_id, desc) in transactions_fetch:
        return f"This {transc_type} already exist."
    
    cur.execute("""INSERT INTO Transactions(title, amount, type, category_id, date, description) VALUES (?, ?, ?, ?, ?, ?);""", (title, amount, transc_type, category_id, date_time, desc, ))
    conn.commit()

# ? GET TRANSACTION ID
def get_transaction_id(title:str, transc_type:str, conn):
    cur = conn.cursor()

    title = title.lower()
    transc_type = transc_type.lower()
    transc_types = ['income', 'expense']

    if transc_type not in transc_types:
        return "Category was not found, only income and expense are allowed."

    transc_query = cur.execute("""
                            SELECT transaction_id
                            FROM Transactions 
                            WHERE title = ? AND type = ?;
                            """, (title, transc_type))

    transc_id = transc_query.fetchone()

    if transc_id is None:
        return None
    
    conn.commit()
    return transc_id

# ?REMOVE TRANSACTION
def remove_transaction(transc_id:int, transc_type:str, conn):
    cur = conn.cursor()

    transc_type = transc_type.lower()
    transaction_types = ["income", "expense"]

    if transc_type not in transaction_types:
        return print("you can only choose between, 'income' and 'expense', try again.")
    
    transactions = cur.execute("""SELECT transaction_id, type FROM Transactions;""")
    transactions_fetch = transactions.fetchall()
    len_transc_fetch = len(transactions_fetch)

    if len_transc_fetch == 0:
        return "There are no 'Transaction', try adding a transaction."

    if (transc_id, transc_type) in transactions_fetch:
        cur.execute( """DELETE FROM Transactions WHERE transaction_id = ? AND type = ?; """, (transc_id, transc_type))

    elif (transc_id, transc_type) not in transactions_fetch:
        return print("Transaction doesn't exist, add a transaction and try again later.")
    conn.commit()

def income_transc_query_all(transc:str, conn):
    cur = conn.cursor()

    transc  = transc.lower()
    transc_list = ["income", "expense"]

    if transc not in transc_list:
        return print("Only income and expense are allowed, please try again...")

    elif transc in transc_list:
        query = cur.execute("""
                SELECT
                    title, description
                FROM Transactions
                WHERE type = ?;""", (transc, ))
    
        result = query.fetchall()

    conn.commit()
    return result

# ? GET USER INPUT AN
def user_input(msg:str, input_type:int|str = None):
    from rich import print

    while True:
        try:
            print(f"{msg}")
            userinput = input("> ")

            if len(userinput) == 0:
                print("Input cannot be empty, please try again...")
            
            elif input_type == int:
                userinput = int(userinput)
                return userinput
            
            elif input_type == str:
                userinput = str(userinput)
                return userinput
        
        except ValueError:
            print("Invalid input, try again...")

def render_menu(menu:list):
        print("")
        for i, option in enumerate(menu, start=1):
            option = list(option)
            first_index = 0
            first_letter = option[first_index].capitalize()
            option.pop(0)
            option.insert(0, first_letter)
            option = "".join(option)
            print(f"{i}. {option}")

def render_query_view(result):
    for i, query_result in enumerate(result, start=1):
        query_result = list(query_result)
        first_index = 0
        last_index = len(query_result) - 1
        print(f"{i}. 'Title': {query_result[first_index]}, 'Description': {query_result[last_index]}")

def set_to_list(set_to_convert):
    set_to_convert = list(set_to_convert)
    return set_to_convert

def transaction_menu(menu, transaction, table, date, conn):
    while True:
        render_menu(menu)
        len_menu = len(menu)
        userinput = user_input(f"CHoose 1 and {len_menu}: ", int)
        
        if userinput == 1:
            transc = income_transc_query_all(transaction, conn)
            len_transc = len(transc)
            
            if len_transc == 0:
                print("The is no income, please add income and try again.")
            elif len_transc > 0:
                render_query_view(transc)
                time.sleep(2.5)
        
        elif userinput == 2:
            while True:
                transc_type = transaction

                title_input = user_input(f"Enter the 'Title' for {transc_type}:", str)
                amount_input = user_input(f"Enter the 'Amount' of the {transc_type}", int)
                desc_input = user_input(f"Enter {transc_type} 'Description'.", str)

                query = query_all(transc_type, table, conn)
                len_query = len(query)

                render_menu(query)
                category_id_input = user_input("Choose Category from above:", int)

                if category_id_input < 1 or category_id_input > len_query:
                    print(f"Invalid input, choose between 1 and {len_query}")
                    continue
                
                first_index = 0
                category_index = category_id_input - 1
                category_name = list(query[category_index])
                category_name = category_name[first_index]
                category_id = get_category_id(category_name, transc_type, conn)
                category_id = set_to_list(category_id)
                category_id = category_id[first_index]
                # print(f"Category Name: {category_name}, ID: {category_id}")

                insert_transaction(title_input, amount_input, transc_type, category_id, date, desc_input, conn)
                print(f"'{transc_type}' of amount {amount_input} successfully added")
                break

        elif userinput == 3:
            while True:
                transc = income_transc_query_all(transaction, conn)
                len_transc = len(transc)
                len_transc_extra = len_transc + 1

                if len_transc == 0:
                    print("The is no income, please add income and try again.")
                elif len_transc > 0:
                    render_query_view(transc)
                print(f"{len_transc_extra}. Go back")

                userinput = user_input(f"Choose between 1 and {len_transc_extra} to remove income.", int)
                
                if userinput > 0 and userinput <= len_transc_extra:
                    if userinput == len_transc_extra:
                        break

                    userinput -= 1
                    transc = set_to_list(transc[userinput])
                    title_index = 0
                    transc_title = transc[title_index]
                    transc_id = get_transaction_id(transc_title, transaction, conn)
                    transc_id = set_to_list(transc_id)
                    transc_id = transc_id[0]

                    if userinput == 0:
                        removed_transaction = transc_title
                        remove_transaction(transc_id, transaction, conn)
                        print(f"{removed_transaction} successfully removed index.")
                        break
                    elif userinput > 0:
                        removed_transaction = transc_title
                        remove_transaction(transc_id, transaction, conn)  
                        print(f"{transc_title} successfully removed index.")
                        break
                    else:
                        print(f"{transc_title} deletion failed...")
                        break
                else:
                    print(f"Choose from the advailable options above, from 1 to {len_transc_extra}")

        elif userinput == 4:
            break

        elif userinput == len_menu:
            conn.commit()
            conn.close()
            sys.exit()

def main():
    conn = connect_db()
    now = datetime.now()
    date_time = now.strftime("%Y/%m/%d %H:%M:%S")
    
    first_index = 0
    income = "income"
    expense = "expense"
    transaction_table = "Transactions"
    category_table = "Categories"

    transaction_types = ["Income", "Expense"]
    main_menu = ["income/expense", "category", "exit"]
    transc_submenu = ["income", "expense", "go back"]
    income_menu = ["view income(s)", "add income", "remove income", "go back", "exit"]
    expense_menu = ["view expense(s)", "add expense","remove expense", "go back", "exit"]
    category_submenu = ["view categories", "add category", "remove category", "go back", "exit"]

    len_main_menu = len(main_menu)
    len_transc_submenu = len(transc_submenu)
    len_category_submenu = len(category_submenu)
    len_transc_type = len(transaction_types)

    while True:
        render_menu(main_menu)
        userinput = user_input("Choose from the option above:", int)

        if userinput == 1:
            while True:
                render_menu(transc_submenu)
                userinput = user_input("Choose from the options above", int)
                if userinput == 1:
                    transaction_menu(income_menu, income, category_table, date_time, conn)
                
                elif userinput == 2:
                    transaction_menu(expense_menu, expense, category_table, date_time, conn)

                elif userinput == len_transc_submenu:
                    break

        elif userinput == 2:
            while True:
                render_menu(category_submenu)
                userinput = user_input("Choose from the above:", int)
                # TODO add view category option

                if userinput == 1:
                    income_categories = query_all(income, category_table, conn)
                    expense_categories = query_all(expense, category_table, conn)

                    print("Income Categories:", end="")
                    render_menu(income_categories)
                    print("")

                    print("Expense Categories", end="")
                    render_menu(expense_categories)
                    print(" ")
                    time.sleep(2.5)

                elif userinput == 2:
                    while True:
                        render_menu(transaction_types)
                        category_type_input = user_input("Choose type 'category' from above:", int)

                        if category_type_input < 1 or category_type_input > len_transc_type:
                            print(f"Invalid input, input must be in range 1 to {len_transc_type}. try again with correct input.")

                        category_type = transaction_types[category_type_input - 1]
                        category_name_input = user_input(f"Enter the name of the {category_type} type category:", str)

                        try:
                            insert_category(category_name_input, category_type, conn)
                            print(f"Successfully added category with name {category_name_input} of type {category_type}")
                            break
                        except ValueError:
                            print("Failed to add category, make sure input is correct and try again")
                            continue

                elif userinput == 3:
                    while True:
                        render_menu(transaction_types)
                        category_type_input = user_input("Choose type 'category' from above:", int)

                        if category_type_input < 1 or category_type_input > len_transc_type:
                            print(f"Invalid input, input must be in range 1 to {len_transc_type}. try again with correct input.")

                        category_type = transaction_types[category_type_input - 1]
                        category_type = category_type.lower()

                        categories = query_all(category_type, category_table, conn)
                        len_category = len(categories)

                        render_menu(categories)
                        category = user_input(f"Choose between 1 to {len_category} to delete corresponding category:", int)

                        if category < 1 or category > len_category:
                            print(f"Invalid input, input must be in range 1 to {len_category}. try again with correct input.")
                        
                        category_id = category - 1
                        category_name = categories[category_id]
                        category_name = category_name[first_index]

                        try:
                            remove_category(category_name, category_type, conn)
                            print(f"Category was \"successfully\" removed, name: {category_name_input} type: {category_type}")
                            break
                        except ValueError:
                            print("Failed to remove category,try again....")
                            continue
                        break

                elif userinput == 4:
                    break

                elif userinput == len_category_submenu:
                    conn.commit()
                    conn.close()
                    sys.exit()

        elif userinput == len_main_menu:
            conn.commit()
            conn.close()
            sys.exit()
            break    
    
if __name__ == "__main__":
    main()


