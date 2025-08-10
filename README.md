# Metal Evaporation History Tracker - User Guide

A Streamlit application for tracking and managing metal evaporation deposition data with database storage and user-friendly interfaces.

## 📋 Table of Contents
- [Getting Started](#getting-started)
- [Page 1: View Data](#page-1-view-data)
- [Page 2: Add Entry](#page-2-add-entry)
- [Page 3: User Data](#page-3-user-data)
- [Page 4: Staff Only](#page-4-staff-only)

---

## Getting Started

The application has four main pages accessible from the sidebar navigation:
1. **📈 View Data** - Browse deposition data by material
2. **➕ Add Entry** - Create new deposition entries
3. **📊 User Data** - View and edit user-specific data
4. **🔒 Staff Only** - Administrative functions

---

## Page 1: View Data

**Purpose**: Browse and visualize deposition data filtered by material type.

### Sidebar Controls
- **Select Material**: Dropdown menu showing all available materials
  - Defaults to "Gold" if available
  - Choose any material to filter the data
  - Shows record count for selected material

### Main Page Features
- **Data Table**: Displays all records for the selected material
  - Columns: Date, User, Threshold Power, Power Deposition, Rate, Thickness, Measured Thickness, Crystal Monitor
  - Sorted by date (most recent first)
  - Row numbers for easy reference

- **Summary Statistics**: 
  - Total number of records for selected material
  - Date range of available data

### How to Use
1. Select a material from the sidebar dropdown
2. View the filtered data in the main table
3. Use the sidebar to see record counts and date ranges
4. Switch between materials to compare different datasets

---

## Page 2: Add Entry

**Purpose**: Create new deposition entries with all required parameters.

### Sidebar
- No sidebar controls on this page

### Main Page Features

#### Auto-Generated Information
- **Date**: Automatically set to today's date (MM/DD/YYYY format)

#### Required Fields (marked with *)
- **User**: Dropdown menu of all registered users
  - Select "None" to see validation error
  - Choose the user who performed the deposition

- **Material**: Dropdown menu of all available materials
  - Alphabetically sorted for easy selection
  - Choose the material that was deposited

- **Threshold Power (%)**: Number input (0-100%)
  - Enter the threshold power percentage
  - Step: 0.1% increments

- **Deposition Power (%)**: Number input (0-100%)
  - Enter the deposition power percentage
  - Step: 0.1% increments

- **Rate (A/s)**: Number input (0-100 A/s)
  - Enter deposition rate in Angstroms per second
  - Step: 0.01 increments

- **Thickness (nm)**: Number input (0-10,000 nm)
  - Enter target thickness in nanometers
  - Step: 0.01 increments

- **Crystal Monitor**: Number input (0-100%)
  - Enter crystal monitor reading
  - Step: 0.01 increments

#### Optional Fields
- **Measured Thickness (nm)**: Number input (0-10,000 nm)
  - Enter actual measured thickness if available
  - Can be left empty and updated later
  - Step: 0.01 increments

- **Notes**: Text area for additional comments
  - Free-form text for detailed observations
  - Optional but recommended for important details

#### Validation
- All required fields must be greater than 0
- User and Material must be selected (not "None")
- Real-time validation with clear error messages

#### Submission
- **Add Entry Button**: Saves the entry to the database
- **Success Message**: Appears below the button after successful submission
- **Form Reset**: All fields clear automatically after successful submission

### How to Use
1. Fill in all required fields (marked with *)
2. Optionally add measured thickness and notes
3. Click "Add Entry" to save
4. Check for validation errors if submission fails
5. Success message confirms entry was saved
6. Form automatically clears for next entry

---

## Page 3: User Data

**Purpose**: View, filter, and edit deposition data for specific users.

### Sidebar Controls
- **Select User**: Dropdown menu with user options
  - "All Users" - View combined data from all users
  - Individual user names - View data for specific user
- **User Info**: Shows selected user and record count

### Main Page Features

#### Data Display
- **Header**: Shows whether viewing all users (👥) or specific user (👤)
- **Summary Metrics**: 
  - Total Records count
  - Unique Materials count
- **Data Table**: Complete deposition history
  - All columns including Notes and Measured Thickness
  - Row numbers starting from 1
  - Sorted by date (most recent first)

#### Edit Functionality (Only for Specific Users)
- **Edit Row Button**: Appears only when viewing a specific user's data
  - Hidden when "All Users" is selected
  - Click to toggle edit mode on/off

##### Edit Mode Interface
- **Row Selection**: Enter row number to edit (1 to max rows)
  - Number input for fast selection with many records
  - Shows valid range (e.g., "1 to 45")

- **Side-by-Side Comparison**:
  - **Left Column (Current Values)**: Read-only display of existing data
  - **Right Column (New Values)**: Editable inputs for updates

##### Editable Fields
- **Date**: Date picker with MM/DD/YYYY format
- **User**: Text input (can change user assignment)
- **Material**: Text input (can change material)
- **Threshold Power**: Number input (0-100%, step 0.1)
- **Power Deposition**: Number input (0-100%, step 0.1)
- **Rate**: Number input (0-100 A/s, step 0.1)
- **Thickness**: Number input (0-10,000 nm, step 0.1)
- **Measured Thickness**: Number input (0-10,000 nm, step 0.1, optional)
- **Crystal Monitor**: Number input (0-100%, step 0.1)
- **Notes**: Text area for detailed comments

##### Save/Cancel Actions
- **Save Changes**: 
  - Validates all required fields
  - Updates database record
  - Shows success message below buttons
  - Refreshes page with updated data
- **Cancel**: 
  - Closes edit interface immediately
  - Returns to main table view
  - No changes are saved

#### Success Messages
- **Green Banner**: Appears below Save/Cancel buttons after successful update
- **Dismiss Button**: Click to clear the success message
- **Persistent**: Message stays visible until dismissed

### How to Use

#### Viewing Data
1. Select user from sidebar dropdown
2. Choose "All Users" for overview or specific user for detailed view
3. Review summary statistics
4. Browse data table with row numbers

#### Editing Data (Specific User Only)
1. Select a specific user (not "All Users")
2. Click "✏️ Edit Row" button
3. Enter the row number you want to edit
4. Compare current vs. new values side-by-side
5. Modify any fields as needed
6. Click "💾 Save Changes" to update or "❌ Cancel" to exit
7. Success message confirms update
8. Click "✅ Dismiss" to clear success message

---

## Page 4: Staff Only

**Purpose**: Administrative functions for database management and system operations.

*Note: This page contains administrative functions and may require special permissions or training before use.*

### Features
- Database management tools
- User administration
- System maintenance functions
- Data import/export capabilities
- Advanced reporting features

### Access
- Restricted to authorized staff members
- May require additional authentication
- Contact system administrator for access

---

## 💡 Tips and Best Practices

### Data Entry
- **Be Consistent**: Use consistent naming and units across entries
- **Add Notes**: Include relevant observations and conditions
- **Verify Units**: Double-check that values are in correct units (nm, A/s, %)
- **Regular Backups**: Staff should regularly backup important data

### Navigation
- **Use Sidebar**: Efficiently filter and navigate data using sidebar controls
- **Row Numbers**: Use row numbers for quick reference when editing
- **Material Defaults**: View Data page defaults to Gold for convenience

### Editing
- **Double-Check**: Always verify changes before clicking Save
- **Use Cancel**: Don't hesitate to cancel if you make a mistake
- **One at a Time**: Edit one row at a time for accuracy
- **Check Units**: Ensure edited values maintain proper units

### Troubleshooting
- **Validation Errors**: Read error messages carefully and fix highlighted issues
- **Save Issues**: Ensure all required fields are filled with valid values
- **Missing Data**: Contact staff if expected users or materials don't appear
- **Performance**: For large datasets, use specific user selection instead of "All Users"

---

## 📞 Support

For technical issues, questions about data, or requests for new features, contact your system administrator or the development team.

**Remember**: This application tracks important scientific data - always double-check your entries for accuracy!
