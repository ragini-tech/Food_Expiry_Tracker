import tkinter as tk
from tkinter import messagebox, ttk, filedialog, simpledialog
from datetime import datetime, timedelta
from plyer import notification
import random
import sqlite3
import csv
import os

# Database setup
conn = sqlite3.connect('food_database.db')
c = conn.cursor()

# Check existing schema and add missing columns if needed
c.execute("PRAGMA table_info(food_items)")
columns = [column[1] for column in c.fetchall()]

# Create tables if they don't exist
c.execute('''CREATE TABLE IF NOT EXISTS food_items
             (id INTEGER PRIMARY KEY, name TEXT, expiry_date DATE)''')

# Add category column if it doesn't exist
if 'category' not in columns:
    try:
        c.execute("ALTER TABLE food_items ADD COLUMN category TEXT DEFAULT 'Other'")
        print("Added 'category' column to existing database")
    except sqlite3.Error as e:
        print(f"Error adding category column: {e}")

# Add notes column if it doesn't exist
if 'notes' not in columns:
    try:
        c.execute("ALTER TABLE food_items ADD COLUMN notes TEXT")
        print("Added 'notes' column to existing database")
    except sqlite3.Error as e:
        print(f"Error adding notes column: {e}")

# Create usage_log table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS usage_log
             (id INTEGER PRIMARY KEY, item_name TEXT, action TEXT, timestamp TEXT)''')

conn.commit()

# Define log_usage
def log_usage(item_name, action):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO usage_log (item_name, action, timestamp) VALUES (?, ?, ?)",
              (item_name, action, timestamp))
    conn.commit()

# GUI setup
root = tk.Tk()
root.geometry("800x750")
root.title("Food Expiry Tracker")

is_dark_mode = False

# Setup app styles
def setup_styles():
    global is_dark_mode
    bg = "#2E2E2E" if is_dark_mode else "#f4f4f9"
    fg = "white" if is_dark_mode else "#333333"
    button_bg = "#555" if is_dark_mode else "#4CAF50"
    
    style = ttk.Style()
    theme = "clam"  # A theme that works well with custom colors
    style.theme_use(theme)
    
    # Configure Treeview colors
    style.configure("Treeview", 
                    background=bg,
                    foreground=fg,
                    fieldbackground=bg)
    
    style.configure("Treeview.Heading",
                   background=button_bg,
                   foreground="white")
    
    # Configure ttk combobox colors
    style.map('TCombobox', 
              fieldbackground=[('readonly', bg)],
              background=[('readonly', button_bg)],
              foreground=[('readonly', fg)])
    
    return bg, fg, button_bg

# Toggle Dark Mode
def toggle_dark_mode():
    global is_dark_mode
    is_dark_mode = not is_dark_mode
    bg, fg, button_bg = setup_styles()
    
    root.configure(bg=bg)
    
    # Update all frame backgrounds
    main_frame.configure(bg=bg)
    button_frame.configure(bg=bg)
    tree_frame.configure(bg=bg)
    
    # Update all labels
    for widget in main_frame.winfo_children():
        if isinstance(widget, tk.Label):
            widget.configure(bg=bg, fg=fg)
    
    # Update all buttons
    for widget in button_frame.winfo_children():
        if isinstance(widget, tk.Button):
            widget.configure(bg=button_bg, fg="white")
    
    # Refresh tree to update colors
    refresh_items()

# Add item
def add_item():
    name = name_entry.get()
    category = category_combobox.get()
    expiry_date = expiry_entry.get()
    notes = notes_entry.get()

    if name == '' or expiry_date == '' or category == '':
        messagebox.showerror("Error", "Please enter food name, category, and expiry date")
        return

    try:
        expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d").date()
    except ValueError:
        messagebox.showerror("Error", "Invalid date format")
        return

    try:
        c.execute("INSERT INTO food_items (name, category, expiry_date, notes) VALUES (?, ?, ?, ?)",
                  (name, category, expiry_date, notes))
        log_usage(name, "add")
        conn.commit()
        name_entry.delete(0, tk.END)
        expiry_entry.delete(0, tk.END)
        notes_entry.delete(0, tk.END)
        messagebox.showinfo("Success", "Food item added successfully")
        refresh_items()
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Failed to add item: {e}")

# Edit selected item
def edit_item():
    if not tree.selection():
        messagebox.showerror("Error", "Please select an item to edit")
        return
        
    selected_item = tree.selection()[0]
    item_id = tree.item(selected_item, 'values')[0]
    
    # Get current values
    c.execute("SELECT name, category, expiry_date, notes FROM food_items WHERE id=?", (item_id,))
    item = c.fetchone()
    
    if not item:
        messagebox.showerror("Error", "Item not found")
        return
        
    # Create a dialog for editing
    edit_window = tk.Toplevel(root)
    edit_window.title("Edit Food Item")
    edit_window.geometry("400x300")
    edit_window.resizable(False, False)
    
    # Set background based on mode
    edit_window.configure(bg="#2E2E2E" if is_dark_mode else "#f4f4f9")
    fg_color = "white" if is_dark_mode else "#333333"
    
    # Create form fields
    tk.Label(edit_window, text="Food Name:", bg=edit_window['bg'], fg=fg_color).grid(row=0, column=0, padx=10, pady=10, sticky="w")
    edit_name_entry = tk.Entry(edit_window)
    edit_name_entry.grid(row=0, column=1, padx=10, pady=10, sticky="we")
    edit_name_entry.insert(0, item[0])
    
    tk.Label(edit_window, text="Category:", bg=edit_window['bg'], fg=fg_color).grid(row=1, column=0, padx=10, pady=10, sticky="w")
    edit_category_combo = ttk.Combobox(edit_window, values=["Dairy", "Vegetables", "Meat", "Grains", "Fruits", "Other"])
    edit_category_combo.grid(row=1, column=1, padx=10, pady=10, sticky="we")
    edit_category_combo.set(item[1])
    
    tk.Label(edit_window, text="Expiry Date (YYYY-MM-DD):", bg=edit_window['bg'], fg=fg_color).grid(row=2, column=0, padx=10, pady=10, sticky="w")
    edit_expiry_entry = tk.Entry(edit_window)
    edit_expiry_entry.grid(row=2, column=1, padx=10, pady=10, sticky="we")
    edit_expiry_entry.insert(0, item[2])
    
    tk.Label(edit_window, text="Notes:", bg=edit_window['bg'], fg=fg_color).grid(row=3, column=0, padx=10, pady=10, sticky="w")
    edit_notes_entry = tk.Entry(edit_window)
    edit_notes_entry.grid(row=3, column=1, padx=10, pady=10, sticky="we")
    edit_notes_entry.insert(0, item[3] if item[3] else "")
    
    # Save function for the edit window
    def save_changes():
        new_name = edit_name_entry.get()
        new_category = edit_category_combo.get()
        new_expiry = edit_expiry_entry.get()
        new_notes = edit_notes_entry.get()
        
        if new_name == '' or new_expiry == '' or new_category == '':
            messagebox.showerror("Error", "Please fill in all required fields", parent=edit_window)
            return
            
        try:
            new_expiry_date = datetime.strptime(new_expiry, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Error", "Invalid date format", parent=edit_window)
            return
            
        try:
            c.execute("UPDATE food_items SET name=?, category=?, expiry_date=?, notes=? WHERE id=?",
                     (new_name, new_category, new_expiry_date, new_notes, item_id))
            log_usage(new_name, "edit")
            conn.commit()
            messagebox.showinfo("Success", "Food item updated successfully", parent=edit_window)
            edit_window.destroy()
            refresh_items()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to update item: {e}", parent=edit_window)
    
    # Buttons
    save_button = tk.Button(edit_window, text="Save Changes", 
                           bg="#4CAF50", fg="white",
                           command=save_changes)
    save_button.grid(row=4, column=0, columnspan=2, padx=10, pady=20, sticky="we")
    
    cancel_button = tk.Button(edit_window, text="Cancel", 
                             bg="#F44336", fg="white",
                             command=edit_window.destroy)
    cancel_button.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky="we")
    
    # Configure grid
    edit_window.columnconfigure(0, weight=1)
    edit_window.columnconfigure(1, weight=2)
    
    # Make dialog modal
    edit_window.transient(root)
    edit_window.grab_set()
    root.wait_window(edit_window)

# Delete selected item
def delete_selected():
    if not tree.selection():
        messagebox.showerror("Error", "Please select an item to delete")
        return
        
    selected_item = tree.selection()[0]
    item_id = tree.item(selected_item, 'values')[0]
    item_name = tree.item(selected_item, 'values')[1]
    
    confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete '{item_name}'?")
    if not confirm:
        return
        
    try:
        c.execute("DELETE FROM food_items WHERE id=?", (item_id,))
        log_usage(item_name, "delete")
        conn.commit()
        refresh_items()
        messagebox.showinfo("Success", f"Item '{item_name}' deleted successfully")
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Failed to delete item: {e}")

# Display items with color coding and sorting
def refresh_items(sort_by=None):
    for row in tree.get_children():
        tree.delete(row)

    search_query = search_entry.get().lower()
    selected_category = filter_combobox.get()

    today = datetime.now().date()
    
    # Default sort by expiry date if not specified
    if sort_by is None or sort_by == "":
        sort_by = "expiry_date"
    
    # Check if database has category column
    c.execute("PRAGMA table_info(food_items)")
    columns = [column[1] for column in c.fetchall()]
    has_category = 'category' in columns
    has_notes = 'notes' in columns
    
    # Construct the query with ORDER BY
    query = "SELECT id, name"
    if has_category:
        query += ", category"
    else:
        query += ", 'Other' as category"
    
    query += ", expiry_date"
    
    if has_notes:
        query += ", notes"
    else:
        query += ", '' as notes"
        
    query += " FROM food_items"
    
    params = []
    
    # Add WHERE clauses if needed
    where_clauses = []
    
    if selected_category != "All" and has_category:
        where_clauses.append("category = ?")
        params.append(selected_category)
    
    if search_query:
        where_clauses.append("name LIKE ?")
        params.append(f"%{search_query}%")
    
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    
    # Add sorting - handle case where column doesn't exist
    if sort_by == "category" and not has_category:
        sort_by = "expiry_date"  # Fall back to expiry_date if category doesn't exist
        
    query += f" ORDER BY {sort_by}"
    
    try:
        c.execute(query, params)
        items = c.fetchall()

        for item in items:
            item_id = item[0]
            name = item[1]
            category = item[2] if has_category else "Other"
            expiry_date = item[3] if has_category else item[2]
            notes = item[4] if has_notes and has_category else ""
            
            try:
                expiry = datetime.strptime(expiry_date, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                # Handle case where expiry date is invalid
                expiry = today - timedelta(days=1)  # Mark as expired
                
            if expiry < today:
                tag = 'expired'
            elif expiry - today <= timedelta(days=3):
                tag = 'soon'
            else:
                tag = 'fresh'

            tree.insert('', tk.END, values=(item_id, name, category, expiry_date, notes), tags=(tag,))
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Error loading data: {e}\n\nPlease restart the application.")

def export_to_csv():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv", 
        filetypes=[("CSV files", "*.csv")],
        initialfile="food_inventory.csv"
    )
    if not file_path:
        return

    c.execute("SELECT id, name, category, expiry_date, notes FROM food_items")
    items = c.fetchall()
    
    try:
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['ID', 'Name', 'Category', 'Expiry Date', 'Notes'])
            writer.writerows(items)
        messagebox.showinfo("Export Complete", f"Data exported to {file_path}")
    except Exception as e:
        messagebox.showerror("Export Error", f"Failed to export data: {e}")

# Reminder system
def check_expiry():
    today = datetime.now().date()
    expiry_threshold = today + timedelta(days=3)
    c.execute("SELECT name, expiry_date FROM food_items WHERE expiry_date <= ?", (expiry_threshold,))
    expiring_items = c.fetchall()
    
    if not expiring_items:
        messagebox.showinfo("Expiry Check", "No items are expiring soon.")
        return
        
    try:
        for item in expiring_items:
            name, exp_date = item
            days_left = (datetime.strptime(exp_date, "%Y-%m-%d").date() - today).days
            
            if days_left < 0:
                status = "EXPIRED"
            else:
                status = f"expires in {days_left} days"
                
            notification.notify(
                title="Food Expiry Alert",
                message=f"{name} {status}!",
                timeout=5
            )
        
        # Also show a messagebox with all expiring items
        expiry_msg = "Items expiring:\n\n"
        for item in expiring_items:
            name, exp_date = item
            expiry_msg += f"• {name} - {exp_date}\n"
            
        messagebox.showwarning("Expiry Alert", expiry_msg)
    except Exception as e:
        messagebox.showerror("Notification Error", f"Could not show notifications: {e}")

# Statistics and insights
def show_statistics():
    stats_window = tk.Toplevel(root)
    stats_window.title("Food Inventory Statistics")
    stats_window.geometry("500x400")
    
    bg_color = "#2E2E2E" if is_dark_mode else "#f4f4f9"
    fg_color = "white" if is_dark_mode else "#333333"
    stats_window.configure(bg=bg_color)
    
    # Get statistics
    today = datetime.now().date()
    
    # Total items
    c.execute("SELECT COUNT(*) FROM food_items")
    total_items = c.fetchone()[0]
    
    # Expired items
    c.execute("SELECT COUNT(*) FROM food_items WHERE expiry_date < ?", (today,))
    expired_items = c.fetchone()[0]
    
    # Items expiring soon (within 3 days)
    soon_date = today + timedelta(days=3)
    c.execute("SELECT COUNT(*) FROM food_items WHERE expiry_date BETWEEN ? AND ?", 
             (today, soon_date))
    soon_items = c.fetchone()[0]
    
    # Items by category
    c.execute("SELECT category, COUNT(*) FROM food_items GROUP BY category")
    categories = c.fetchall()
    
    # Create statistics display
    tk.Label(stats_window, text="Food Inventory Statistics", font=("Arial", 14, "bold"),
            bg=bg_color, fg=fg_color).pack(pady=10)
            
    # Summary frame
    summary_frame = tk.Frame(stats_window, bg=bg_color)
    summary_frame.pack(fill=tk.X, padx=20, pady=10)
    
    tk.Label(summary_frame, text=f"Total Items: {total_items}", font=("Arial", 12),
            bg=bg_color, fg=fg_color).pack(anchor="w")
    tk.Label(summary_frame, text=f"Expired Items: {expired_items}", font=("Arial", 12),
            bg=bg_color, fg=fg_color).pack(anchor="w")
    tk.Label(summary_frame, text=f"Items Expiring Soon: {soon_items}", font=("Arial", 12),
            bg=bg_color, fg=fg_color).pack(anchor="w")
    
    # Category breakdown
    tk.Label(stats_window, text="\nCategory Breakdown:", font=("Arial", 12, "bold"),
            bg=bg_color, fg=fg_color).pack(anchor="w", padx=20)
            
    for category, count in categories:
        tk.Label(stats_window, text=f"• {category}: {count} items", font=("Arial", 11),
                bg=bg_color, fg=fg_color).pack(anchor="w", padx=30)
    
    # Action log summary
    tk.Label(stats_window, text="\nRecent Activity:", font=("Arial", 12, "bold"),
            bg=bg_color, fg=fg_color).pack(anchor="w", padx=20, pady=(10, 0))
            
    c.execute("SELECT action, COUNT(*) FROM usage_log GROUP BY action ORDER BY COUNT(*) DESC LIMIT 5")
    actions = c.fetchall()
    
    for action, count in actions:
        tk.Label(stats_window, text=f"• {action.capitalize()}: {count} times", font=("Arial", 11),
                bg=bg_color, fg=fg_color).pack(anchor="w", padx=30)
    
    # Close button
    tk.Button(stats_window, text="Close", bg="#4CAF50", fg="white",
             command=stats_window.destroy).pack(pady=20)
    
    # Make dialog modal
    stats_window.transient(root)
    stats_window.grab_set()
    root.wait_window(stats_window)

# Create main frames for better organization
main_frame = tk.Frame(root, bg="#f4f4f9")
main_frame.pack(fill=tk.X, padx=20, pady=10)

tree_frame = tk.Frame(root, bg="#f4f4f9")
tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

button_frame = tk.Frame(root, bg="#f4f4f9")
button_frame.pack(fill=tk.X, padx=20, pady=10)

# GUI Widgets in main_frame
name_label = tk.Label(main_frame, text="Food Name:", bg="#f4f4f9", fg="#333333")
name_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
name_entry = tk.Entry(main_frame)
name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="we")

category_label = tk.Label(main_frame, text="Category:", bg="#f4f4f9", fg="#333333")
category_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
category_combobox = ttk.Combobox(main_frame, values=["Dairy", "Vegetables", "Meat", "Grains", "Fruits", "Other"])
category_combobox.grid(row=1, column=1, padx=10, pady=5, sticky="we")

expiry_label = tk.Label(main_frame, text="Expiry Date (YYYY-MM-DD):", bg="#f4f4f9", fg="#333333")
expiry_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
expiry_entry = tk.Entry(main_frame)
expiry_entry.grid(row=2, column=1, padx=10, pady=5, sticky="we")

notes_label = tk.Label(main_frame, text="Notes:", bg="#f4f4f9", fg="#333333")
notes_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
notes_entry = tk.Entry(main_frame)
notes_entry.grid(row=3, column=1, padx=10, pady=5, sticky="we")

add_button = tk.Button(main_frame, text="Add Item", bg="#4CAF50", fg="white", command=add_item)
add_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="we")

# Search and filter row
search_frame = tk.Frame(tree_frame, bg="#f4f4f9")
search_frame.pack(fill=tk.X, pady=5)

search_label = tk.Label(search_frame, text="Search:", bg="#f4f4f9", fg="#333333")
search_label.pack(side=tk.LEFT, padx=5)
search_entry = tk.Entry(search_frame, width=20)
search_entry.pack(side=tk.LEFT, padx=5)
search_entry.bind("<KeyRelease>", lambda e: refresh_items())

filter_label = tk.Label(search_frame, text="Filter by Category:", bg="#f4f4f9", fg="#333333")
filter_label.pack(side=tk.LEFT, padx=5)
filter_combobox = ttk.Combobox(search_frame, values=["All", "Dairy", "Vegetables", "Meat", "Grains", "Fruits", "Other"], width=15)
filter_combobox.current(0)
filter_combobox.pack(side=tk.LEFT, padx=5)
filter_combobox.bind("<<ComboboxSelected>>", lambda e: refresh_items())

# Sort options
sort_label = tk.Label(search_frame, text="Sort by:", bg="#f4f4f9", fg="#333333")
sort_label.pack(side=tk.LEFT, padx=5)
sort_combobox = ttk.Combobox(search_frame, values=["expiry_date", "name", "category"], width=15)
sort_combobox.current(0)
sort_combobox.pack(side=tk.LEFT, padx=5)
sort_combobox.bind("<<ComboboxSelected>>", lambda e: refresh_items(sort_combobox.get()))

# Treeview
columns = ("ID", "Name", "Category", "Expiry Date", "Notes")
tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

# Define column widths and headings
column_widths = [50, 150, 100, 100, 300]
for i, col in enumerate(columns):
    tree.heading(col, text=col)
    tree.column(col, width=column_widths[i])

tree.pack(fill=tk.BOTH, expand=True, pady=10)

# Scrollbar for treeview
scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.place(relx=1, rely=0, relheight=1, anchor='ne')

# Double-click to edit
tree.bind("<Double-1>", lambda e: edit_item())

# Color coding
tree.tag_configure('expired', background='tomato')
tree.tag_configure('soon', background='khaki')
tree.tag_configure('fresh', background='palegreen')

# Action buttons in button_frame
button_frame.columnconfigure((0,1,2), weight=1)  # Equal weight for buttons

edit_button = tk.Button(button_frame, text="Edit Selected", bg="#2196F3", fg="white", command=edit_item)
edit_button.grid(row=0, column=0, padx=5, pady=10, sticky="we")

delete_button = tk.Button(button_frame, text="Delete Selected", bg="#F44336", fg="white", command=delete_selected)
delete_button.grid(row=0, column=1, padx=5, pady=10, sticky="we")

export_button = tk.Button(button_frame, text="Export to CSV", bg="#9C27B0", fg="white", command=export_to_csv)
export_button.grid(row=0, column=2, padx=5, pady=10, sticky="we")

reminder_button = tk.Button(button_frame, text="Check Expiry Reminders", bg="#FF9800", fg="white", command=check_expiry)
reminder_button.grid(row=1, column=0, padx=5, pady=10, sticky="we")

stats_button = tk.Button(button_frame, text="View Statistics", bg="#795548", fg="white", command=show_statistics)
stats_button.grid(row=1, column=1, padx=5, pady=10, sticky="we")

darkmode_button = tk.Button(button_frame, text="Toggle Dark Mode", bg="#555", fg="white", command=toggle_dark_mode)
darkmode_button.grid(row=1, column=2, padx=5, pady=10, sticky="we")

# Configure grid weights for main window
main_frame.columnconfigure(0, weight=1)
main_frame.columnconfigure(1, weight=3)

# Initialize styles
bg, fg, button_bg = setup_styles()

# Initial refresh
refresh_items()

# Check for expiring items on startup
root.after(1000, check_expiry)  # Check after 1 second of startup

root.mainloop()
conn.close() 