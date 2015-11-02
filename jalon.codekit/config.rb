require 'compass/import-once/activate'
# Require any additional compass plugins here.
add_import_path "bower_components/foundation/scss"
add_import_path "bower_components/font-awesome/scss"
#add_import_path "bower_components/datetimepicker"


# Set this to the root of your project when deployed:
http_path = "/"
sass_dir = "scss"
css_dir = "../jalon.theme/jalon/theme/browser/css"
images_dir = "../jalon.theme/jalon/theme/browser/images"
javascripts_dir = "../jalon.theme/jalon/theme/browser/scripts"
fonts_dir = "../jalon.theme/jalon/theme/browser/fonts"

#output_style = :nested
#output_style = :expanded
output_style = :compressed

#environment = :development
environment = :production

# To enable relative paths to assets via compass helper functions. Uncomment:
relative_assets = true

# To disable debugging comments that display the original location of your selectors. Uncomment:
line_comments = false

color_output = false


# If you prefer the indented syntax, you might want to regenerate this
# project again passing --syntax sass, or you can uncomment this:
# preferred_syntax = :sass
# and then run:
# sass-convert -R --from scss --to sass scss scss && rm -rf sass && mv scss sass
