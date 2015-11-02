## Script (Python) "JSTranslate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

from Products.CMFCore.utils import getToolByName

class jsTranslate():

    jsTranslate = [ ]
    context = None

    def addJsTranslate( self, name_translate, value_translate=None ):
        translation_service = getToolByName(self.context, 'translation_service')
        if not value_translate:
            for liste in name_translate:
                translate = translation_service.translate(domain='jalon.content',
                                                          msgid=liste[1],
                                                          default=liste[1],
                                                          context=self.context)
                self.jsTranslate.append("var %s = '%s';" % (liste[0], translate))
        else:
            translate = translation_service.translate(domain='jalon.content',
                                                      msgid=value_translate,
                                                      default=value_translate,
                                                      context=self.context)
            self.jsTranslate.append("var %s = '%s';" % (name_translate, translate))

    def getJsTranslate( self ):
        if self.jsTranslate:
            js = [ "\n".join( self.jsTranslate ) ]
            js.append( "\n\t\t" )
            return "\n".join( js )
        else:
            return None

    def setContext( self, context ):
        self.context = context

newJsTranslate = jsTranslate()
newJsTranslate.setContext(context)

return newJsTranslate