# 🎤 PPT Voice Presenter: Offline AI Narration Tool

## 🚀 Project Overview

The **PPT Voice Presenter** is an offline, script-to-audio generation tool designed to bypass the manual process of recording presentation narrations. It allows users, particularly **Consultants** and **Marketers**, to generate professional-sounding audio directly from an annotated text script, with built-in timing for slide transitions and speaking pauses.

The core requirement is **100% offline functionality** to ensure presentation data remains local and secure.

### Customer Value

| Component | Description |
| :--- | :--- |
| **Pain Reliever** | Eliminates the need for multiple tools and avoids the necessity of recording one's own voice. |
| **Gain Creator** | Provides free, easy-to-use **annotations for timing and pauses** (a feature often missing in basic tools). |
| **Products & Services** | A standalone Python application that converts an annotated text script into sequential, presentation-ready MP3 audio files. |

-----

## 🛠️ Current Status & Known Limitations

**WARNING: Audio Quality is Currently Poor\!**

This initial version uses the **`pyttsx3`** library and the underlying **eSpeak** system driver to satisfy the requirement for **offline, open-source functionality**.

  * **Result:** The current audio quality is basic, robotic, and lacks the necessary naturalness, emotion, and tone required for professional presentations.
  * **Action Required:** This tool is a **Proof of Concept (PoC)** demonstrating the parsing and sequencing logic. A major refactor is required to integrate a high-quality offline TTS engine (see **Next Steps**).

### Features Implemented

1.  **Offline Generation:** Uses system-level TTS drivers (`eSpeak` via `pyttsx3`).
2.  **Script Parsing:** Reads `presentation_script.txt` and splits it into slide segments using the `---SLIDE---` delimiter.
3.  **Basic Timing:** Converts custom pause annotations (`<pause:x>`) and header lines (`#`) into mandatory punctuation (`.`) to force an audible break.
4.  **Serial Output:** Reliably generates numbered MP3 files (`01_slide_audio.mp3`, `02_slide_audio.mp3`, etc.).

### Current Script Markup

| Feature | Markup Tag | How it's Handled |
| :--- | :--- | :--- |
| **Slide Section Break** | `---SLIDE---` | Generates a new, sequential MP3 file. |
| **Speaking Pause** | `<pause:x>` | Replaced with a period (`.`) to force a small pause. |
| **Tone/Emotion** | `<tone:emotion>...</tone:emotion>` | **Tags are removed**, and text is retained (currently ignored due to basic TTS engine). |

-----

## 🚀 Installation and Usage

This project requires **Python 3.x** and uses a virtual environment for dependency management.

### Setup Instructions

1.  **Clone the Repository (or navigate to the project directory):**

    ```bash
    cd powerpoint-voice-presenter
    ```

2.  **Create and Activate Virtual Environment:**

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # macOS/Linux
    .\.venv\Scripts\activate.bat # Windows
    ```

3.  **Install System Dependencies (eSpeak):**
    If you encounter errors related to the TTS engine, you must install the system driver. For Linux-based environments (like Codespaces):

    ```bash
    sudo apt-get update
    sudo apt-get install espeak-ng
    ```

4.  **Install Python Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

### Running the Tool

1.  **Edit the Script:** Open `presentation_script.txt` and write your presentation content using the defined markup.
2.  **Run the Generator:**
    ```bash
    python presenter_tool.py
    ```

The script will generate sequential MP3 files in the `./presentation_audio` directory, ready for insertion into PowerPoint or Canva. Debug information will be saved to `presenter_tool.log`.

-----

## 🗺️ Product Roadmap & Next Steps

The focus must immediately shift from *functionality* to **quality**.

### Immediate Refactor Goal (V2)

| Area | Change | Rationale |
| :--- | :--- | :--- |
| **TTS Engine** | Replace `pyttsx3` / `eSpeak` with a high-quality, open-source neural TTS engine like **Coqui TTS** or **Bark**. | This directly addresses the **Pains** and the **Critical Audio Quality issue**. |
| **Markup Handling**| Fully transition to an XML/SSML parser to properly handle the tone and emotion tags, which the advanced engines support. | Enables true **Gain Creation** (professional voice control). |
| **Logging** | Simplify the `presenter_tool.log` output once the critical errors are resolved. | Clean up the developer experience. |

### Long-Term Vision

  * **Product Vision:** To be the most reliable, secure, and highest-quality **offline** AI narration tool for presentation professionals, making studio-quality voice-overs accessible to anyone, anywhere.
  * **Metrics:** Successful audio generation rate (currently 100% success on the serial process) and **Time-to-Generate** (must be competitive with manual recording).
