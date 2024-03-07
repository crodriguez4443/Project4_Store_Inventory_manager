from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import func
from datetime import datetime
import csv

#declare base a class to be defined definitions and allows SQL alchemy to map them to database tables
Base = declarative_base()

class InventoryItem(Base):
    __tablename__ = 'inventory'

    product_id= Column(Integer, primary_key=True)
    product_name = Column(String, nullable=False)
    product_quantity = Column(Integer, nullable=False)
    product_price = Column(Float, nullable=False)
    date_updated = Column(Date, default=datetime.utcnow)

#define the SQLight database
engine = create_engine('sqlite:///inventory.db', echo=False)
#creating the table
Base.metadata.create_all(engine)

# Create a sessionmaker instance bound to the engine
Session = sessionmaker(bind=engine)
session = Session()

def add_csv():
    with open('inventory.csv', mode='r') as csvfile: #r mode to read contents
        data = csv.reader(csvfile)
        next(data, None) # skips header line
        for row in data:
            product_name = row[0].replace('"', "")
            product_price = float(row[1].replace("$",""))
            product_quantity = int(row[2])
            date_updated = datetime.strptime(row[3], '%m/%d/%Y')

            #create new item instance
            new_entry = InventoryItem(
                product_name = product_name,
                product_quantity = product_quantity,
                product_price = product_price,
                date_updated=date_updated
            )
            session.add(new_entry)
        session.commit()

def main_page():
    print("STORE INVENTORY QUERY")
    while True:
        selection = input("\n Select one of the following options.\n  v) View product details \n  a) Add a new product \n  b) Create a backup (in CSV format)\n  x) Exit\n").lower()
        if selection == "v":
            product_selection()
        elif selection == "a":
            add_product()
        elif selection == "b":
            create_backup()
        elif selection == 'x':
            print('thanks for checking in!')
            exit()
        else:
            print("ERROR, pleas print one of the available options")

def product_selection():
    try:
        max_product_id = session.query(func.max(InventoryItem.product_id)).scalar()
        select_product_id = int(input(f"select a product from 1 to {max_product_id}: "))
        product = session.query(InventoryItem).filter_by(product_id=select_product_id).first()
        if product:
            print(f'Product ID: {product.product_id}')
            print(f'Product Name: {product.product_name}')
            print(f'Product Price: ${product.product_price}')
            print(f'Product Quantity: {product.product_quantity}')
            print(f'Date Updated: {product.date_updated}')
        else:
            print('invalid selection. select a valid product ID')
    except ValueError:
        print(f'select a product from 1 to {max_product_id}')


def add_product():
    print("***Please add the following required fields for your new product.***\n")
    product_name = input('Give the product a name? ')
    product_price = float(input("What's the price?"))
    product_quantity = int(input("What's the quantity?"))
    
    #check for duplicate product names. if duplicates, do not add or commit new product
    existing_product = session.query(InventoryItem).filter_by(product_name=product_name).first()
    if existing_product == True:
        print('This product already exists!')
        return

    #InventoryItem is a special class constructor. 
    new_product = InventoryItem(
        product_name=product_name,
        product_quantity=product_quantity,
        product_price=product_price,
    )

    session.add(new_product)
    session.commit()
    print(f'\nAdded {product_name} to the inventory!')

def create_backup():
    #select all items from the inventory database.db
    backupdb_data = session.query(InventoryItem).all()
    #create a new csv file with unique timestamp
    timestamp = datetime.now().strftime('%Y%m%d')
    backup_file_name = f'backup_file_{timestamp}.csv'
    # Define the columns of backup_file
    fieldnames = ['product_id','product_name','product_price','product_quantity','date_updated']


    try:
        #opens backup_file with intention to WRITE it out
        with open(backup_file_name, 'w',newline = '') as new_file:
            #create the WRITER object
            csvwriter = csv.DictWriter(new_file, fieldnames = fieldnames)
            
            #WRITING the header row 
            csvwriter.writeheader()

            #iterate over backupdb_data and WRITING that value to the csv file
            for item in backupdb_data:
                csvwriter.writerow({
                    'product_id': item.product_id, 
                    'product_name': item.product_name,
                    'product_price': item.product_price, 
                    'product_quantity': item.product_quantity, 
                    'last_updated': item.date_updated.strftime('%Y-%m-%d')
                    })
        print('backup successfully created!')
    except Exception as e:
        print(f' Error creating backup:{e}')
