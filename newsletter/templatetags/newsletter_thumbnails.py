"""Basic template tag to generate and retrieve thumbnails."""
import os
from io import BytesIO

from PIL import Image

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.template import Library, Node


register = Library()

class ThumbnailNode(Node):
    def __init__(self, source_image, context_variable):
        self.source_variable = source_image
        self.context_variable = context_variable

    def _create_thumbnail_file_path(self, file_name):
        """Creates path to retrieve/save the thumbnail.
            Recreates the original image's media folder so it can be
            uploaded to the same folder.
        """
        # Break path into head and tail
        image_folders, full_image_name = os.path.split(file_name)

        # Break image name into the name and extension
        image_name, image_extension = os.path.splitext(full_image_name)

        # Break the path head into individual folders
        image_folder_parts = str(image_folders).split(os.path.sep)

        # Reconstruct the media folder for the original image
        # Uses the last 5 items because all files are uploaded with the
        # same structure: newsletter/images/<year>/<month>/<day>
        media_folder_path = image_folder_parts[-5:]

        # Combine media path parts and image name into one list
        thumbnail_path_parts = media_folder_path + [image_name]

        # Return the joined path and thumbnail name
        return '%s_thumbnail%s' % (
            os.path.sep.join(thumbnail_path_parts), image_extension
        )

    def _get_pillow_format(self, thumbnail):
        """Converts thumbnail format to an acceptable Pillow format."""
        _, extension = os.path.splitext(thumbnail)

        # Remove "." from front of extension
        extension = extension[1:]

        # If necessary convert extension to Pillow format
        pillow_conversions = {
            'jpg': 'JPEG'
        }
        try:
            extension = pillow_conversions[extension.lower()]
        except KeyError:
            pass

        return extension.upper()

    def _get_or_create_thumbnail(self, source_file):
        """Resizes, saves, and retrieves thumbnails."""
        thumbnail_path = self._create_thumbnail_file_path(source_file.name)

        # Check if thumbnail needs to be created
        if default_storage.exists(thumbnail_path) is False:
            # Create bytes object to hold the thumbnail in memory
            thumbnail_io = BytesIO()

            # Open the image and resize it
            original_image = Image.open(source_file)
            original_image.thumbnail((200, 200))

            # Save the image to the bytes object
            pillow_format = self._get_pillow_format(thumbnail_path)
            original_image.save(thumbnail_io, format=pillow_format)

            # Save the bytes object as a Django File
            default_storage.save(
                thumbnail_path, ContentFile(thumbnail_io.getvalue())
            )

        return default_storage.url(thumbnail_path)

    def render(self, context):
        # Get the source ImageFile from the filter expression
        source = self.source_variable.resolve(context)

        # Retrieve URL for the thumbnail
        thumbnail_url = self._get_or_create_thumbnail(source)

        # Assign the URL to the context variable
        context[self.context_variable] = thumbnail_url

        return '' # method expects string return value

@register.tag
def newsletter_thumbnail(parser, token):
    """Takes the provided ImageFile and returns a thumbnail URL."""
    # Split the tag into its components
    # Second item = image argument; last item = context variable
    tag_args = token.split_contents()

    # Retrieve the source image argument as a filter expression
    source_image = parser.compile_filter(tag_args[1])

    # Return the thumbnail
    return ThumbnailNode(source_image, tag_args[-1])
