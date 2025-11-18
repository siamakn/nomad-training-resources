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

    # Restrict to your TrainingResource entries
    filters_locked={
        "section_defs.definition_qualified_name": [SCHEMA],
    },

    # Search quantities available to the app (menu, dashboard, etc.)
    # search_quantities=SearchQuantities(
    #     include=[
    #         f"data.subject.*#{SCHEMA}",
    #         f"data.keyword.*#{SCHEMA}",
    #         f"data.instructional_method.*#{SCHEMA}",
    #         f"data.educational_level_main#{SCHEMA}",
    #         f"data.learning_resource_type_main#{SCHEMA}",
    #         f"data.format_main#{SCHEMA}",
    #         f"data.license_main#{SCHEMA}",
    #         f"data.date_created#{SCHEMA}",
    #         f"data.date_modified#{SCHEMA}",
    #     ],
    # ),
    search_quantities=SearchQuantities(include=[f'data.*#{SCHEMA}']),
    # Table columns
    columns=[
        Column(
            quantity=f"data.title#{SCHEMA}",
            label="Title",
            selected=True,
        ),
        Column(
            quantity=f"data.subject#{SCHEMA}",
            label="Subject",
            selected=True,
        ),
        Column(
            quantity=f"data.keyword#{SCHEMA}",
            label="Keyword",
            selected=True,
        ),
        Column(
            quantity=f"data.instructional_method#{SCHEMA}",
            label="Instructional method",
            selected=True,
        ),
        Column(
            quantity=f"data.educational_level#{SCHEMA}",
            label="Educational level",
            selected=True,
        ),
        Column(
            quantity=f"data.learning_resource_type#{SCHEMA}",
            label="Resource type",
            selected=True,
        ),
        Column(
            quantity=f"data.format#{SCHEMA}",
            label="Format",
            selected=True,
        ),
        Column(
            quantity=f"data.license#{SCHEMA}",
            label="License",
            selected=True,
        ),
        Column(
            quantity=f"data.date_created#{SCHEMA}",
            label="Date created",
            selected=False,
        ),
        Column(
            quantity=f"data.date_modified#{SCHEMA}",
            label="Date modified",
            selected=False,
        ),
        Column(
            quantity="authors.name",
            label="Authors",
            selected=False,
        ),
    ],

    # Left-hand filter menu
    menu=Menu(
        title="Filters",
        items=[
            # Content-related filters
            Menu(
                title="Content",
                items=[
                    MenuItemTerms(
                        search_quantity=f"data.subject#{SCHEMA}",
                        title="Subject",
                        show_input=True,
                        options=20,
                    ),
                    MenuItemTerms(
                        search_quantity=f"data.keyword#{SCHEMA}",
                        title="Keyword",
                        show_input=True,
                        options=20,
                    ),
                    MenuItemTerms(
                        search_quantity=f"data.instructional_method#{SCHEMA}",
                        title="Instructional method",
                        show_input=True,
                        options=10,
                    ),
                    MenuItemTerms(
                        search_quantity=f"data.educational_level#{SCHEMA}",
                        title="Educational level",
                        show_input=True,
                        options=10,
                    ),
                ],
            ),
            # Resource metadata filters
            Menu(
                title="Resource metadata",
                items=[
                    MenuItemTerms(
                        search_quantity=f"data.learning_resource_type#{SCHEMA}",
                        title="Resource type",
                        show_input=True,
                        options=10,
                    ),
                    MenuItemTerms(
                        search_quantity=f"data.format#{SCHEMA}",
                        title="Format",
                        show_input=True,
                        options=10,
                    ),
                    MenuItemTerms(
                        search_quantity=f"data.license#{SCHEMA}",
                        title="License",
                        show_input=True,
                        options=10,
                    ),
                ],
            ),
            # Dates + author / visibility
            Menu(
                title="Dates and authors",
                items=[
                    MenuItemHistogram(
                        title="Date created",
                        x={"search_quantity": f"data.date_created#{SCHEMA}"},
                        n_bins=40,
                        autorange=True,
                    ),
                    MenuItemHistogram(
                        title="Date modified",
                        x={"search_quantity": f"data.date_modified#{SCHEMA}"},
                        n_bins=40,
                        autorange=True,
                    ),
                    MenuItemTerms(
                        search_quantity="authors.name",
                        title="Author",
                        show_input=True,
                        options=20,
                    ),
                    MenuItemVisibility(title="Visibility"),
                ],
            ),
        ],
    ),

    # Dashboard widgets (summary view)
    dashboard=Dashboard(
        widgets=[
            # Histogram of resources over time
            WidgetHistogram(
                title="Resources over time",
                x=AxisQuantity(search_quantity=f"data.date_created#{SCHEMA}"),
                n_bins=40,
                autorange=True,
                layout={
                    "md": Layout(w=12, h=4, x=0, y=0, minW=6, minH=3),
                    "lg": Layout(w=12, h=4, x=0, y=0, minW=6, minH=3),
                },
            ),
            # Subject
            WidgetTerms(
                title="Subject",
                search_quantity=f"data.subject#{SCHEMA}",
                layout={
                    "md": Layout(w=6, h=4, x=0, y=4, minW=3, minH=3),
                    "lg": Layout(w=6, h=4, x=0, y=4, minW=3, minH=3),
                },
            ),
            # Keyword
            WidgetTerms(
                title="Keyword",
                search_quantity=f"data.keyword#{SCHEMA}",
                layout={
                    "md": Layout(w=6, h=4, x=6, y=4, minW=3, minH=3),
                    "lg": Layout(w=6, h=4, x=6, y=4, minW=3, minH=3),
                },
            ),
            # Instructional method
            WidgetTerms(
                title="Instructional method",
                search_quantity=f"data.instructional_method#{SCHEMA}",
                layout={
                    "md": Layout(w=6, h=4, x=0, y=8, minW=3, minH=3),
                    "lg": Layout(w=6, h=4, x=0, y=8, minW=3, minH=3),
                },
            ),
            # Educational level
            WidgetTerms(
                title="Educational level",
                search_quantity=f"data.educational_level#{SCHEMA}",
                layout={
                    "md": Layout(w=6, h=4, x=6, y=8, minW=3, minH=3),
                    "lg": Layout(w=6, h=4, x=6, y=8, minW=3, minH=3),
                },
            ),
            # Resource type
            WidgetTerms(
                title="Resource type",
                search_quantity=f"data.learning_resource_type#{SCHEMA}",
                layout={
                    "md": Layout(w=6, h=4, x=0, y=12, minW=3, minH=3),
                    "lg": Layout(w=6, h=4, x=0, y=12, minW=3, minH=3),
                },
            ),
            # Format
            WidgetTerms(
                title="Format",
                search_quantity=f"data.format#{SCHEMA}",
                layout={
                    "md": Layout(w=6, h=4, x=6, y=12, minW=3, minH=3),
                    "lg": Layout(w=6, h=4, x=6, y=12, minW=3, minH=3),
                },
            ),
            # License
            WidgetTerms(
                title="License",
                search_quantity=f"data.license#{SCHEMA}",
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
