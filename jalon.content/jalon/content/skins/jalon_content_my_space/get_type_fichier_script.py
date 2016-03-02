## Controller Python Script "typefichier_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=imageName
##title=
##

"""
    À enrichir éventuellement en éditant les types mime de Zope,
    et en ajoutant des entrées dans le tableau ci-après :

        clé     = nom du fichier image retourné dans le "brain"
        valeur  = icône FA associée

"""

fileType = imageName.split('.')

return {
    'application':  'fa-file',
    'audio':        'fa-file-audio-o',
    'avi':          'fa-file-video-o',
    'doc':          'fa-file-word-o',
    'image':        'fa-file-image-o',
    'midi':         'fa-file-audio-o',
    'pdf':          'fa-file-pdf-o',
    'png':          'fa-file-image-o',
    'ppt':          'fa-file-powerpoint-o',
    'ps':           'fa-file-image-o',
    'quicktime':    'fa-file-video-o',
    'rpm':          'fa-file-archive-o',
    'sxc':          'fa-file-excel-o',
    'tar':          'fa-file-archive-o',
    'text':         'fa-file-text-o',
    'tgz':          'fa-file-archive-o',
    'txt':          'fa-file-text-o',
    'video':        'fa-file-video-o',
    'wav':          'fa-file-audio-o',
    'xls':          'fa-file-excel-o',
    'zip':          'fa-file-archive-o',
    }.get( fileType[ 0 ], 'fa-file-o' )
