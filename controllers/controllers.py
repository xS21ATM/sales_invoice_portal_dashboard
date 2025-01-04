# -*- coding: utf-8 -*-
import json

from odoo import http
from odoo.http import request, request as req
from odoo import Command
from datetime import datetime, time, date, timedelta
import math
from werkzeug.utils import redirect
import base64
from collections import defaultdict
import pytz
from odoo import models, fields, api
import calendar


def get_partner():
    user_id = req.env.user.id
    res_user = req.env['res.users'].sudo().search([('id', '=', user_id)], limit=1)

    if res_user:
        return res_user.partner_id
    else:
        return None


class bdPortal(http.Controller):

    @http.route('/ajax/create_new_client', type='http', auth='user', cors='*', csrf=False)
    def create_new_client(self, **kw):

        error = False
        error_response = {
            "status": "error",
            "error": {
                "code": 404,
                "message": "Error message"
            }
        }

        success_response = {
            "status": "success",
            "data": {
                "client": {}
            },
            "message": "New Client Created successfully."
        }

        # Validate
        client_user_name = kw.get('client_user_name')
        street = kw.get('street')
        city = kw.get('city')
        _zip = kw.get('zip')
        country_id = kw.get('country_id')
        phone = kw.get('phone')
        email = kw.get('email')
        website = kw.get('website')

        # If client not posted / pass
        if not client_user_name:
            error = True
            error_response['error']['message'] = 'Client id not passed'

        # Check if client already exists
        client = req.env['res.partner'].sudo().search([
            ('is_mp_customer', '=', True),
            ('name', '=', client_user_name),
        ])
        if client:
            error = True
            error_response['error'][
                'message'] = f'Already have a client <b>{client.name}</b>. Please try a different one'

        # Error response
        if error:
            return json.dumps(error_response)

        # Create new client
        client_values = {
            'is_mp_customer': True,
            'name': client_user_name,
            'street': street,
            'city': city,
            'zip': _zip,
            'country_id': country_id,
            'phone': phone,
            'email': email,
            'website': website,
        }

        new_client = req.env['res.partner'].sudo().sudo().create(client_values)

        if not new_client:
            error = True
            error_response['error']['message'] = 'Client not created'

        success_response['message'] = f'Successfully Client <b>{new_client.name}</b> Created'

        my_client = {
            "id": new_client.id,
            "client_user_name": new_client.name,
            "name": "yyy",
            "email": new_client.email,
            "phone": new_client.phone,
        }
        success_response['data']['client'] = my_client

        # Success response
        return json.dumps(success_response)

    """
    Portal Dashboard
    Monthly basis data will show
    """

    @http.route('/portal/dashboard', auth='user')
    def portal_dashboard(self, **kw):
        # Global Variables
        user_id = req.env.user

        # Get the current date
        current_date = date.today()

        # Get the first date of the current month
        first_day_of_month = datetime(current_date.year, current_date.month, 1)

        # Get the current year and month --------------
        a_now = datetime.now()
        a_year = a_now.year
        a_month = a_now.month

        # Get the last day of the current month
        last_day = calendar.monthrange(a_year, a_month)[1]

        print(f"The last day of the current month is: {last_day}")
        # Get the current year and month --------------

        # Get the last date of the current month
        if last_day == 31:
            last_day_of_month = datetime(current_date.year, current_date.month, 1) - timedelta(days=1)
            print('last_day_of_month', last_day_of_month)
        else:
            last_day_of_month = datetime(current_date.year, current_date.month + 1, 1) - timedelta(days=1)
            print('last_day_of_month', last_day_of_month)

        # Set the time components to the beginning of the day (00:00:00) for the first date
        first_day_of_month = first_day_of_month.replace(hour=0, minute=0, second=0)

        # Set the time components to the end of the day (23:59:59) for the last date
        last_day_of_month = last_day_of_month.replace(hour=23, minute=59, second=59)

        total_order = req.env['sale.order'].sudo().search([
            ('date_order', '>=', first_day_of_month),
            ('date_order', '<=', last_day_of_month),
            ('company_id', '=', user_id.company_id.id),
        ])
        """
        Best Sales Performer
        best_sales_performer
        """
        sales = req.env['sale.order'].sudo().search([
            ('date_order', '>=', first_day_of_month),
            ('date_order', '<=', last_day_of_month),
        ])

        best_sales = []
        for sale in sales:
            best_sale = [sale.sales_employee_id.id, sale.amount_total]
            best_sales.append(best_sale)

        # Initialize a dictionary to store the total sales amount for each employee ID
        sales_totals = defaultdict(float)

        # Calculate the total sales amount for each employee
        for employee in best_sales:
            employee_id, amount = employee
            sales_totals[employee_id] += amount

        # Find the employee ID with the highest total sales amount
        best_employee_id = None
        try:
            best_employee_id = max(sales_totals, key=sales_totals.get)
        except ValueError:
            pass

        best_sale_performer = req.env['hr.employee'].sudo().search([('id', '=', best_employee_id)])

        """
        Best Delivery Performer
        best_delivery_performer
        """
        sales_delivered = req.env['sale.order'].sudo().search([
            ('date_order', '>=', first_day_of_month),
            ('date_order', '<=', last_day_of_month),
        ])

        best_sales_delivered = []
        for sale_d in sales_delivered:
            best_sale_d = [sale_d.delivered_team_id.id, sale_d.amount_total]
            best_sales_delivered.append(best_sale_d)

        # Initialize a dictionary to store the total sales amount for each employee ID
        sales_totals_d = defaultdict(float)

        # Calculate the total sales amount for each employee
        for team in best_sales_delivered:
            team_id, amount = team
            sales_totals_d[team_id] += amount

        # Find the employee ID with the highest total sales amount
        best_team_id = None
        try:
            best_team_id = max(sales_totals_d, key=sales_totals_d.get)
        except ValueError:
            pass


        return req.render('sales_invoice_portal_dashboard.dashboard', {
            'total_order': total_order,
            'best_sale_performer': best_sale_performer,
        })

    # View all sales with pagination
    @http.route('/portal/sales', auth='user')
    def portal_sales(self, **kw):

        filter_order_id = kw.get('filter_order_id')
        is_filter = False
        user_id = req.env.user

        print('user_id:', user_id)

        # Filter by order number
        if filter_order_id:
            orders = req.env['sale.order'].sudo().search([('order_number', '=', filter_order_id)])
            is_filter = True

            return req.render('sales_invoice_portal_dashboard.sales', {
                'kw': kw,
                'orders': orders,
                'filter_order_id': filter_order_id,
                'is_filter': is_filter,
                'user_id': user_id,
            })
            # End filter by order number

        else:
            previous = 'enable'
            _next = 'enable'
            is_jumper_page = False
            jumper_page = 0

            current_page = 1
            if kw.get('page'):
                current_page = int(kw.get('page'))

            page = current_page - 1
            page_per_item = 10
            offset = page * page_per_item

            """
            filter_order_status
            """
            total_orders_domain = []
            if kw.get('filter_order_status'):
                filter_order_status = kw.get('filter_order_status')
                total_orders_domain.append(('state', '=', filter_order_status))
                is_filter = True

                if not user_id.is_project_manager:

                    emp = req.env['hr.employee'].sudo().search([('user_id2', '=', user_id.id)])
                    barcode = emp.barcode if emp else None

                    if barcode:
                        total_orders_domain.append(('employee_id_barcode', '=', barcode))

            print('total_orders_domain', total_orders_domain)
            total_orders = req.env['sale.order'].sudo().search_count(total_orders_domain)

            """
            filter_order_status
            For sale.order objects
            """
            orders_domain = []
            if kw.get('filter_order_status'):

                filter_order_status = kw.get('filter_order_status')
                orders_domain.append(('state', '=', filter_order_status))
                is_filter = True

                if not user_id.is_project_manager:

                    emp = req.env['hr.employee'].sudo().search([('user_id2', '=', user_id.id)])
                    barcode = emp.barcode if emp else None

                    if barcode:
                        orders_domain.append(('employee_id_barcode', '=', barcode))

            """
            Filter updates
            """
            if kw.get('f_sales_employee_id'):
                f_sales_employee_id = kw.get('f_sales_employee_id')
                orders_domain.append(('sales_employee_id', '=', int(f_sales_employee_id)))
                is_filter = True

            if kw.get('f_platform_source_id'):
                f_platform_source_id = kw.get('f_platform_source_id')
                orders_domain.append(('platform_source_id', '=', int(f_platform_source_id)))
                is_filter = True

            if kw.get('f_order_source_id'):
                f_order_source_id = kw.get('f_order_source_id')
                orders_domain.append(('order_source_id', '=', int(f_order_source_id)))
                is_filter = True

            if kw.get('f_profile_id'):
                f_profile_id = kw.get('f_profile_id')
                orders_domain.append(('profile_id', '=', int(f_profile_id)))
                is_filter = True

            if kw.get('f_client_user_id'):
                f_client_user_id = kw.get('f_client_user_id')
                orders_domain.append(('client_user_id', '=', int(f_client_user_id)))
                is_filter = True

            if kw.get('f_order_status'):
                f_order_status = kw.get('f_order_status')
                orders_domain.append(('state', '=', f_order_status))
                is_filter = True

            if kw.get('f_order_id'):
                f_order_id = kw.get('f_order_id')
                orders_domain.append(('order_number', '=', f_order_id))
                is_filter = True

            """
            End Filter updates
            """
            orders = req.env['sale.order'].sudo().search(orders_domain, offset=offset, limit=page_per_item)
            print('orders_domain', orders_domain)
            print('orders', orders)

            total_decimal_pages = total_orders / page_per_item
            total_pages = math.ceil(total_decimal_pages)

            if len(orders) < page_per_item:
                _next = 'disable'

            else:
                _next = 'enable'

            if page == 0:
                previous = 'disable'

            else:
                previous = 'enable'

            pagination_pages = total_pages - current_page
            pages = []
            future_page = current_page
            for pagination_page in range(pagination_pages):
                if pagination_page + 1 > page_per_item:
                    break

                future_page = future_page + 1
                pages.append(future_page)

            # print('pages', pages)

            if pages:
                jumper_page = pages[-1] + 5
                is_jumper_page = False
                # print('jumper_page', jumper_page)
                a_a = page_per_item * jumper_page
                b_b = a_a - page_per_item

                # print('a_a', a_a)
                # print('b_b', b_b)

                if b_b < total_orders:
                    # print('jumper_page available')
                    is_jumper_page = True

            url_params = ''
            if kw.get('filter_order_status'):
                url_params = url_params + f'&filter_order_status={kw.get("filter_order_status")}'

            return req.render('sales_invoice_portal_dashboard.sales', {
                'kw': kw,
                'orders': orders,
                'page_per_item': page_per_item,
                'previous': previous,
                'previous_page': current_page - 1,
                '_next': _next,
                'next_page': current_page + 1,
                'pages': pages,
                'current_page': current_page,
                'is_jumper_page': is_jumper_page,
                'jumper_page': jumper_page,
                'filter_order_id': filter_order_id,
                'url_params': url_params,
                'is_filter': is_filter,
                'user_id': user_id,
            })

    # Create sales from portal
    @http.route('/portal/sales/create', auth='user')
    def portal_sales_create(self, **kw):
        pt = get_partner()
        if not pt:
            return 'Partner not found'

        env_user = req.env.user

        # Service types
        service_types = req.env['product.template'].sudo().search([('portal_available', '=', True)])

        user_id = req.env.user.id
        print('user_id', user_id)

        company_id = req.env.company
        print('company_id', company_id)


        client_user_ids = req.env['res.partner'].sudo().search([])
        clients = []
        for client in client_user_ids:
            _client = {
                'id': client.id,
                'client_user_name': client.name,
                'name': client.name,
                'email': client.email,
                'phone': client.phone,
            }
            clients.append(_client)
        js_clients = json.dumps(clients)

        # Employee Details
        employee_id = req.env['hr.employee'].sudo().search([('user_id2', '=', user_id)])
        if not employee_id:
            return 'Employee not found for this user'

        # All Companies
        # companies = req.env['res.company'].sudo().search([('active', '=', True)])
        # print('companies', companies)

        # Sales Employee Details
        employees_ids = req.env['hr.employee'].sudo().search([('barcode', '!=', False)])
        employees = []
        for employee in employees_ids:
            _employee = {
                'id': employee.id,
                'name': employee.name,
                'barcode': employee.barcode,
                'company_name': employee.company_id.name if employee.company_id else None,
            }
            employees.append(_employee)
        js_employees = json.dumps(employees)

        # Server data
        # Server data
        server_data = {
            'service_types': None,
        }

        # Service types
        service_types_list = []
        for st in service_types:
            vals = {
                'id': st.id,
                'unit_price': st.list_price,
            }
            service_types_list.append(vals)

        server_data['service_types'] = service_types_list

        # Employee Information
        employee = {
            'id': employee_id.id,
            'barcode': employee_id.barcode if employee_id.barcode else '',
            'name': employee_id.name,
        }

        server_data['employee'] = employee

        # Make json
        js_server_data = json.dumps(server_data)

        # Start a session
        req.session['session_create_sale'] = True

        return req.render('sales_invoice_portal_dashboard.create_sale', {
            'service_types': service_types,
            'user_id': user_id,
            'company_id': company_id,
            'client_user_ids': client_user_ids,
            'js_clients': js_clients,
            'employee_id': employee_id,
            'js_employees': js_employees,
            'js_server_data': js_server_data,
            'env_user': env_user,
        })

    # Create sales status
    @http.route('/portal/sales/create/status', auth='user', csrf=False)
    def portal_sales_create_status(self, **kw):

        def get_datetime(datetime_string):
            # Example input from a datetime-local input
            delivery_last_date = datetime_string

            # Parse the input string to a datetime object
            dt_object = datetime.strptime(delivery_last_date, "%Y-%m-%dT%H:%M")

            # Convert the datetime object to UTC if needed
            # Assuming the input datetime is in local time and needs conversion to UTC
            local_tz = pytz.timezone("Asia/Dhaka")  # Replace with your local timezone
            local_dt = local_tz.localize(dt_object)
            utc_dt = local_dt.astimezone(pytz.utc)

            # Format the datetime object for Odoo's Datetime field
            odoo_formatted_datetime = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
            return odoo_formatted_datetime

        if not req.session.get('session_create_sale'):
            print('/portal/sales/create')
            return redirect('/portal/sales/create')

        req.session.pop('session_create_sale', None)

        sale_order_values = {
            # Employee
            'partner_id': kw.get('partner_id'),
            'partner_invoice_id': kw.get('partner_id'),
            'partner_shipping_id': kw.get('partner_id'),
            'date_order': datetime.now(),
            'reference': kw.get('order_reference'),
        }
        new_sale = req.env['sale.order'].sudo().create(sale_order_values)

        # Product process
        product_lines = None
        product_lines = kw.get('product_lines')
        print('product_lines', product_lines)
        _product_lines = None

        if product_lines:
            _product_lines = json.loads(kw.get('product_lines'))
            print('_product_lines', _product_lines)

        for product in _product_lines:
            request.env['sale.order.line'].sudo().create({
                'order_id': new_sale.id,
                'product_id': int(product.get('product_id')),
                'name': product.get('description'),
                'product_uom_qty': product.get('product_uom_qty'),
                'price_unit': product.get('price_unit'),
            })
        if new_sale:
            new_sale.sudo().action_confirm()
            print('Order created')
        else:
            print('Order not created')

        return req.render('sales_invoice_portal_dashboard.create_sale_status', {
            'order': new_sale,
        })

    """
    Create New Customer
    """

    @http.route('/portal/sales/create_new_customer', auth='user')
    def create_new_customer(self, **kw):
        # pt = get_partner()
        # if not pt:
        #     return 'Partner not found'

        req.session['session_create_new_customer'] = True

        return req.render('sales_invoice_portal_dashboard.create_new_customer', {
            'kw': kw,
        })

    @http.route('/portal/sales/create_new_customer/status', auth='user', csrf=False)
    def create_new_customer_status(self, **kw):

        session_create_new_customer = req.session.get('session_create_new_customer')
        if not session_create_new_customer:
            return redirect('/portal/sales/create_new_customer')

        req.session.pop('session_create_new_customer', None)

        # Create customer
        customer_values = kw

        if 'image_1920' in kw:
            image_1920_file = kw.get('image_1920')
            customer_values['image_1920'] = base64.b64encode(image_1920_file.read())

        new_customer = req.env['res.partner'].sudo().create(customer_values)

        alert_info = None
        alert_danger = None

        if new_customer:
            alert_info = f'Customer {new_customer.name} created successfully'
        else:
            alert_danger = f'Create New Customer Failed'

        return req.render('sales_invoice_portal_dashboard.create_new_customer_status', {
            'kw': kw,
            'new_customer': new_customer,
            'alert_info': alert_info,
            'alert_danger': alert_danger,
        })

    """
    View sale order details in edit mode
    """

    @http.route('/portal/sales/details', auth='user')
    def portal_sales_details(self, **kw):
        pt = get_partner()
        if not pt:
            return 'Partner not found'

        order_id = kw.get('order_id')
        if not order_id:
            return 'order_id not found'

        order_id = int(order_id)

        order = req.env['sale.order'].sudo().search([('id', '=', order_id)])
        print('order', order)
        if not order:
            return 'Order object not found'

        return req.render('sales_invoice_portal_dashboard.sale_details', {
            'order': order,
        })

    @http.route('/portal/notifications', auth='user')
    def portal_notifications(self, **kw):

        # Finance Notifications
        user = req.env.user
        fin_not = None

        if user.scm_department:
            fin_not = req.env['bd.notification'].sudo().search([('department', '=', 'finance')], limit=50)

            if fin_not:
                for fin_nt in fin_not:
                    fin_nt.mark_as_read = True

        return req.render('sales_invoice_portal_dashboard.notifications', {
            'fin_not': fin_not,
        })

    @http.route('/f_sales_employee_id', type='http', auth='none', cors='*', csrf=False)
    def f_sales_employee_id(self, **kw):

        error_response = {
            "status": "error",
            "error_code": "INVALID_INPUT",
            "message": "Invalid input provided.",
            "details": {
                "field": "username",
                "error": "Cannot be empty"
            }
        }

        success_response = {
            "status": "success",
            "data": {
                "message": "Operation completed successfully."
            }
        }

        # Get employee object from search
        query = kw.get('query')
        employees = req.env['hr.employee'].sudo().search([
            '|', '|',
            ('name', 'ilike', query),
            ('work_phone', 'ilike', query),
            ('work_email', 'ilike', query),
        ], limit=5)

        print('employees', employees)

        if employees:

            emp_recs = []

            for emp in employees:
                vals = {
                    'id': emp.id,
                    'name': emp.name,
                    'other': 'other',
                    'url': f'/portal/sales?page=1&f_sales_employee_id={emp.id}',
                }

                emp_recs.append(vals)

            success_response['data'] = emp_recs
            return json.dumps(success_response)

        else:
            return json.dumps(error_response)

    @http.route('/f_platform_source', type='http', auth='none', cors='*', csrf=False)
    def f_platform_source(self, **kw):

        error_response = {
            "status": "error",
            "error_code": "INVALID_INPUT",
            "message": "Invalid input provided.",
            "details": {
                "field": "username",
                "error": "Cannot be empty"
            }
        }

        success_response = {
            "status": "success",
            "data": {
                "message": "Operation completed successfully."
            }
        }

        # Get employee object from search
        query = kw.get('query')
        records = req.env['bd.platform_source'].sudo().search([
            ('name', 'ilike', query),
        ], limit=5)

        print('records', records)

        if records:

            recs = []

            for rec in records:
                vals = {
                    'id': rec.id,
                    'name': rec.name,
                    'url': f'/portal/sales?page=1&f_platform_source_id={rec.id}',
                }

                recs.append(vals)

            success_response['data'] = recs
            return json.dumps(success_response)

        else:
            return json.dumps(error_response)

    @http.route('/f_order_source', type='http', auth='none', cors='*', csrf=False)
    def f_order_source(self, **kw):

        error_response = {
            "status": "error",
            "error_code": "INVALID_INPUT",
            "message": "Invalid input provided.",
            "details": {
                "field": "username",
                "error": "Cannot be empty"
            }
        }

        success_response = {
            "status": "success",
            "data": {
                "message": "Operation completed successfully."
            }
        }

        # Get employee object from search
        query = kw.get('query')
        records = req.env['bd.order_source'].sudo().search([
            ('name', 'ilike', query),
        ], limit=5)

        print('records', records)

        if records:

            recs = []

            for rec in records:
                vals = {
                    'id': rec.id,
                    'name': rec.name,
                    'url': f'/portal/sales?page=1&f_order_source_id={rec.id}',
                }

                recs.append(vals)

            success_response['data'] = recs
            return json.dumps(success_response)

        else:
            return json.dumps(error_response)

    @http.route('/f_profile_id', type='http', auth='none', cors='*', csrf=False)
    def f_profile_id(self, **kw):

        error_response = {
            "status": "error",
            "error_code": "INVALID_INPUT",
            "message": "Invalid input provided.",
            "details": {
                "field": "username",
                "error": "Cannot be empty"
            }
        }

        success_response = {
            "status": "success",
            "data": {
                "message": "Operation completed successfully."
            }
        }

        # Get employee object from search
        query = kw.get('query')
        records = req.env['bd.profile'].sudo().search([
            ('name', 'ilike', query),
        ], limit=5)

        print('records', records)

        if records:

            recs = []

            for rec in records:
                vals = {
                    'id': rec.id,
                    'name': f'{rec.name}{" - " + rec.platform_source_id.name if rec.platform_source_id else None}',
                    'url': f'/portal/sales?page=1&f_profile_id={rec.id}',
                }

                recs.append(vals)

            success_response['data'] = recs
            return json.dumps(success_response)

        else:
            return json.dumps(error_response)

    @http.route('/f_client_user_id', type='http', auth='none', cors='*', csrf=False)
    def f_client_user_id(self, **kw):

        error_response = {
            "status": "error",
            "error_code": "INVALID_INPUT",
            "message": "Invalid input provided.",
            "details": {
                "field": "username",
                "error": "Cannot be empty"
            }
        }

        success_response = {
            "status": "success",
            "data": {
                "message": "Operation completed successfully."
            }
        }

        # Get employee object from search
        query = kw.get('query')
        records = req.env['res.partner'].sudo().search([
            ('mp_customer_fullname', 'ilike', query),
            ('is_mp_customer', '=', True),
        ], limit=5)

        print('records', records)

        if records:

            recs = []

            for rec in records:
                vals = {
                    'id': rec.id,
                    'name': rec.mp_customer_fullname,
                    'url': f'/portal/sales?page=1&f_client_user_id={rec.id}',
                }

                recs.append(vals)

            success_response['data'] = recs
            return json.dumps(success_response)

        else:
            return json.dumps(error_response)

    @http.route('/f_order_id', type='http', auth='none', cors='*', csrf=False)
    def f_order_id(self, **kw):

        error_response = {
            "status": "error",
            "error_code": "INVALID_INPUT",
            "message": "Invalid input provided.",
            "details": {
                "field": "username",
                "error": "Cannot be empty"
            }
        }

        success_response = {
            "status": "success",
            "data": {
                "message": "Operation completed successfully."
            }
        }

        # Get employee object from search
        query = kw.get('query')
        records = req.env['sale.order'].sudo().search([
            ('order_number', 'ilike', query),
        ], limit=5)

        print('records', records)

        if records:

            recs = []

            for rec in records:
                vals = {
                    'id': rec.id,
                    'name': rec.order_number,
                    'url': f'/portal/sales?page=1&f_order_id={rec.order_number}',
                }

                recs.append(vals)

            success_response['data'] = recs
            return json.dumps(success_response)

        else:
            return json.dumps(error_response)

    @http.route('/ajax_requisition_get_products', type='http', auth='none', cors='*', csrf=False)
    def ajax_requisition_get_products(self, **kw):

        print('ajax_requisition_get_products called')

        error_response = {
            "status": "error",
            "error_code": "INVALID_INPUT",
            "message": "Invalid input provided.",
            "details": {
                "field": "username",
                "error": "Cannot be empty"
            }
        }

        success_response = {
            "status": "success",
            "data": {
                "message": "Operation completed successfully."
            }
        }

        # Get employee object from search
        query = kw.get('query')
        products = req.env['product.product'].sudo().search([
            ('name', 'ilike', query)
        ], limit=5)

        print('products', products)

        if not products:
            return json.dumps(error_response)

        pd_recs = []

        for product in products:
            vals = {
                'id': product.id,
                'name': product.name,
                'other': 'other',
                'url': f'/portal/sales?page=1&f_sales_employee_id={product.id}',
            }

            pd_recs.append(vals)

        success_response['data'] = pd_recs
        return json.dumps(success_response)

    @http.route('/t666', type='http', auth='none', cors='*', csrf=False)
    def t666(self, **kw):

        # sale = req.env['sale.order'].sudo().search([('id', '=', 4301)])
        # order_line = sale.order_line
        # print('order_line', order_line)
        #
        # for line in order_line:
        #     print(line.price_unit)

        # full_path = req.httprequest.full_path
        # req.session['full_path'] = full_path

        req.session['is_redirected'] = False

        return 't666'

