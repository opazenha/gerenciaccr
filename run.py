import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from gerencia_ccr.web.app import app

if __name__ == "__main__":
    app.run(debug=True, port=7770, host='0.0.0.0')