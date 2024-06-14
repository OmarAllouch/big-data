# The schema we're going to create is in the `images/etoile.png` file.
# You may consult it to understand the relationships between the tables.
# The input data (from the sources) is in the `data` folder.
# The output data (the tables) are saved in the `output` folder.

import pandas as pd

# Load the data
orders = pd.read_csv('data/orders.csv')
returns = pd.read_csv('data/returns.csv')
cities = pd.read_csv('data/uscities.csv')

# Remove orders that don't have a corresponding city in the cities dataset
for city in orders['City']:
    if city not in cities['city'].values:
        orders = orders[orders['City'] != city]

# Create : order_fact, ship_dim, product_dim, customer_dim, return_dim, city_dim, date_dim
order_fact = orders[['Order ID', 'Sales', 'Quantity', 'Discount', 'Profit',
                     'Order Date', 'Customer ID', 'City', 'Product ID']]
order_fact.rename(columns={'Order Date': 'timestamp', 'City': 'city'}, inplace=True)
order_fact['timestamp'] = pd.to_datetime(order_fact['timestamp'])

ship_dim = orders[['Order ID', 'Ship Mode']]
ship_dim = ship_dim.drop_duplicates()

product_dim = orders[['Product ID', 'Category', 'Sub-Category', 'Product Name']]
product_dim = product_dim.drop_duplicates()

customer_dim = orders[['Customer ID', 'Customer Name', 'Segment']]
customer_dim = customer_dim.drop_duplicates()

return_dim = returns

city_dim = cities[['city', 'lat', 'lng']]

date_dim = pd.to_datetime(orders['Order Date'])
date_dim = pd.DataFrame(date_dim)
date_dim['timestamp'] = date_dim['Order Date']
date_dim['year'] = date_dim['Order Date'].dt.year
date_dim['month'] = date_dim['Order Date'].dt.month
date_dim['day'] = date_dim['Order Date'].dt.day
date_dim = date_dim.drop_duplicates()

# Save the data
order_fact.to_csv('output/order_fact.csv', index=False)
ship_dim.to_csv('output/ship_dim.csv', index=False)
product_dim.to_csv('output/product_dim.csv', index=False)
customer_dim.to_csv('output/customer_dim.csv', index=False)
return_dim.to_csv('output/return_dim.csv', index=False)
city_dim.to_csv('output/city_dim.csv', index=False)
date_dim.to_csv('output/date_dim.csv', index=False)

# Combine the data
combined_data = []
for _, order in orders.iterrows():
    city = city_dim[city_dim['city'] == order['City']].iloc[0]
    date = date_dim[date_dim['timestamp'] == order['Order Date']].iloc[0]

    combined_data.append({
        # Order
        'order_id': order['Order ID'],
        'sales': order['Sales'],
        'quantity': order['Quantity'],
        'discount': order['Discount'],
        'profit': order['Profit'],
        # Date
        'year': date['year'],
        'month': date['month'],
        'day': date['day'],
        # City
        'city': order['City'],
        'longitude': city['lng'],
        'latitude': city['lat'],
        # Ship
        'ship_mode': order['Ship Mode'],
        'ship_date': order['Ship Date'],
        # Product
        'product_id': order['Product ID'],
        'product_name': order['Product Name'],
        'category': order['Category'],
        'sub_category': order['Sub-Category'],
        # Customer
        'customer_id': order['Customer ID'],
        'customer_name': order['Customer Name'],
        'segment': order['Segment'],
        # Return
        'returned': order['Order ID'] in returns['Order ID'].values
    })

combined_data = pd.DataFrame(combined_data)

# Save the combined data
combined_data.to_csv('output/combined_data.csv', index=False)
