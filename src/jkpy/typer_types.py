import typer

emailOption=typer.Option(
    "--email",
    "-e",
    help="Set user email for making jira requests.",
    is_eager=True,
)
tokenOption=typer.Option(
    "--token",
    "-t",
    help="Set api token for making jira requests.",
    is_eager=True
)
isSetupOption=typer.Option(
    "--isSetup",
    help="Specifies if the request is for setup only.",
    is_eager=True,
)
folderPathOption=typer.Option(
    "--folderPath",
    "-fp",
    help="A Path string specifying the primary folder path to export all generated files.",
    is_eager=True)
teamLabelsOption=typer.Option(
    "--teamLabels",
    "-tl",
    help="A Comma separated string specifying team labels used in the default query for filtering results by team. If specified, the config file will be updated with any new labels - else, the config file values are used.",
    is_eager=True)
nameLabelsOption=typer.Option(
    "--nameLabels",
    "-nl",
    help="A Comma separated string specifying name labels used in the default query for filtering results by user name. If specified, the config file will be updated with any new labels - else, the config file values are used.",
    is_eager=True)
statusTypesOption=typer.Option(
    "--statusTypes",
    "-st",
    help="A Comma separated string specifying ticket status types to be used in the default query in the CHANGED TO argument. If specified, the config file will be updated with any new status types - else, the config file values are used.",
    is_eager=True)
metricLabelsOption=typer.Option(
    "--metricLabels",
    "-ml",
    help="A Comma separated string specifying labels to run metrics on. If specified, the config file will be updated with metrics on any new labels - else, the config file values are used.",
    is_eager=True)
remove_metricLabelsOption=typer.Option(
    "--remove-metricLabels",
    help="A Comma separated string specifying metric labels to remove from the config.",
    is_eager=True,
)
remove_statusTypesOption=typer.Option(
    "--remove-statusTypes",
    help="A Comma separated string specifying status types to remove from the config.",
    is_eager=True,
)
remove_teamLabelsOption=typer.Option(
    "--remove-teamLabels",
    help="A Comma separated string specifying team labels to remove from the config. This will not remove any data from the <current_year>_kpis.xlsx file.",
    is_eager=True,
)
remove_nameLabelsOption=typer.Option(
    "--remove-nameLabels",
    help="A Comma separated string specifying name labels to remove from the config. This will not remove any data from the <current_year>_kpis.xlsx file.",
    is_eager=True,
)
startDateOption=typer.Option(
    "--startDate",
    help="A date string specifying the start date to be used for the default query.'<1-12>M <1-31>D <xxxx>Y' where M is for month, D is for day, Y is for year. If unspecified the default will be the start of the current year.",
    is_eager=True,
)
endDateOption=typer.Option(
    "--endDate",
    help="A date string specifying the end date to be used for the default query. '<1-12>M <1-31>D <xxxx>Y' where M is for month, D is for day, Y is for year. If unspecified the default will be the end of the current year.",
    is_eager=True,
)
showConfigOption=typer.Option(
    "--showConfig",
    help="If true will print the config values to console.",
    is_eager=True,
)
