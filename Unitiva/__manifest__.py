{
    "name": "CianiUnitiva",
    "version": "1.0",
    "summary": "unitiva",
    "description": """
    Unitiva
    """,
    "author": "Gianmarco Ciani",
    "category": "Custom",
    "depends": ["base", "contacts", "sale", 'sale_management', "purchase", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
        "views/unitiva_views.xml",
        "views/ateco_views.xml",
        "views/vendite_views.xml",
        "views/motivazioni_views.xml",
        "views/menu_vendite_unitiva.xml",
        "wizard/wizard_vendite.xml",
        "wizard/wizard_invio_mail.xml"
    ],
    "installable": True,
    "application": False,
}