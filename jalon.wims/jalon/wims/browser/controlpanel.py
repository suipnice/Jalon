# -*- coding: utf-8 -*-
"""Wims Control Panel."""
from zope.interface import implements
from plone.fieldsets.fieldsets import FormFieldsets
from plone.app.controlpanel.form import ControlPanelForm

from jalon.wims import contentMessageFactory as _
from jalon.wims.interfaces.utility import IWimsLayout, IWimsClasse
from jalon.wims.browser.interfaces.controlpanel import IWimsControlPanelForm


class WimsControlPanelForm(ControlPanelForm):

    """Wims Control Panel Form."""

    implements(IWimsControlPanelForm)

    wimslayout = FormFieldsets(IWimsLayout)
    wimslayout.id = 'wimslayout'
    wimslayout.label = _(u'Connexion')

    wimsclasse = FormFieldsets(IWimsClasse)
    wimsclasse.id = 'wimsclasse'
    wimsclasse.label = _(u'Classe')

    form_fields = FormFieldsets(wimslayout, wimsclasse)  # Wimslibraries

    label = _(u"Wims Settings")
    description = _(u"Settings for the Wims connector.")
    form_name = _("Wims Settings")
