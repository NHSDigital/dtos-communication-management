import azure.functions as func
import function_app


def test_function_app(mocker):
    mock = mocker.patch("data_processor.process_data")
    input_stream = func.blob.InputStream(
        data=b'["0000000000,2000-01-01"]',
        name="pilot-data/JDO NHS App Pilot 002 SPRPT.csv",
    )

    func_call = function_app.process_data.build().get_user_function()
    func_call(input_stream)

    mock.assert_called_once()
    mock.assert_called_with('JDO NHS App Pilot 002 SPRPT', ['["0000000000,2000-01-01"]'])
