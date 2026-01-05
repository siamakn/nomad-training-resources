from nomad.config.models.plugins import AppEntryPoint
from nomad.config.models.ui import (
    App,
    AxisQuantity,
    Column,
    Dashboard,
    Layout,
    Menu,
    MenuItemHistogram,
    MenuItemTerms,
    MenuItemVisibility,
    SearchQuantities,
    WidgetHistogram,
    WidgetTerms,
)

SCHEMA = "nomad_training_resources.schema_packages.schema_package.TrainingResource"

# Search quantities (index-friendly mirror subsections)
Q_SUBJECT = f"data.subject_terms.value#{SCHEMA}"
Q_KEYWORD = f"data.keyword_terms.value#{SCHEMA}"
Q_INSTRUCTIONAL_METHOD = f"data.instructional_method_terms.value#{SCHEMA}"
Q_EDUCATIONAL_LEVEL = f"data.educational_level_terms.value#{SCHEMA}"
Q_RESOURCE_TYPE = f"data.learning_resource_type_terms.value#{SCHEMA}"
Q_FORMAT = f"data.format_terms.value#{SCHEMA}"
Q_LICENSE = f"data.license_terms.value#{SCHEMA}"

Q_TITLE = f"data.title#{SCHEMA}"
Q_IDENTIFIER = f"data.identifier#{SCHEMA}"
Q_DATE_CREATED = f"data.date_created#{SCHEMA}"
Q_DATE_MODIFIED = f"data.date_modified#{SCHEMA}"


training_resources_app = App(
    label="Training Resources",
    path="training-resources",
    category="Training",
    description="Explore NOMAD training resources.",
    readme=(
        "This app lets you browse and filter training materials stored with the "
        "TrainingResource schema. Use the filters and dashboard to find relevant "
        "tutorials, videos, examples, and documentation."
    ),
    filters_locked={
        "section_defs.definition_qualified_name": [SCHEMA],
    },
    search_quantities=SearchQuantities(
        include=[
            Q_TITLE,
            Q_IDENTIFIER,
            Q_SUBJECT,
            Q_KEYWORD,
            Q_INSTRUCTIONAL_METHOD,
            Q_EDUCATIONAL_LEVEL,
            Q_RESOURCE_TYPE,
            Q_FORMAT,
            Q_LICENSE,
            Q_DATE_CREATED,
            Q_DATE_MODIFIED,
            "authors.name",
        ]
    ),
    columns=[
        Column(quantity=Q_TITLE, label="Title", selected=True),
        Column(quantity=Q_IDENTIFIER, label="Identifier (URL)", selected=False),
        Column(quantity=Q_SUBJECT, label="Subject", selected=True),
        Column(quantity=Q_KEYWORD, label="Keyword", selected=True),
        Column(quantity=Q_INSTRUCTIONAL_METHOD, label="Instructional method", selected=True),
        Column(quantity=Q_EDUCATIONAL_LEVEL, label="Educational level", selected=True),
        Column(quantity=Q_RESOURCE_TYPE, label="Resource type", selected=True),
        Column(quantity=Q_FORMAT, label="Format", selected=True),
        Column(quantity=Q_LICENSE, label="License", selected=True),
        Column(quantity=Q_DATE_CREATED, label="Date created", selected=False),
        Column(quantity=Q_DATE_MODIFIED, label="Date modified", selected=False),
        Column(quantity="authors.name", label="Authors", selected=False),
    ],
    menu=Menu(
        title="Filters",
        items=[
            Menu(
                title="Find",
                items=[
                    MenuItemTerms(
                        search_quantity=Q_IDENTIFIER,
                        title="Find by URL (Identifier)",
                        show_input=True,
                        options=20,
                    ),
                ],
            ),
            Menu(
                title="Content",
                items=[
                    MenuItemTerms(search_quantity=Q_SUBJECT, title="Subject", show_input=True, options=20),
                    MenuItemTerms(search_quantity=Q_KEYWORD, title="Keyword", show_input=True, options=20),
                    MenuItemTerms(
                        search_quantity=Q_INSTRUCTIONAL_METHOD,
                        title="Instructional method",
                        show_input=True,
                        options=10,
                    ),
                    MenuItemTerms(
                        search_quantity=Q_EDUCATIONAL_LEVEL,
                        title="Educational level",
                        show_input=True,
                        options=10,
                    ),
                ],
            ),
            Menu(
                title="Resource metadata",
                items=[
                    MenuItemTerms(search_quantity=Q_RESOURCE_TYPE, title="Resource type", show_input=True, options=10),
                    MenuItemTerms(search_quantity=Q_FORMAT, title="Format", show_input=True, options=10),
                    MenuItemTerms(search_quantity=Q_LICENSE, title="License", show_input=True, options=10),
                ],
            ),
            Menu(
                title="Dates and authors",
                items=[
                    MenuItemHistogram(
                        title="Date created",
                        x={"search_quantity": Q_DATE_CREATED},
                        n_bins=40,
                        autorange=True,
                    ),
                    MenuItemHistogram(
                        title="Date modified",
                        x={"search_quantity": Q_DATE_MODIFIED},
                        n_bins=40,
                        autorange=True,
                    ),
                    MenuItemTerms(search_quantity="authors.name", title="Author", show_input=True, options=20),
                    MenuItemVisibility(title="Visibility"),
                ],
            ),
        ],
    ),
    dashboard=Dashboard(
        widgets=[
            WidgetHistogram(
                title="Resources over time",
                x=AxisQuantity(search_quantity=Q_DATE_CREATED),
                n_bins=40,
                autorange=True,
                layout={
                    "md": Layout(w=12, h=4, x=0, y=0, minW=6, minH=3),
                    "lg": Layout(w=12, h=4, x=0, y=0, minW=6, minH=3),
                },
            ),
            WidgetTerms(
                title="Subject",
                search_quantity=Q_SUBJECT,
                layout={
                    "md": Layout(w=6, h=4, x=0, y=4, minW=3, minH=3),
                    "lg": Layout(w=6, h=4, x=0, y=4, minW=3, minH=3),
                },
            ),
            WidgetTerms(
                title="Keyword",
                search_quantity=Q_KEYWORD,
                layout={
                    "md": Layout(w=6, h=4, x=6, y=4, minW=3, minH=3),
                    "lg": Layout(w=6, h=4, x=6, y=4, minW=3, minH=3),
                },
            ),
            WidgetTerms(
                title="Instructional method",
                search_quantity=Q_INSTRUCTIONAL_METHOD,
                layout={
                    "md": Layout(w=6, h=4, x=0, y=8, minW=3, minH=3),
                    "lg": Layout(w=6, h=4, x=0, y=8, minW=3, minH=3),
                },
            ),
            WidgetTerms(
                title="Educational level",
                search_quantity=Q_EDUCATIONAL_LEVEL,
                layout={
                    "md": Layout(w=6, h=4, x=6, y=8, minW=3, minH=3),
                    "lg": Layout(w=6, h=4, x=6, y=8, minW=3, minH=3),
                },
            ),
            WidgetTerms(
                title="Resource type",
                search_quantity=Q_RESOURCE_TYPE,
                layout={
                    "md": Layout(w=6, h=4, x=0, y=12, minW=3, minH=3),
                    "lg": Layout(w=6, h=4, x=0, y=12, minW=3, minH=3),
                },
            ),
            WidgetTerms(
                title="Format",
                search_quantity=Q_FORMAT,
                layout={
                    "md": Layout(w=6, h=4, x=6, y=12, minW=3, minH=3),
                    "lg": Layout(w=6, h=4, x=6, y=12, minW=3, minH=3),
                },
            ),
            WidgetTerms(
                title="License",
                search_quantity=Q_LICENSE,
                layout={
                    "md": Layout(w=12, h=4, x=0, y=16, minW=6, minH=3),
                    "lg": Layout(w=12, h=4, x=0, y=16, minW=6, minH=3),
                },
            ),
        ],
    ),
)


training_resources_app_entry_point = AppEntryPoint(
    name="training_resources",
    description="App for exploring training resources defined by the TrainingResource schema.",
    app=training_resources_app,
)
