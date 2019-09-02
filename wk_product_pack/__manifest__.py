# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Product Pack",
  "summary"              :  "Combine two or more products together in order to create a bundle product.",
  "category"             :  "Sales Management",
  "version"              :  "3.1.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Product-Pack.html",
  "description"          :  "http://webkul.com/blog/odoo-product-pack/",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=wk_product_pack&version=11.0",
  "depends"              :  [
                             'sale_stock',
                            ],
  "data"                 :  [
                             'wizard/product_pack_wizard.xml',
                             'views/wk_product_pack.xml',
                             'security/ir.model.access.csv',
                            ],
  "demo"                 :  ['demo/demo.xml'],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  69,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
}