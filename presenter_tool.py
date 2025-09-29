import pyttsx3
import re
import os
import logging
from pathlib import Path

# --- Configuration ---
SCRIPT_FILE = 'presentation_script.txt'
OUTPUT_DIR = 'presentation_audio'
LOG_FILE = 'presenter_tool.log'
SLIDE_DELIMITER = '---SLIDE---'
# --- End Configuration ---

# Set up the logger
logger = logging.getLogger(__name__)

# Regular expression to find <pause:x> and <tone:x> tags.
# This pattern captures the tag name (e.g., 'pause', 'tone') and its value (e.g., '1000', 'excited').
MARKUP_REGEX = re.compile(r'<(\w+):(\w+)>')

def setup_logging():
    """Configures the logger to output to both console and a log file."""
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    
    # 1. Clear any existing handlers (important for re-running)
    if logger.hasHandlers():
        logger.handlers.clear()

    # 2. Set the global logging level
    logger.setLevel(logging.INFO)

    # 3. File Handler: Writes logs to a file
    file_handler = logging.FileHandler(LOG_FILE, mode='w') # mode='w' clears file on each run
    file_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(file_handler)

    # 4. Console Handler: Prints logs to the terminal
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(console_handler)
    
    logger.info(f"Logging configured. Logs also being written to: {LOG_FILE}")

def initialize_tts_engine():
    """Initializes and configures the offline pyttsx3 engine."""
    logger.info("--- TTS Initialization ---")

    engine = None

    try:
        # Try initializing with the specific 'espeak' driver
        logger.info("Attempting to initialize pyttsx3 with 'espeak' driver...")
        engine = pyttsx3.init('espeak')
        logger.info("pyttsx3 initialized successfully.")
    except Exception as e:
        logger.critical(f"FATAL ERROR: Failed to call pyttsx3.init('espeak'). Details: {e}")
        return None

    # Check for the driver name attribute ONLY if the engine object was created.
    try:
        engine.setProperty('rate', 150)

        # Guard the problematic getDriverName() call
        driver = 'espeak (Assumed)'
        
        try:
            driver = engine.getDriverName()
        except AttributeError:
            logger.warning("Could not call getDriverName(). Engine object appears incomplete, but proceeding.")
        
        voices = engine.getProperty('voices')
        logger.info(f"Driver confirmed: {driver}")
        logger.info(f"Voice count: {len(voices)}")
        
        if voices:
            # Set the first available voice
            engine.setProperty('voice', voices[0].id)
            current_voice = engine.getProperty('voice')
            logger.info(f"Set Voice ID: {current_voice}")
        else:
             logger.warning("No voices found by pyttsx3. Audio generation may fail.")
        
        logger.info("--- Initialization Complete ---")
        return engine

    except Exception as e:
        # If any property setting or driver logging fails after init, log it.
        logger.critical(f"FATAL ERROR: Engine setup failed post-initialization. Details: {e}")
        return None

def parse_script(script_path):
    """Reads the script file and splits it into a list of slide contents."""
    logger.info(f"\n--- Parsing Script: {script_path} ---")
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
            logger.info(f"Script loaded. Total characters: {len(script_content)}")
    except FileNotFoundError:
        logger.error(f"Error: Script file not found at {script_path}")
        return []

    slides = script_content.split(SLIDE_DELIMITER)
    cleaned_slides = [slide.strip() for slide in slides if slide.strip()]
    
    logger.info(f"Found {len(cleaned_slides)} valid slide segments.")
    return cleaned_slides

def process_slide_text(text):
    """
    Processes the slide text, converting custom markup tags into 
    SSML-like formatting for the TTS engine.
    
    NOTE ON TONE/EMOTION: pyttsx3/eSpeak has very minimal support for
    emotional tone. The `<tone:x>` tag is included here for future 
    upgrades to more advanced TTS engines (like Coqui TTS or a commercial 
    local engine) but will be ignored for basic pyttsx3/eSpeak. 
    The `<pause:x>` tag is handled using an SSML-compliant break.
    """
    processed_text = text
    
    # 1. FIX: Remove headers and replace with a period and space for a strong pause.
    # The regex removes the header line (e.g., # Section 1) and replaces it with ". "
    processed_text = re.sub(r'#.*?\n', '. ', processed_text, flags=re.DOTALL)

    def replace_markup(match):
        tag_type = match.group(1).lower()
        tag_value = match.group(2)
        
        if tag_type == 'pause':
            # FIX: Replace the SSML tag with a simple period, which forces a pause.
            # The value (e.g., 500ms) is now ignored, but a pause is created.
            return ". "
        elif tag_type == 'tone':
            # For pyttsx3/eSpeak, we'll just remove the tone tags but keep the text inside.
            # E.g., <tone:excited>text</tone:excited> becomes "text"
            # More advanced engines would use this value.
            return ''
        return match.group(0) # Return the original text if it's an unrecognized tag

    # Find and process all markup tags
    # The current regex and logic is simplified for basic pyttsx3/eSpeak.
    # For robust handling of tags *containing text* (like <tone>...</tone>), 
    # we would use a more advanced XML parser. For now, we'll use a simple
    # placeholder to remove the tone tags but retain the text.
    
    # Simple cleanup of tags that wrap content (like <tone:excited>text</tone:excited>)
    processed_text = re.sub(r'<tone:\w+>(.*?)</tone:\w+>', r'\1', processed_text, flags=re.DOTALL | re.IGNORECASE)
    
    # Now process the simpler inline tags like <pause:x>
    processed_text = MARKUP_REGEX.sub(replace_markup, processed_text)

    # Clean up any remaining newlines or extra spaces
    final_text = ' '.join(processed_text.split())

    return final_text

def generate_slide_audio(text, slide_number,engine):
    """
    Generates and saves the audio file for a single slide.
    """
    logger.info(f"\n--- Starting Generation for Slide {slide_number} ---")

    # 1. Path and Directory Check
    filename = f"{str(slide_number).zfill(2)}_slide_audio.mp3"
    output_path = Path(os.getcwd()) / OUTPUT_DIR / filename
    
    # Create the output directory if it doesn't exist
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory confirmed: {output_path.parent}")
    except OSError as e:
        logger.error(f"Cannot create output directory or check path. Permission issue? Details: {e}")
        return False

    logger.info(f"Target file path: {output_path}")
        
    # 2. Text Processing and SSML Preparation
    processed_text = process_slide_text(text)
    final_text = processed_text
    # **NEW LOGGING LINE FOR DEBUGGING**
    logger.info(f"FULL TEXT SENT TO ENGINE: {final_text}") 
    
    # 3. Audio Generation Queue
    try:
        # **NEW: Flush any pending events before queuing the new job**
        # This helps clear any residual state that might be causing the first slide failure.
        engine.stop()
        logger.info("Engine stopped/flushed before queuing.")
        
        engine.save_to_file(final_text, str(output_path))
        logger.info(f"SUCCESS: Audio generation job queued for Slide {slide_number}.")
        return True
    except Exception as e:
        logger.error(f"Failed to queue audio generation. Details: {e}")
        return False

def main():
    """Main execution function: parses the script and generates all audio files."""
    
    # 1. Setup logging before anything else
    setup_logging()
    
    # 2. Initialize TTS Engine
    engine = initialize_tts_engine()
    if engine is None:
        logger.critical("Cannot proceed without a working TTS engine.")
        return

    # 3. Parse the script file
    slides = parse_script(SCRIPT_FILE)
    if not slides:
        logger.warning("Script processing finished with no slides to generate. Check your script file.")
        return

    logger.info(f"\nStarting generation process for {len(slides)} slides...")
    
    # 4. Loop through each slide, queue the audio, AND WAIT immediately after.
    for i, slide_text in enumerate(slides, 1):
        # We call the generation function
        success = generate_slide_audio(slide_text, i, engine)
        
        if success:
            # 5. IMMEDIATELY WAIT for the current slide to finish generating
            logger.info(f"--- Waiting for Slide {i} to finish (runAndWait) ---")
            try:
                engine.runAndWait()
                logger.info(f"Slide {i} generation complete.")
            except Exception as e:
                logger.error(f"ERROR during runAndWait() for Slide {i}. Details: {e}")
                # Log the failure but continue to the next slide job queue if possible
                continue
        else:
            logger.error(f"Failed to queue audio for Slide {i}. Skipping runAndWait.")
    
    # 6. Final verification check
    output_files = list(Path(OUTPUT_DIR).glob('*.mp3'))

    if len(output_files) == len(slides):
        logger.info(f"\n✅ All {len(slides)} presenter audio files successfully created in '{OUTPUT_DIR}/'.")
    elif output_files:
        logger.warning(f"\n⚠️ WARNING: Found {len(output_files)} files, but expected {len(slides)}. Check the logs.")
    else:
        logger.critical("\n❌ CRITICAL FAILURE: No audio files were generated. Review the logs for errors.")
    
if __name__ == "__main__":
    main()