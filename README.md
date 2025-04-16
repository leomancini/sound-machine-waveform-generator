# Sound Machine Waveform Generator

A Python-based tool for generating and visualizing audio waveforms, with LED matrix simulation capabilities.

## Features

- Audio waveform processing and visualization
- LED matrix simulation
- Real-time audio processing capabilities

## Prerequisites

- Python 3.x
- Virtual environment (recommended)

## Setup

1. Create and activate a virtual environment:

```bash
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

The project contains several main components:

- `process-audio.py`: Audio processing module
- `simulator.py`: LED matrix simulation
- `led_matrix_sim/`: LED matrix simulation package

To run the audio processor:

```bash
python process-audio.py
```

To run the simulator:

```bash
python simulator.py
```

## Project Structure

```
sound-machine-waveform-generator/
├── process-audio.py      # Audio processing module
├── simulator.py          # LED matrix simulation
├── led_matrix_sim/       # LED matrix simulation package
├── sample/               # Sample files
└── requirements.txt      # Project dependencies
```

## Dependencies

- pygame >= 2.5.2
- numpy >= 1.26.0
- scipy >= 1.12.0
