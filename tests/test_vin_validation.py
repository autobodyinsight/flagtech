from app.services.vin import body_style_from_vpic, decode_vin, validate_vin


def test_vin_rejects_bad_length_and_characters():
    short = validate_vin("123")
    assert short["valid_format"] is False
    illegal = validate_vin("I" * 17)
    assert illegal["valid_format"] is False


def test_vin_check_digit_warning_still_allows_decode():
    bad = "11111111111111112"
    result = validate_vin(bad)
    assert result["valid_format"] is True
    assert result["check_digit_ok"] is False
    assert result["warnings"]

    def fake_fetch(_url):
        return {
            "Results": [
                {
                    "Make": "FORD",
                    "Model": "Maverick",
                    "ModelYear": "2024",
                    "Trim": "Lariat",
                    "BodyClass": "Pickup",
                    "Doors": "4",
                    "DriveType": "4WD",
                    "DisplacementL": "2.0",
                    "EngineCylinders": "4",
                    "ErrorCode": "0",
                }
            ]
        }

    decoded = decode_vin(bad, fetcher=fake_fetch)
    assert decoded["decoded"] is True
    assert decoded["vehicle"]["make"] == "Ford"
    assert decoded["vehicle"]["body_style"] == "pickup"
    assert decoded["validation"]["warnings"]


def test_decoder_error_is_graceful():
    def broken(_url):
        raise TimeoutError("down")

    decoded = decode_vin("1HGCM82633A004352", fetcher=broken)
    assert decoded["decoded"] is False
    assert "manually" in decoded["error"]


def test_body_style_mapping():
    assert body_style_from_vpic("Sport Utility Vehicle", 4) == "suv"
    assert body_style_from_vpic("Sedan", 2) == "coupe"
    assert body_style_from_vpic("Cargo Van", 4) == "van"
