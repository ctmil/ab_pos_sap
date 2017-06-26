# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging
import psycopg2
import time
from datetime import datetime,date

from openerp import tools
from openerp.osv import fields, osv
from openerp.tools import float_is_zero
from openerp.tools.translate import _

import openerp.addons.decimal_precision as dp
import openerp.addons.product.product

import csv

_logger = logging.getLogger(__name__)

class pos_session(osv.osv):
	_inherit = 'pos.session'

	def wkf_action_close(self, cr, uid, ids, context=None):
		#for session_id in ids:
		#	return_id = self.pool.get('pos.session').generate_files(cr,uid,context=context)
		#self.generate_files()
		res = super(pos_session, self).wkf_action_close(cr, uid, ids, context=context)
		return res

pos_session()
