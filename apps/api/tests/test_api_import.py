def test_import_skills_csv_valid_and_invalid(client, auth_headers):
    # Valid CSV
    valid_csv = "name,category,description\nGraphQL,Backend,API query language\nVue.js,Frontend,Progressive JS framework\n"
    res = client.post(
        "/api/v1/imports/csv?entity_type=skills",
        files={"file": ("skills.csv", valid_csv, "text/csv")},
        headers=auth_headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_rows"] == 2
    assert data["imported_rows"] == 2
    assert data["failed_rows"] == 0

    # Invalid CSV (missing name on row 2, missing category on row 3)
    invalid_csv = "name,category,description\n,Backend,No name\nSvelte,,No category\n"
    res_inv = client.post(
        "/api/v1/imports/csv?entity_type=skills",
        files={"file": ("skills.csv", invalid_csv, "text/csv")},
        headers=auth_headers,
    )
    assert res_inv.status_code == 200
    inv_data = res_inv.json()
    assert inv_data["failed_rows"] == 2
    assert len(inv_data["errors"]) == 2
    assert inv_data["errors"][0]["field"] == "name"
    assert inv_data["errors"][1]["field"] == "category"


def test_import_employees_csv_row_level_validation(client, auth_headers):
    # CSV with 1 valid row, 1 bad email row, 1 negative cost row
    mixed_csv = (
        "name,email,role,cost_per_hour,start_date\n"
        "Valid Dev,valid.dev@example.com,Backend Dev,80.0,2026-01-01\n"
        "Bad Email Dev,notanemail,Backend Dev,75.0,2026-01-01\n"
        "Bad Cost Dev,badcost@example.com,Backend Dev,-50.0,2026-01-01\n"
    )
    res = client.post(
        "/api/v1/imports/csv?entity_type=employees",
        files={"file": ("employees.csv", mixed_csv, "text/csv")},
        headers=auth_headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_rows"] == 3
    assert data["imported_rows"] == 1
    assert data["failed_rows"] == 2
    err_fields = [e["field"] for e in data["errors"]]
    assert "email" in err_fields
    assert "cost_per_hour" in err_fields
