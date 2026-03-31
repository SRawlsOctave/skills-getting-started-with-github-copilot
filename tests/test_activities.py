from src.app import activities


EXPECTED_ACTIVITY_KEYS = {
    "description",
    "schedule",
    "max_participants",
    "participants",
}


def test_when_requesting_activities_then_returns_all_activities_with_required_keys(client):
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)

    for _, details in payload.items():
        assert set(details.keys()) == EXPECTED_ACTIVITY_KEYS


def test_when_signing_up_for_valid_activity_then_participant_is_added(client):
    # Arrange
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for {activity_name}",
    }
    assert email in activities[activity_name]["participants"]


def test_when_signing_up_for_unknown_activity_then_returns_not_found(client):
    # Arrange
    activity_name = "Unknown Activity"
    email = "new.student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_when_signing_up_existing_participant_then_returns_bad_request(client):
    # Arrange
    activity_name = "Chess Club"
    email = activities[activity_name]["participants"][0]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up"}


def test_when_signing_up_for_full_activity_then_returns_bad_request(client):
    # Arrange
    activity_name = "Chess Club"
    max_participants = activities[activity_name]["max_participants"]
    current_count = len(activities[activity_name]["participants"])
    for index in range(current_count, max_participants):
        activities[activity_name]["participants"].append(f"filled{index}@mergington.edu")
    email = "overflow.student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Activity is full"}
    assert email not in activities[activity_name]["participants"]


def test_when_removing_existing_participant_then_participant_is_removed(client):
    # Arrange
    activity_name = "Programming Class"
    email = activities[activity_name]["participants"][0]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Removed {email} from {activity_name}",
    }
    assert email not in activities[activity_name]["participants"]


def test_when_removing_participant_from_unknown_activity_then_returns_not_found(client):
    # Arrange
    activity_name = "Unknown Activity"
    email = "someone@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_when_removing_missing_participant_then_returns_not_found(client):
    # Arrange
    activity_name = "Soccer Club"
    email = "missing.student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Participant not found in this activity"}
