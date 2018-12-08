def _test_filtered_hal(d):
    for k, v in d.items():
        assert isinstance(k, (int, str))

        if isinstance(v, dict):
            _test_filtered_hal(v)
        elif isinstance(v, list):
            for vv in v:
                if isinstance(vv, dict):
                    _test_filtered_hal(vv)
                else:
                    assert isinstance(vv, (type(None), float, int, str, bool))
        else:
            assert isinstance(v, (type(None), float, int, str, bool))


def test_filtered_hal(wpilib, hal_data):
    _test_filtered_hal(hal_data)


def test_hal_update(wpilib, hal_data):
    from hal_impl.data import update_hal_data

    in_dict = {"compressor": {"on": True}}

    assert hal_data["compressor"]["on"] == False

    update_hal_data(in_dict, hal_data)

    assert hal_data["compressor"]["on"] == True
