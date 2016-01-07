# Script (Python) "initializeJsBuffer"
# bind container=container
# bind context=context
# bind namespace=
# bind script=script
# bind subpath=traverse_subpath
# parameters=
# title=
##


class jsBuffer:

    """
            Tunnel JavaScript

    Permet de charger du code JavaScript qui sera injecté juste avant </body>
    dans « main_template.pt » de trois manières, dans l'ordre suivant :
        - ExtraFiles : ces fichiers seront chargés via l'attribut src d'une
          balise <script /> après les fichiers JS standard de Jalon (app, post,
          staff-app, etc.), depuis le dossier « ./browser/scripts/ » du thème ;
        - DirectBuffer : ce code sera injecté directement dans une balise
          <script /> pour être évalué une fois l'ensemble des fichiers JS chargés ;
        - Buffer : ce code sera injecté dans une fonction « doc. ready » (dans
          une balise <script />) pour être évalué en dernier une fois l'ensemble
          du marquage chargé ;

    """

    jsBuffer = []
    jsDirectBuffer = []
    jsExtraFiles = []
    context = None

    def addJS(self, jsCode):
        self.jsBuffer.append("%s;" % jsCode)

    def addJSDirect(self, jsCode):
        self.jsDirectBuffer.append("%s;" % jsCode)

    def addFile(self, fileName):
        self.jsBuffer.append(str(getattr(self.context, "%s.min.js" % fileName)))

    def addFileDirect(self, fileName):
        self.jsDirectBuffer.append(str(getattr(self.context, "%s.min.js" % fileName)))

    def addExtraFile(self, fileName):
        self.jsExtraFiles.append("%s.min.js" % fileName)

    def getBuffer(self):
        if self.jsBuffer:
            js = ["\n/*<![CDATA[*/"]
            js.append("$( document ).ready( function ( ) {")
            js.append("\n".join(self.jsBuffer))
            js.append("} );")
            js.append("/*]]>*/\n\t\t")
            return "\n".join(js)
        else:
            return None

    def getDirectBuffer(self):
        if self.jsDirectBuffer:
            js = ["\n".join(self.jsDirectBuffer)]
            self.jsDirectBuffer = []
            js.append("\n\t\t")
            return "\n".join(js)
        else:
            return None

    def getExtraFiles(self):
        if self.jsExtraFiles:
            return self.jsExtraFiles
        else:
            return None

    def setContext(self, context):
        self.context = context

jsBuffer = jsBuffer()
jsBuffer.setContext(context)

return jsBuffer
