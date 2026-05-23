"""
The MIT License (MIT)

Copyright (c) 2021-present Pycord Development

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

__all__ = ("ComponentLimits",)

class ComponentLimits:
    # View constraints
    VIEW_CHILDREN_MAX = 40

    # ActionRow constraints
    ACTION_ROW_CHILDREN_MAX = 5

    # Button constraints
    BUTTON_LABEL_MAX = 80

    # MediaGallery constraints
    MEDIA_GALLERY_ITEMS_MIN = 1
    MEDIA_GALLERY_ITEMS_MAX = 10

    # MediaGalleryItem constraints
    MEDIA_GALLERY_ITEM_DESCRIPTION_MAX = 256

    # Select constraints
    SELECT_PLACEHOLDER_MAX = 150
    SELECT_OPTIONS_MAX = 25
    SELECT_DEFAULT_VALUES_MAX = 25

    # Select option constraints
    SELECT_OPTION_LABEL_MAX = 100
    SELECT_OPTION_VALUE_MAX = 100
    SELECT_OPTION_DESCRIPTION_MAX = 100

    # Section constraints
    SECTION_ACCESSORY_MAX = 1
    SECTION_CHILDREN_MIN = 1
    SECTION_CHILDREN_MAX = 3

    # TextInput constraints
    TEXT_INPUT_MAX_COUNT = 5
    TEXT_INPUT_LABEL_MAX = 45
    TEXT_INPUT_PLACEHOLDER_MAX = 100
    TEXT_INPUT_MIN_LENGTH_MIN = 0
    TEXT_INPUT_MIN_LENGTH_MAX = 4000
    TEXT_INPUT_MAX_LENGTH_MIN = 1
    TEXT_INPUT_MAX_LENGTH_MAX = 4000
    TEXT_INPUT_VALUE_MAX = 4000

    # TextDisplay constraints
    TEXT_DISPLAY_CONTENT_MAX = 4000

    # Thumbnail constraints
    THUMBNAIL_DESCRIPTION_MAX = 256

    # Custom ID constraints
    CUSTOM_ID_MIN = 1
    CUSTOM_ID_MAX = 100

    # RadioGroup constraints
    RADIO_OPTIONS_MAX = 10

    # CheckboxGroup constraints
    CHECKBOX_OPTIONS_MAX = 10
    CHECKBOX_MIN_VALUES_MIN = 0
    CHECKBOX_MIN_VALUES_MAX = 10
    CHECKBOX_MAX_VALUES_MIN = 1
    CHECKBOX_MAX_VALUES_MAX = 10

    # FileUpload constraints
    FILE_UPLOAD_MIN_FILES = 0
    FILE_UPLOAD_MAX_FILES_MIN = 1
    FILE_UPLOAD_MAX_FILES_MAX = 10

    # Modal constraints
    MODAL_TITLE_MAX = 45
    MODAL_ROWS_MAX = 5
