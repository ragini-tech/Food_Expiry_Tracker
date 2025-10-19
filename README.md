# Food Expiry Tracker

A comprehensive desktop application to help you track food items in your inventory, monitor expiry dates, and reduce food waste.

## Features

- **Add and manage food items** with names, categories, expiry dates, and optional notes
- **Color-coded display** (green for fresh, yellow for expiring soon, red for expired)
- **Filter and search** to quickly find items by name or category
- **Sort items** by name, category, or expiry date
- **Edit existing items** (double-click on any item)
- **Export data to CSV** for backup or analysis in spreadsheets
- **Expiry reminders** - get notified when food items are about to expire
- **Dark mode** - toggle between light and dark themes
- **Statistics** - view a breakdown of your inventory by category and expiry status

## Requirements

- Python 3.6+
- Required packages:
  - tkinter (included with Python)
  - plyer (for notifications)

## Installation

1. Clone this repository or download the files
2. Install required packages:
   ```
   pip install plyer
   ```
3. Run the application:
   ```
   python food_tracker_improved.py
   ```

## Usage

### Adding Items
Fill in the food name, category, expiry date, and optional notes at the top of the window, then click "Add Item".

### Managing Items
- **Select an item** in the table to edit or delete it
- **Double-click** on any item to edit its details
- **Filter** by category using the dropdown menu
- **Search** for items by typing in the search box
- **Sort** items by clicking on the "Sort by" dropdown

### Additional Functions
- **Check Expiry Reminders** - Shows notifications for items expiring soon
- **Export to CSV** - Saves your inventory to a spreadsheet file
- **View Statistics** - Displays a summary of your inventory
- **Toggle Dark Mode** - Switches between light and dark themes

## Files
- `food_tracker_improved.py` - The main application file
- `food_database.db` - SQLite database where inventory is stored

## License
This project is free to use and modify.

## Author
Ragini_Yadav

## Acknowledgements

This project was created to help reduce food waste and improve inventory management. 
