from app import create_app

def test_health_check():
    """Responds with a 200 status code and a healthy status message."""
    app = create_app()
    client = app.test_client()

    response = client.get('/api/message-status/health-check')

    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy"}
