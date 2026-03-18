from ampf.testing import ApiTestClient

from core.user_settings.user_settings_model import UserSettings


def test_get_patch_get(client: ApiTestClient, headers: dict[str, str]):
    # GET:
    us = client.get_typed("/api/user-settings", 200, UserSettings, headers=headers)
    assert us.native_language == "en"
    # PATCH
    us.native_language = "pl"
    client.patch("/api/user-settings", 200, json=us, headers=headers)
    # GET
    us = client.get_typed("/api/user-settings", 200, UserSettings, headers=headers)
    assert us.native_language == "pl"
