from odoo import _, api, fields, models


class AccountStatementLineCreate(models.TransientModel):
    _name = "account.statement.line.create"
    _description = "Wizard to create statement lines"

    statement_id = fields.Many2one("account.bank.statement", string="Bank Statement")
    journal_id = fields.Many2one('account.journal', related='statement_id.journal_id')
    payment_ids = fields.Many2many("account.payment", string="Payments", domain="[('journal_id', '=', journal_id)]")

    @api.model
    def default_get(self, field_list):
        res = super().default_get(field_list)
        active_model = self.env.context.get("active_model")
        if active_model == "account.bank.statement":
            statement = (self.env[active_model].browse(self.env.context.get("active_id")).exists())
            if statement:
                res.update({"statement_id": statement.id, })
        return res

    def create_statement_lines(self):
        for rec in self:
            for payment in rec.payment_ids:
                line_obj = self.env["account.bank.statement.line"]
                line = line_obj.new(
                    {
                        "statement_id": rec.statement_id.id,
                        "date": payment.date,
                        "payment_ref": payment.name,
                        "partner_id": payment.partner_id.id,
                        "amount": payment.amount,

                    }
                )
                line = line_obj.create(line._convert_to_write(line._cache))
        return True
