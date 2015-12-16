# Script (Python) "initializeJsBuffer"
# bind container=container
# bind context=context
# bind namespace=
# bind script=script
# bind subpath=traverse_subpath
# parameters=
# title=
##


class joyRide:

    """
        objet pour l'ajout des joyrides sur une page.

    """

    joyRide = []

    def addJoyRide(self, file_name, macro_name):
        self.joyRide.append({"file": file_name, "macro": macro_name})

    def getJoyRide(self):
        return self.joyRide

    def isJoyRide(self):
        return True if self.joyRide else False

joyRide = joyRide()

return joyRide
