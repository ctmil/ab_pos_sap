# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.osv import osv
from openerp.exceptions import except_orm, ValidationError
from StringIO import StringIO
import urllib2, httplib, urlparse, gzip, requests, json
import openerp.addons.decimal_precision as dp
import logging
import datetime
from openerp.fields import Date as newdate
from datetime import datetime,date
import csv

class pos_session(models.Model):
        _inherit = 'pos.session'

	@api.multi
        def generate_files(self):
		self.ensure_one()
                output_directory = self.env['ir.config_parameter'].search([('key','=','ab_pos_output_directory')])
                if not output_directory:
                        raise osv.except_osv('Error','No esta parametrizado ab_pos_output_directory\nComuniquese con el administrador')
		# Asientos
                filename = 'ASIENTOSODOOSAP'
                session = self
		fechahora = session.start_at[:16]
		fechahora = fechahora.replace(' ','')
		fechahora = fechahora.replace(':','')
		fechahora = fechahora.replace('-','')
                fecha = session.start_at[:10]
                ofile  = open(output_directory.value + '/' + filename + fechahora + '.txt', "wb")
                writer = csv.writer(ofile, delimiter='|', quoting=csv.QUOTE_NONE)
		# Cabecera 0
		total_amount = 0
		for order in session.order_ids:
			if order.state in ['paid','invoiced','done']:
				total_amount = total_amount + order.amount_total
                row = [0,session.name,len(session.order_ids),total_amount]
                writer.writerow(row)
		sistema_origen = 'ODOO'
		source_id = None
		id_proceso = '10'
		ref = None
		header_txt = None
		doc_date = None
		pstng_date = None
		acct_receivable = None
		acct_vat = None
		acct_sales = None
		row_line1 = []
		row_line2 = []
		row_line3 = []
		
		row_payments = []

		for order in session.order_ids:
			if order.state in ['paid','invoiced','done']:
				source_id = order.id
				ref = order.pos_reference
				header_txt = order.pos_reference
				doc_date = fecha[8:10] + fecha[5:7] + fecha[0:4]
				pstng_date = fecha[8:10] + fecha[5:7] + fecha[0:4]

				acct_receivable = session.config_id.account_receivable.sap_account
				acct_vat = session.config_id.account_vat.sap_account
				acct_sales = session.config_id.account_sales.sap_account
				row_line1 = [2,acct_receivable,'ARS',order.amount_total,'','Deudores por Venta','','']
				row_line2 = [2,acct_sales,'ARS',order.amount_total - order.amount_tax,'-','Ventas','','']
				row_line3 = [2,acct_vat,'ARS',order.amount_tax,'-','IVA','','']
				
				for payment in order.statement_ids:
					if payment.journal_id.is_credit_card:
						tipo_proc = '21'
					else:
						tipo_proc = '20'
					row_payment_line1 = ['2',acct_receivable,'ARS',payment.amount,'-','Ventas','','']
					row_payment_line2 = ['2',payment.journal_id.default_credit_account_id.sap_account,'ARS',payment.amount,'',payment.journal_id.name,'','']
					row_payments.append(row_payment_line1)
					row_payments.append(row_payment_line2)
			row = [1,sistema_origen,source_id,id_proceso,ref,header_txt,doc_date,pstng_date]
			writer.writerow(row)
			writer.writerow(row_line1)
			writer.writerow(row_line2)
			writer.writerow(row_line3)
			for row_payment in  row_payments:
				writer.writerow(row_payment)
			row_payments = []	
                ofile.close()

		# Libro de IVA
                filename = 'DETALLETICKET'
                session = self
		fechahora = session.start_at[:16]
		fechahora = fechahora.replace(' ','')
		fechahora = fechahora.replace(':','')
		fechahora = fechahora.replace('-','')
                fecha = session.start_at[:10]
                ofile  = open(output_directory.value + '/' + filename + fechahora + '.txt', "wb")
                writer = csv.writer(ofile, delimiter='|', quoting=csv.QUOTE_NONE)
		sistema_origen = 'ODOO'
		source_id = None
		id_proceso = '10'
		ref = None
		header_txt = None
		doc_date = None
		pstng_date = None
		acct_receivable = None
		acct_vat = None
		acct_sales = None
		
		for order in session.order_ids:
			if order.state in ['paid','invoiced','done']:
				source_id = order.id
				ref = order.pos_reference
				header_txt = order.pos_reference
				doc_date = fecha[8:10] + fecha[5:7] + fecha[0:4]
				pstng_date = fecha[8:10] + fecha[5:7] + fecha[0:4]

				acct_receivable = session.config_id.account_receivable.sap_account
				acct_vat = session.config_id.account_vat.sap_account
				acct_sales = session.config_id.account_sales.sap_account

				#partner_name = unicode(order.partner_id.name,errors='ignore')
				partner_name = order.partner_id.name
				
				row = [doc_date,order.id,'TFC',order.pos_reference,order.partner_id.document_number,partner_name,\
					order.amount_total - order.amount_tax,'','',\
					order.amount_tax,'','','',order.amount_total,pstng_date]
				writer.writerow(row)
                ofile.close()

		# Libro de IVA
                filename = 'MOVIMIENTOSTOCKSAP'
                session = self
		fechahora = session.start_at[:16]
		fechahora = fechahora.replace(' ','')
		fechahora = fechahora.replace(':','')
		fechahora = fechahora.replace('-','')
                fecha = session.start_at[:10]
                ofile  = open(output_directory.value + '/' + filename + fechahora + '.txt', "wb")
                writer = csv.writer(ofile, delimiter='|', quoting=csv.QUOTE_NONE)
		sistema_origen = 'ODOO'
		source_id = None
		id_proceso = '10'
		ref = None
		header_txt = None
		doc_date = None
		pstng_date = None
		acct_receivable = None
		acct_vat = None
		acct_sales = None
		
		for order in session.order_ids:
			if order.state in ['paid','invoiced','done']:
				source_id = order.id
				ref = order.pos_reference
				header_txt = order.pos_reference
				doc_date = fecha[8:10] + fecha[5:7] + fecha[0:4]
				pstng_date = fecha[8:10] + fecha[5:7] + fecha[0:4]

				for line in order.lines:
							
					row = [doc_date,line.product_id.default_code,order.session_id.config_id.stock_location_id.sap_center,\
						order.session_id.config_id.stock_location_id.sap_warehouse,line.qty,line.product_id.product_tmpl_id.uom_id.name]
					writer.writerow(row)
                ofile.close()
		


                return None

class pos_config(models.Model):
	_inherit = 'pos.config'

	account_receivable = fields.Many2one('account.account',string='Cuenta Deudores por Venta')
	account_sales = fields.Many2one('account.account',string='Cuenta Ventas')
	account_vat = fields.Many2one('account.account',string='Cuenta Ventas')

class account_account(models.Model):
	_inherit = 'account.account'

	sap_account = fields.Char('Cuenta SAP')

class stock_location(models.Model):
	_inherit = 'stock.location'

	sap_center = fields.Char('Centro SAP')
	sap_warehouse = fields.Char('Almacen SAP')
