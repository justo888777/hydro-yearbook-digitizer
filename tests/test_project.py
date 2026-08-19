from hydro_yearbook_digitizer.project import initialize_project, validate_project


def test_initialize_and_validate_project(tmp_path) -> None:
    project_dir = initialize_project(tmp_path, "永定河流域", 1962)
    result = validate_project(project_dir)
    assert result.ok
    assert result.warnings == ("no source photos or PDFs found under raw/",)
