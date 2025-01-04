# Sales Invoice Portal Dashboard for Odoo

## Overview
The **Sales Invoice Portal Dashboard** module enhances the functionality of the portal in Odoo by providing an intuitive and customizable dashboard for managing sales and invoices. It is designed to give users quick access to critical data and improve user experience for portal users such as customers or partners.

## Features
- Interactive dashboard for sales orders and invoices.
- Displays key metrics such as:
  - Total sales
  - Total invoices
- Charts and graphs for visual representation of data.
- Easy navigation to detailed views of sales orders and invoices.
- Mobile-friendly design for optimal usability on all devices.

## Installation
1. Clone the repository into your Odoo `addons` directory:
   ```bash
   git clone https://github.com/xS21ATM/sales_invoice_portal_dashboard.git
   ```
2. Restart your Odoo server to recognize the new module:
   ```bash
   ./odoo-bin -c <config_file> -d <database_name> -u all
   ```
3. Navigate to **Apps** in the Odoo backend.
4. Search for `Sales Invoice Portal Dashboard` and install it.

## Usage
1. Once installed, the portal users will see an enhanced dashboard under their **Portal** view.
2. The dashboard will display:
   - Recent sales orders and their status.
   - Invoice summaries (paid, unpaid, overdue).
   - Payment actions for overdue invoices.
3. Charts and graphs provide an at-a-glance view of financial data.

## Dependencies
- Odoo version: 14.0+ (Adjust based on the version compatibility mentioned in the repository)
- Required modules:
  - `sale`
  - `account`
  - `portal`

## Configuration
1. Navigate to **Settings** > **Portal** to configure the fields and data visible on the dashboard.
2. Assign portal access to users as needed to grant them access to the dashboard.

## Screenshots
Include screenshots or GIFs showcasing the dashboard interface.

## Contributing
Contributions are welcome! Please fork the repository, make your changes, and submit a pull request.

## License
This module is released under the MIT License (or the license mentioned in the repository).

## Author
Developed and maintained by **xS21ATM**.

---

If you have access to the repository, ensure that specific instructions or additional features mentioned in the codebase are included in the README for completeness.

Feature 
1st
Portal Dashbord Click
![Screenshot from 2025-01-04 14-38-54](https://github.com/user-attachments/assets/50a20849-fd7f-4e38-bb4f-aa943bf1b741)
2nd
Sales
sales List
![Screenshot from 2025-01-04 14-39-08](https://github.com/user-attachments/assets/322251cb-e2a4-4a9f-ad71-310ab67f78c5)
3rd
New Sakes Order Create
![Screenshot from 2025-01-04 14-39-19](https://github.com/user-attachments/assets/2466e9dd-4f9c-42c8-b5b7-04000e3ad3a2)
4rd
New Customer Create
![Screenshot from 2025-01-04 14-39-31](https://github.com/user-attachments/assets/248cca4e-7eb3-4142-ad70-5438bf6079cf)

"Add an invoice feature to update the time issue and include the next working time schedule."
