{
    "name": "E-learning Website Enhanced",
    "version": "19.0.1.0.0",
    "category": "custom",
    "summary": "Advanced eLearning features: sequential content unlocking, evaluation surveys, and Vimeo-based video tracking.",
    "description": """
This module provides advanced enhancements to the Odoo eLearning platform.
Key Features:
- **Sequential unlocking of course content**: Users must complete each step before accessing the next one.
- **Evaluation surveys as course content**: Add course evaluation surveys and display aggregated ratings on the public course page.
- **Vimeo video tracking and progression control**: Enforce linear playback, block skipping, and register completion only at 100%.
""",
    "author": "Odoo PS",
    "depends": [
        "website_slides",
        "website_slides_survey",
        "survey",
        "website",
        "portal",
    ],
    "data": [
        "views/website_slides.xml",
        "views/slide_channel_view.xml",
        "views/slide_slide_view.xml",
        "views/survey_survey_view.xml",
        "views/website_slide_course_template.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_elearning_enhanced/static/src/js/slide_course_fullscreen.js",
            "website_elearning_enhanced/static/src/xml/website_slides_fullscreen.xml",
        ],
    },
    "installable": True,
    "license": "LGPL-3",
}
