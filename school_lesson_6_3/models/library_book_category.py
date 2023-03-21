from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class LibraryBookCategory(models.Model):
    """This is an extension of the model from module school_lesson_6_1"""
    _inherit = 'library.book.category'

    name = fields.Char(index=True, required=True)
    complete_name = fields.Char(compute='_compute_complete_name',
                                recursive=True,
                                store=True)
    parent_id = fields.Many2one(comodel_name='library.book.category',
                                string='Parent Category',
                                index=True,
                                ondelete='cascade')
    parent_path = fields.Char(index=True)
    child_id = fields.One2many(comodel_name='library.book.category',
                               inverse_name='parent_id',
                               string='Child Categories')
    book_count = fields.Integer(compute='_compute_book_count')

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        """creating a hierarchical category name"""
        for category in self:
            if category.parent_id:
                category.complete_name = '%s / %s' % (
                    category.parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name

    def _compute_book_count(self):
        """counting the number of books in a category"""
        for categ in self:
            categ.book_count = self.env[
                'library.book'].search_count([
                    ('category_id', 'child_of', categ.id)
                ])

    @api.constrains('parent_id')
    def _check_category_recursion(self):
        """checking for recursive categories"""
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive categories.'))

    def get_category_books(self):
        """returns a list of all books in the current category"""
        return {
            "type": "ir.actions.act_window",
            "res_model": "library.book",
            "domain": [("category_id", "=", self.id)],
            "name": "Books",
            "view_mode": "tree",
        }
