from AccessControl.Permissions import manage_users
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService import registerMultiPlugin

import plugin

manage_add_bdd_form = PageTemplateFile('browser/add_plugin',
                            globals(), __name__='manage_add_bdd_form' )


def manage_add_bdd_helper( dispatcher, id, title=None, REQUEST=None ):
    """Add an bdd Helper to the PluggableAuthentication Service."""

    sp = plugin.BddHelper( id, title )
    dispatcher._setObject( sp.getId(), sp )

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect( '%s/manage_workspace'
                                      '?manage_tabs_message='
                                      'bddHelper+added.'
                                      % dispatcher.absolute_url() )


def register_bdd_plugin():
    try:
        registerMultiPlugin(plugin.BddHelper.meta_type)
    except RuntimeError:
        # make refresh users happy
        pass


def register_bdd_plugin_class(context):
    context.registerClass(plugin.BddHelper,
                          permission = manage_users,
                          constructors = (manage_add_bdd_form,
                                          manage_add_bdd_helper),
                          visibility = None,
                          icon='browser/icon.gif'
                         )
