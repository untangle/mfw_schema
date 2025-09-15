from pydantic_models.mfw_schema import MfwSchema

# Sample data that conforms to the schema
sample_data = {
    "version": 1,
    "network": {
        "interfaces": [
            {
                "interfaceId": 1,
                "name": "eth0",
                "device": "eth0",
                "wan": True,
                "type": "NIC",
                "configType": "ADDRESSED",
                "v4ConfigType": "STATIC",
                "v4StaticAddress": "192.168.1.1",
                "v4StaticPrefix": 24,
            }
        ]
    },
    "system": {"hostName": "test-host", "domainName": "example.com"},
}


def test_v1_config() -> None:
    """
    Tests the MfwSchema model with sample data.
    """
    try:
        # Create an instance of the MfwSchema model
        config = MfwSchema(**sample_data)

        # Print the model instance to verify its contents
        print("Successfully created MfwSchema instance:")
        print(config.model_dump_json(indent=4))

    except Exception as e:
        print(f"Error creating MfwSchema instance: {e}")


if __name__ == "__main__":
    test_v1_config()
