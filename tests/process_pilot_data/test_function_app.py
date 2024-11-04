import function_app
import io


def test_function_app(mocker):
    mock = mocker.patch("data_processor.process_data")
    input_stream = io.BytesIO(b'["0000000000,2000-01-01"]')

    func_call = function_app.process_data.build().get_user_function()
    func_call(input_stream)

    mock.assert_called_once()
    mock.assert_called_with(['["0000000000,2000-01-01"]'])
