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
# from unidecode import unidecode

class product_category(models.Model):
        _inherit = 'product.category'

	sap_name = fields.Char('Categoria SAP')

class pos_session(models.Model):
        _inherit = 'pos.session'

	@api.one
	def generate_file(self):
		if self:
			self.generate_files(self.id)

	@api.model
        def generate_files(self,session_id=None):
		#self.ensure_one()
                output_directory = self.env['ir.config_parameter'].search([('key','=','ab_pos_output_directory')])
                if not output_directory:
                        raise osv.except_osv('Error','No esta parametrizado ab_pos_output_directory\nComuniquese con el administrador')
                #session = self
		if session_id:
			sessions = self.search([('id','=',session_id)])
		else:
			sessions = self.search([])
		for session in sessions:
			# Asientos
        	        filename = 'ASIENTOSODOOSAP'
			if not session:
				continue
                	#session = self
			fechahora = session.start_at[:16]
			fechahora = fechahora.replace(' ','')
			fechahora = fechahora.replace(':','')
			fechahora = fechahora.replace('-','')
        	        fecha = session.start_at[:10]
			filename_fechahora = fechahora[6:8] + fechahora[4:6] + fechahora[0:4] + fechahora[8:12]
			#import pdb;pdb.set_trace()
        	        ofile  = open(output_directory.value + '/' + filename + filename_fechahora + '.txt', "wb")
                	writer = csv.writer(ofile, delimiter='|', quoting=csv.QUOTE_NONE)
			# Cabecera 0
			total_amount = 0
			for order in session.order_ids:
				if order.state in ['paid','invoiced','done'] and order.pos_reference:
					total_amount = total_amount + abs(order.amount_total * 2) 
					for payment in order.statement_ids:
						total_amount = total_amount + abs(payment.amount * 2)
                	row = [0,session.name,len(session.order_ids)*2,total_amount]
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
				if not order.pos_reference:
					continue
				if order.state in ['paid','invoiced','done'] and order.pos_reference:
					id_proceso = '10'
					if order.partner_id.responsability_id.code == '1':
						tipo_factura = 'A'
					else:
						tipo_factura = 'B'
					source_id = order.id
					ref = order.pos_reference.replace('-',tipo_factura)
					header_txt = order.pos_reference
					doc_date = fecha[8:10] + fecha[5:7] + fecha[0:4]
					pstng_date = fecha[8:10] + fecha[5:7] + fecha[0:4]
	
					acct_receivable = session.config_id.account_receivable.code
					acct_vat = session.config_id.account_vat.code
					acct_sales = session.config_id.account_sales.code
					if order.amount_total > 0:
						row_line1 = [2,acct_receivable,'ARS',order.amount_total,'','Deudores por Venta','','']
						row_line2 = [2,acct_sales,'ARS',order.amount_total - order.amount_tax,'-','Ventas','','']
						row_line3 = [2,acct_vat,'ARS',order.amount_tax,'-','IVA','','']
					else:
						row_line1 = [2,acct_receivable,'ARS',order.amount_total * (-1),'-','Deudores por Venta','','']
						row_line2 = [2,acct_sales,'ARS',(order.amount_total - order.amount_tax) * (-1),'','Ventas','','']
						row_line3 = [2,acct_vat,'ARS',(order.amount_tax)*(-1),'','IVA','','']
					
				
					for payment in order.statement_ids:
						if payment.journal_id.is_credit_card:
							tipo_proc = '21'
						else:
							tipo_proc = '20'
						row_payment_line1 = ['2',acct_receivable,'ARS',abs(payment.amount),'-','Ventas','','']
						row_payment_line2 = ['2',payment.journal_id.default_credit_account_id.sap_account,'ARS',abs(payment.amount),'',payment.journal_id.name,'','']
						row_payments.append(row_payment_line1)
						row_payments.append(row_payment_line2)
				row = [1,sistema_origen,source_id,id_proceso,ref,header_txt,doc_date,pstng_date]
				row_1 = [1,sistema_origen,source_id,tipo_proc,ref,header_txt,doc_date,pstng_date]
				#writer.writerow(unidecode(row))
				try:
					writer.writerow(row)
					writer.writerow(row_line1)
					writer.writerow(row_line2)
					writer.writerow(row_line3)
					writer.writerow(row_1)
					for row_payment in  row_payments:
						writer.writerow(row_payment)
				except:
					import pdb;pdb.set_trace()
				row_payments = []	
	                ofile.close()

			# Libro de IVA
        	        filename = 'DETALLETICKET'
			fechahora = session.start_at[:16]
			fechahora = fechahora.replace(' ','')
			fechahora = fechahora.replace(':','')
			fechahora = fechahora.replace('-','')
        	        fecha = session.start_at[:10]
			filename_fechahora = fechahora[6:8] + fechahora[4:6] + fechahora[0:4] + fechahora[8:12]
	                ofile  = open(output_directory.value + '/' + filename + filename_fechahora + '.txt', "wb")
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
				
					net_amount_21 = 0
					net_amount_105 = 0
					tax_amount_21 = 0
					tax_amount_105 = 0
					no_gravados = 0
					#import pdb;pdb.set_trace()
					for line in order.lines:
						if line.product_id.tax_rate == 0.21:
							net_amount_21 = net_amount_21 + line.price_subtotal
							tax_amount_21 = tax_amount_21 + (line.price_subtotal_incl - line.price_subtotal)
						if line.product_id.tax_rate == 0.105:
							net_amount_105 = net_amount_105 + line.price_subtotal
							tax_amount_105 = tax_amount_105 + (line.price_subtotal_incl - line.price_subtotal)

					#partner_name = unicode(order.partner_id.name,errors='ignore')
					partner_name = order.partner_id.name
					#row = [doc_date,order.id,'TFC',order.pos_reference,order.partner_id.document_number,partner_name,\
					#	order.amount_total - order.amount_tax,'','',\
					#	order.amount_tax,'','','',order.amount_total,pstng_date]
					if order.partner_id.responsability_id.code == '1':
						tipo_comp = 'A'
					else:
						tipo_comp = 'B'
					if order.amount_total > 0:
						row = [doc_date,order.id,'TFC',tipo_comp,order.pos_reference,order.partner_id.document_number,partner_name,\
							net_amount_21,net_amount_105,no_gravados,\
							tax_amount_21,tax_amount_105,'','',order.amount_total,pstng_date]
					else:
						if order.amount_total < 0:
							row = [doc_date,order.id,'TNC',tipo_comp,order.pos_reference,order.partner_id.document_number,partner_name,\
								net_amount_21 * (-1),net_amount_105 * (-1),no_gravados,\
								tax_amount_21 * (-1),tax_amount_105 * (-1),'','',float(order.amount_total) * (-1),pstng_date]
					try:
						writer.writerow(row)
					except:
						import pdb;pdb.set_trace()
			for refund in session.refund_ids:
				if order.state in ['paid','open','done']:
					refund = refund.refund_id
					source_id = refund.id
					ref = refund.internal_number
					header_txt = refund.internal_number
					doc_date = fecha[8:10] + fecha[5:7] + fecha[0:4]
					pstng_date = fecha[8:10] + fecha[5:7] + fecha[0:4]
	
					acct_receivable = session.config_id.account_receivable.sap_account
					acct_vat = session.config_id.account_vat.sap_account
					acct_sales = session.config_id.account_sales.sap_account
					
					net_amount_21 = 0
					net_amount_105 = 0
					tax_amount_21 = 0
					tax_amount_105 = 0
					no_gravados = 0
					#import pdb;pdb.set_trace()
					for line in refund.invoice_line:
						net_amount = line.price_unit * line.quantity
						if line.product_id.tax_rate == 0.21:
							net_amount_21 = net_amount_21 + net_amount
							tax_amount_21 = tax_amount_21 + (net_amount * line.product_id.tax_rate)
						if line.product_id.tax_rate == 0.105:
							net_amount_105 = net_amount_105 + net_amount
							tax_amount_105 = tax_amount_105 + (net_amount * line.product_id.tax_rate)
		
					#partner_name = unicode(order.partner_id.name,errors='ignore')
					partner_name = order.partner_id.name
					#row = [doc_date,order.id,'TFC',order.pos_reference,order.partner_id.document_number,partner_name,\
					#	order.amount_total - order.amount_tax,'','',\
					#	order.amount_tax,'','','',order.amount_total,pstng_date]
					row = [doc_date,refund.id,'TNC',refund.internal_number,refund.partner_id.document_number,partner_name,\
						net_amount_21,net_amount_105,no_gravados,\
						tax_amount_21,tax_amount_105,'','',refund.amount_total,pstng_date]
					writer.writerow(row)
        	        ofile.close()
	
			# Libro de IVA
                	filename = 'MOVIMIENTOSTOCKSAP'
			fechahora = session.start_at[:16]
			fechahora = fechahora.replace(' ','')
			fechahora = fechahora.replace(':','')
			fechahora = fechahora.replace('-','')
			filename_fechahora = fechahora[6:8] + fechahora[4:6] + fechahora[0:4] + fechahora[8:12]
        	        fecha = session.start_at[:10]
                	ofile  = open(output_directory.value + '/' + filename + filename_fechahora + '.txt', "wb")
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
					doc_date = fecha[5:7] + '/' + fecha[8:10] + '/' + fecha[0:4]
					pstng_date = fecha[8:10] + fecha[5:7] + fecha[0:4]
	
					for line in order.lines:
						if line.product_id.type != 'service':	
							if 'No Brother' in line.product_id.product_tmpl_id.categ_id.complete_name:
								row = [doc_date,line.product_id.product_tmpl_id.categ_id.sap_name or line.product_id.product_tmpl_id.categ_id.complete_name,\
									order.session_id.config_id.stock_location_id.sap_center or order.session_id.config_id.stock_location_id.name,\
									order.session_id.config_id.stock_location_id.sap_warehouse or order.session_id.config_id.stock_location_id.name,\
									line.qty,'EA']
							else:	
								row = [doc_date,line.product_id.default_code or line.product_id.name,\
									order.session_id.config_id.stock_location_id.sap_center or order.session_id.config_id.stock_location_id.name,\
									order.session_id.config_id.stock_location_id.sap_warehouse or order.session_id.config_id.stock_location_id.name,\
									line.qty,'EA']
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
