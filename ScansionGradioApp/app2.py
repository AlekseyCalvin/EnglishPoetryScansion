import gradio as gr
import os
import sys

# Clone the repository
os.system("rm -rf EnglishPoetryScansion") # Clean up in case of a restart
os.system("git clone https://github.com/Koziev/EnglishPoetryScansion.git")

# Add the 'english_scansion' subdirectory to Python's path
sys.path.insert(0, './EnglishPoetryScansion/english_scansion')

# Now you can import the module
#from english_scansion import EnglishScansionTool

# Clone the English Poetry Scansion repository and add it to the path
#os.system("git clone https://github.com/Koziev/EnglishPoetryScansion.git")
#sys.path.insert(0, './EnglishPoetryScansion')

from english_scansion import EnglishScansionTool
from english_scansion.utils import format_scansion_as_html

# Initialize the scansion tool
scansion_tool = EnglishScansionTool()

def analyze_poem(poem_text, use_rhythm, use_stress, use_metrical_pattern, use_rhyme_scheme):
    """
    Analyzes a poem for meter, rhythm, stress, and rhyme.
    """
    try:
        # Perform the scansion analysis
        analysis_result = scansion_tool.analyze_poem(
            poem_text,
            predict_rhythm=use_rhythm,
            predict_stress=use_stress,
            predict_metrical_pattern=use_metrical_pattern,
            predict_rhyme_scheme=use_rhyme_scheme
        )

        # Format the results in a user-friendly way
        formatted_output = f"""
# Poetry Analysis Results

## Original Poem
{poem_text}

## Scansion Analysis
{analysis_result.get('scansion', 'N/A')}

## Metrical Pattern
{analysis_result.get('metrical_pattern', 'N/A')}

## Rhyme Scheme
{analysis_result.get('rhyme_scheme', 'N/A')}

## Stress Pattern
{analysis_result.get('stress_pattern', 'N/A')}
        """

        return formatted_output

    except Exception as e:
        return f"An error occurred during analysis: {str(e)}"

# Create the Gradio interface
with gr.Blocks(theme=gr.themes.Soft(), title="English Poetry Scansion Analyzer") as demo:
    gr.Markdown("""
    # English Poetry Scansion Analyzer
    Analyze the meter, rhythm, syllable stress-patterns, and scansion of English poetry.
    This tool is based on the [English Poetry Scansion](https://github.com/Koziev/EnglishPoetryScansion) toolkit.
    """)

    with gr.Row():
        with gr.Column():
            poem_input = gr.Textbox(
                lines=10,
                placeholder="Paste your English poem here...",
                label="Poem Text",
                info="Enter the poem you want to analyze."
            )

            with gr.Accordion("Analysis Options", open=False):
                use_rhythm = gr.Checkbox(value=True, label="Analyze Rhythm")
                use_stress = gr.Checkbox(value=True, label="Analyze Syllable Stress")
                use_metrical_pattern = gr.Checkbox(value=True, label="Identify Metrical Pattern")
                use_rhyme_scheme = gr.Checkbox(value=True, label="Detect Rhyme Scheme")

            analyze_btn = gr.Button("Analyze Poem", variant="primary")

        with gr.Column():
            output_text = gr.Markdown(label="Analysis Results")

    # Examples for users to try
    gr.Examples(
        examples=[
            ["Shall I compare thee to a summer's day?\nThou art more lovely and more temperate:\nRough winds do shake the darling buds of May,\nAnd summer's lease hath all too short a date:"],
            ["Two roads diverged in a yellow wood,\nAnd sorry I could not travel both\nAnd be one traveler, long I stood\nAnd looked down one as far as I could"],
            ["The curfew tolls the knell of parting day,\nThe lowing herd wind slowly o'er the lea,\nThe plowman homeward plods his weary way,\nAnd leaves the world to darkness and to me."]
        ],
        inputs=poem_input
    )

    # Connect the button to the function
    analyze_btn.click(
        fn=analyze_poem,
        inputs=[poem_input, use_rhythm, use_stress, use_metrical_pattern, use_rhyme_scheme],
        outputs=output_text
    )

# Launch the app
if __name__ == "__main__":
    demo.launch(share=False, server_name="0.0.0.0", server_port=7860)