# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'AB POS SAP',
    'version': '8.0.1',
    'category': 'Point Of Sale',
    'sequence': 1,
    'summary': 'AB Point of sale',
    'depends': [
        "ab_pos",
	"account",
	"point_of_sale"
    ],
    'data': [
	"ab_pos_sap_view.xml"
    ],
    'demo': [
    ],
    'qweb': [
        'static/src/xml/pos.xml'
    ],
    'installable': True,
    'license': 'AGPL-3',
}
