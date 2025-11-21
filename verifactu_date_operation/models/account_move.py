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


    @api.onchange('invoice_date', 'highest_name', 'company_id')
    def _onchange_invoice_date(self):
        # Guardamos fecha original
        original_date = self.date
        # Ejecutamos comportamiento estándar
        super(AccountMove, self)._onchange_invoice_date()
        # Si es factura de venta: mantener la fecha original y validar límite
        if self.is_sale_document(include_receipts=True):
            # Restaurar fecha original antes de validarla
            self.date = original_date
            """# --- CONTROL DE ANTIGÜEDAD 15 DÍAS ---
            if self.date:
                limite = fields.Date.today() - timedelta(days=15)

                # Si la fecha es más antigua que (hoy - 15 días)
                if self.date < limite:
                    # Muestra error y restaura la fecha a límite
                    self.date = limite
                    return {
                        'warning': {
                            'title': _("Fecha demasiado antigua"),
                            'message': _(
                                "La fecha de operación no puede ser anterior a %s "
                                "(más de 15 días respecto a hoy)."
                            ) % limite
                        }
                    }"""

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
