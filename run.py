from app import create_app

app = create_app()

if __name__ == "__main__":
    # Use the self-signed certificate for HTTPS
    app.run(debug=True, host='0.0.0.0', port=5003, ssl_context=("cert.pem", "key.pem"))
