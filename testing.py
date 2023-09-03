import datetime

# Get the current date
current_date = datetime.datetime.now()

# Format and print the full name of the current month
month_name = current_date.strftime('%B')
print(month_name)