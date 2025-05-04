import gradio as gr
import os
from model import story_to_audio, extract_text_from_pdf

def text_to_speech(text):
    if not text.strip():
        return None
    audio_path = story_to_audio(text)
    return audio_path if audio_path and os.path.exists(audio_path) else None

def pdf_to_speech(pdf_file):
    if not pdf_file:
        return None
    text = extract_text_from_pdf(pdf_file.name)
    if not text.strip():
        return None
    audio_path = story_to_audio(text)
    return audio_path if audio_path and os.path.exists(audio_path) else None

with gr.Blocks(
    title="Text to Audio Converter",
    theme=gr.themes.Soft()
) as demo:
    gr.Markdown("## ✨ Text to Audio Converter")

    with gr.Row():
        # Left: Text to Speech
        with gr.Column():
            text_input = gr.Textbox(
                label="Enter your text",
                lines=10,
                placeholder="Type or paste your text here...",
                elem_id="textbox"
            )
            gr.Button("Generate Audio from Text", variant="primary").click(
                fn=text_to_speech,
                inputs=text_input,
                outputs=gr.Audio(label="Generated Audio from Text", type="filepath")
            )

        # Right: PDF to Speech
        with gr.Column():
            pdf_input = gr.File(label="Upload PDF", file_types=[".pdf"])
            gr.Button("Generate Audio from PDF", variant="primary").click(
                fn=pdf_to_speech,
                inputs=pdf_input,
                outputs=gr.Audio(label="Generated Audio from PDF", type="filepath")
            )

if __name__ == "__main__":
    demo.launch()
