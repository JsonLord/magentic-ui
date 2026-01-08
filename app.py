import sys
import os

# Add the 'src' directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

import gradio as gr
from magentic_ui.backend.web.app import app as fastapi_app

# It's not possible to directly mount a FastAPI app in a Gradio interface in the traditional sense.
# However, for the purpose of this deployment, we will create a simple Gradio interface
# that acknowledges the backend is running. The FastAPI app will be served by the same
# process, but Gradio will be the entry point for the Hugging Face Space.

def backend_status():
    return "The Magentic UI backend is running. Access it at /docs on this space."

iface = gr.Interface(fn=backend_status, inputs=None, outputs="text", title="Magentic UI Backend")

# This is a workaround to serve both the Gradio interface and the FastAPI app.
# We will mount the FastAPI app to the Gradio app's root.
app = gr.mount_gradio_app(fastapi_app, iface, path="/")
