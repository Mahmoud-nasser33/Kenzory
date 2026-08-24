import os

from dotenv import load_dotenv

load_dotenv()

from kenzory import create_app  # noqa: E402

app = create_app()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8081"))
    debug = app.config.get("DEBUG", False)
    app.run(host="127.0.0.1", port=port, debug=debug)
