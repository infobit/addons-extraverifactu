# Copyright 2025 Infobit Informatica
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields, _
from datetime import timedelta
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        for move in self:
            # Solo para facturas de venta
            if move.is_sale_document(include_receipts=True):
                if move.date:
                    limite = fields.Date.today() - timedelta(days=15)
                    if move.date < limite:
                        raise UserError(
                            _("La fecha de operación no puede ser anterior a %s (máximo 15 días respecto a hoy).")
                            % limite
                        )
        return super(AccountMove, self).action_post()

    @api.depends('invoice_date', 'company_id')
    def _compute_date(self):
        # Guardamos fecha original
        #self.date = fields.Date.context_today(self)
        if self.date: #and self.is_sale_document(include_receipts=True):
           original_date = self.date
        else:
           if self.invoice_date:
              original_date = self.invoice_date
           else:
              original_date = fields.Date.context_today(self)
        res = super(AccountMove, self)._compute_date()
        if self.is_sale_document(include_receipts=True):
           self.date = original_date
           # _affect_tax_report may trigger premature recompute of line_ids.date
           self.env.add_to_compute(self.line_ids._fields['date'], self.line_ids)
           # might be protected because `_get_accounting_date` requires the `name`
           self.env.add_to_compute(self._fields['name'], self)
        return res


    """@api.onchange('date')
    def _onchange_date(self):
       # Guardamos fecha original
        if self.date != self.invoice_date:
           original_date = self.date
        # Ejecutamos comportamiento estándar
        super(AccountMove, self)._onchange_date()
        # Si es factura de venta: mantener la fecha original y validar límite
        #raise Warning(self.is_sale_document(include_receipts=True))
        if self.is_sale_document(include_receipts=True):
            # Restaurar fecha original antes de validarla
            if self.date != self.invoice_date:
               self.date = original_date
            #raise Warning(self.date)"""
    
    def _get_verifactu_invoice_dict_out(self, cancel=False):
        res = super()._get_verifactu_invoice_dict_out(cancel)
        # Solo aplicar si RegistroAlta existe
        if "RegistroAlta" not in res:
            return res
        registro = res["RegistroAlta"]
        # Solo insertar FechaOperacion si invoice_date != date
        if self.invoice_date and self.date and self.invoice_date != self.date:
            nuevo_orden = {}
            insert_key = "FechaOperacion"
            insert_value = self._get_verifactu_date(self.date) #self.date.strftime("%d-%m-%Y") if hasattr(self.date, "strftime") else self.date
            for k, v in registro.items():
                # Insertar antes de DescripcionOperacion
                if k == "DescripcionOperacion":
                    nuevo_orden[insert_key] = insert_value
                nuevo_orden[k] = v
            # Mantener estructura correcta
            res["RegistroAlta"] = nuevo_orden
        return res
