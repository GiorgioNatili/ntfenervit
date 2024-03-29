try:
    from sorl.thumbnail.fields import ImageWithThumbnailsField
except ImportError:

    from django.db.models import ImageField
    
    class ImageWithThumbnailsField(ImageField):
        def __init__(self, *args, **kwargs):
            kwargs.pop('thumbnail', None)
            kwargs.pop('extra_thumbnails', None)
            super(ImageWithThumbnailsField, self).__init__(*args, **kwargs)


from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^survey\.fields\.ImageWithThumbnailsField"])