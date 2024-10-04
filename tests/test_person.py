def test_get_people_without_auth(test_client):
    response = test_client.get("/api/people")
    assert response.status_code == 401  # Unauthorized


def test_create_person_without_auth(test_client):
    response = test_client.post("/api/people", json={"name": "Test Person"})
    assert response.status_code == 401  # Unauthorized


def test_get_people_with_auth(test_client, get_jwt_token):
    token = get_jwt_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = test_client.get("/api/people", headers=headers)
    assert response.status_code == 200
    assert response.get_json() == []  # No people in the DB yet


def test_create_person_with_auth(test_client, get_jwt_token):
    token = get_jwt_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = test_client.post(
        "/api/people",
        json={"name": "Test Person", "sale_oportunity": True},
        headers=headers,
    )
    assert response.status_code == 201
    assert response.get_json()["name"] == "Test Person"


def test_patch_person(test_client, get_jwt_token):
    token = get_jwt_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = test_client.patch(
        "/api/person/1",
        json={"name": "Edited Test Person", "sale_oportunity": True},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.get_json()["name"] == "Edited Test Person"


def test_create_person_with_auth_without_sale_oportunity(test_client, get_jwt_token):
    token = get_jwt_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = test_client.post(
        "/api/people",
        json={"name": "Test Person 2", "sale_oportunity": False},
        headers=headers,
    )
    assert response.status_code == 201
    assert response.get_json()["name"] == "Test Person 2"
    assert response.get_json()["sale_oportunity"] is False


def test_create_person_limit_vehicles(test_client, get_jwt_token):
    token = get_jwt_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Create a person
    person_resp = test_client.post(
        "/api/people", json={"name": "Bob", "sale_oportunity": True}, headers=headers
    )
    person_id = person_resp.get_json()["id"]

    # Add three vehicles (valid)
    vehicle_data = [
        {"name": "Golf", "color": "yellow", "model": "hatch"},
        {"name": "BMW M4", "color": "blue", "model": "sedan"},
        {"name": "Test", "color": "gray", "model": "convertible"},
    ]
    for vehicle in vehicle_data:
        response = test_client.post(
            f"/api/vehicles/person/{person_id}", json=vehicle, headers=headers
        )
        assert response.status_code == 201

    # Attempt to add a fourth vehicle (should fail)
    response = test_client.post(
        f"/api/vehicles/person/{person_id}",
        json={"name": "Test 2", "color": "gray", "model": "convertible"},
        headers=headers,
    )
    assert response.status_code == 400  # Max 3 vehicles limit
    assert response.get_json()["message"] == "A person can only have up to 3 vehicles."


def test_create_person_invalid_color_vehicles(test_client, get_jwt_token):
    token = get_jwt_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Create a person
    person_resp = test_client.post(
        "/api/people", json={"name": "Bob", "sale_oportunity": True}, headers=headers
    )
    person_id = person_resp.get_json()["id"]

    # Add a vehicle (valid)
    vehicle_data = [
        {"name": "Golf", "color": "yellow", "model": "hatch"},
        {"name": "BMW M4", "color": "blue", "model": "sedan"},
    ]
    for vehicle in vehicle_data:
        response = test_client.post(
            f"/api/vehicles/person/{person_id}", json=vehicle, headers=headers
        )
        assert response.status_code == 201

    # Attempt to add a vehicle with invalid color (should fail)
    response = test_client.post(
        f"/api/vehicles/person/{person_id}",
        json={"name": "Test 2", "color": "invalid", "model": "convertible"},
        headers=headers,
    )
    assert response.status_code == 400
    assert response.get_json()["message"] == "Color not available."


def test_create_person_invalid_model_vehicles(test_client, get_jwt_token):
    token = get_jwt_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Create a person
    person_resp = test_client.post(
        "/api/people", json={"name": "Bob", "sale_oportunity": True}, headers=headers
    )
    person_id = person_resp.get_json()["id"]

    # Add a vehicle (valid)
    vehicle_data = [
        {"name": "Golf", "color": "yellow", "model": "hatch"},
        {"name": "BMW M4", "color": "blue", "model": "sedan"},
    ]
    for vehicle in vehicle_data:
        response = test_client.post(
            f"/api/vehicles/person/{person_id}", json=vehicle, headers=headers
        )
        assert response.status_code == 201

    # Attempt to add a vehicle with invalid model (should fail)
    response = test_client.post(
        f"/api/vehicles/person/{person_id}",
        json={"name": "Test 2", "color": "yellow", "model": "invalid"},
        headers=headers,
    )
    assert response.status_code == 400
    assert response.get_json()["message"] == "Model not available."


def test_create_person_and_add_vehicle_without_sale_oportunity(
    test_client, get_jwt_token
):
    token = get_jwt_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Create a person
    person_resp = test_client.post(
        "/api/people", json={"name": "Bob", "sale_oportunity": False}, headers=headers
    )
    person_id = person_resp.get_json()["id"]

    # Add a vehicle (valid)
    vehicle_data = {"name": "Golf", "color": "yellow", "model": "hatch"}

    response = test_client.post(
        f"/api/vehicles/person/{person_id}", json=vehicle_data, headers=headers
    )
    assert response.status_code == 403  # Sale oportunity is False
    assert response.get_json()["message"] == "Person cannot buy vehicles yet."


def test_delete_vehicle(test_client, get_jwt_token):
    token = get_jwt_token()
    headers = {"Authorization": f"Bearer {token}"}
    vehicles_ids = []

    # Create a person
    person_resp = test_client.post(
        "/api/people", json={"name": "Bob", "sale_oportunity": True}, headers=headers
    )
    person_id = person_resp.get_json()["id"]

    # Add vehicles (valid)
    vehicle_data = [
        {"name": "Golf", "color": "yellow", "model": "hatch"},
        {"name": "BMW M4", "color": "blue", "model": "sedan"},
    ]
    for vehicle in vehicle_data:
        response = test_client.post(
            f"/api/vehicles/person/{person_id}", json=vehicle, headers=headers
        )
        assert response.status_code == 201
        vehicles_ids.append(response.get_json().get("id"))

    # Remove a vehicle
    response = test_client.delete(
        f"/api/vehicle/{vehicles_ids[0]}/person/{person_id}",
        headers=headers,
    )
    assert response.status_code == 204


def test_delete_vehicle_not_from_person(test_client, get_jwt_token):
    token = get_jwt_token()
    headers = {"Authorization": f"Bearer {token}"}
    vehicles_ids = []

    # Create a person
    person_resp = test_client.post(
        "/api/people", json={"name": "Bob", "sale_oportunity": True}, headers=headers
    )
    person_id = person_resp.get_json()["id"]

    # Create anothe person
    another_person_resp = test_client.post(
        "/api/people",
        json={"name": "Another Person", "sale_oportunity": True},
        headers=headers,
    )
    another_person_id = another_person_resp.get_json()["id"]

    # Add a vehicle (valid)
    vehicle_data = [
        {"name": "Golf", "color": "yellow", "model": "hatch"},
        {"name": "BMW M4", "color": "blue", "model": "sedan"},
    ]
    for vehicle in vehicle_data:
        response = test_client.post(
            f"/api/vehicles/person/{person_id}", json=vehicle, headers=headers
        )
        assert response.status_code == 201
        vehicles_ids.append(response.get_json().get("id"))

    # Remove a vehicle
    response = test_client.delete(
        f"/api/vehicle/{vehicles_ids[0]}/person/{person_id}",
        headers=headers,
    )
    assert response.status_code == 204

    # Try to remove an inexistent vehicle
    response = test_client.delete(
        f"/api/vehicle/9999/person/{person_id}",
        headers=headers,
    )
    assert response.status_code == 404

    # Try to remove a vehicle from another person
    response = test_client.delete(
        f"/api/vehicle/{vehicles_ids[1]}/person/{another_person_id}",
        headers=headers,
    )
    assert response.status_code == 403
