import pygame
import json
import sys
import os
import time

# Display settings
width, height = 64, 32  # Same dimensions as your LED matrix
scale = 15  # Scale up for better visibility on screen
fps = 30  # Match the FPS used in audio processing

class WaveformVisualizer:
    def __init__(self, waveform_path, audio_path):
        # Initialize pygame and mixer
        pygame.init()
        pygame.mixer.init(frequency=44100)
        
        # Set up display
        self.screen = pygame.display.set_mode((width * scale, height * scale))
        pygame.display.set_caption("Audio Spectrum Visualizer")
        
        # Load frequency data
        with open(waveform_path, 'r') as f:
            self.frequency_data = json.load(f)
            
        # Print information about the frequency data
        if len(self.frequency_data) > 0:
            num_bands = len(self.frequency_data[0])
            print(f"Number of frequency bands: {num_bands}")
            # Print average amplitude for each band across first 100 frames
            if len(self.frequency_data) >= 100:
                band_averages = [0] * num_bands
                for frame in self.frequency_data[:100]:
                    for i, amp in enumerate(frame):
                        band_averages[i] += amp
                band_averages = [avg/100 for avg in band_averages]
                print("Average amplitude per band (first 100 frames):")
                for i, avg in enumerate(band_averages):
                    print(f"Band {i}: {avg:.3f}")
        
        # Color settings
        self.red = 255
        self.green = 0
        self.blue = 0
        
        # Animation settings
        self.clock = pygame.time.Clock()
        self.frame = 0  # Current frame in animation
        
        # Load audio
        self.audio_path = audio_path
        pygame.mixer.music.load(audio_path)
    
    def draw_frame(self, bands):
        """Draw a single frame of the visualization."""
        # Clear screen
        self.screen.fill((0, 0, 0))
        
        # Calculate width of each band to fill screen
        band_width = width / len(bands)
        
        # Add offset to shift visualization to the right
        x_offset = 0  # No offset, centered visualization
        
        # Draw frequency bands
        for i, amplitude in enumerate(bands):
            # Normalize amplitude to 0-1 range (assuming max amplitude of 15.0)
            normalized_amplitude = amplitude / 15.0
            # Then scale to appropriate display height (using most of our 32px height)
            amplitude = normalized_amplitude * 14  # This will give us max height of 14px from center
            
            # Calculate x position and width for this band, adding the offset
            x = (i * band_width) + x_offset
            
            # Calculate wave points
            mid_point = height // 2
            
            # Mirror the wave to get the classic soundwave effect
            start_y = int(mid_point - amplitude)
            end_y = int(mid_point + amplitude)
            
            # Keep within bounds with minimal margins
            start_y = max(0, start_y)
            end_y = min(height - 1, end_y)
            
            # Draw filled rectangle for this frequency band
            rect_height = end_y - start_y + 1
            rect_width = max(1, int(band_width * scale))  # Ensure minimum width of 1 pixel
            pygame.draw.rect(self.screen, (self.red, self.green, self.blue),
                           (int(x * scale), start_y * scale, rect_width, rect_height * scale))
        
        # Update the display
        pygame.display.flip()
    
    def run(self):
        """Run the visualization."""
        running = True
        paused = False
        
        # Start playing audio
        pygame.mixer.music.play()
        start_time = time.time()
        
        while running and self.frame < len(self.frequency_data):
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Toggle pause
                        paused = not paused
                        if paused:
                            pygame.mixer.music.pause()
                        else:
                            pygame.mixer.music.unpause()
            
            if not paused:
                # Get current frame of frequency data
                bands = self.frequency_data[self.frame]
                self.draw_frame(bands)
                self.frame += 1
            
            # Maintain frame rate
            self.clock.tick(fps)
        
        # Cleanup
        pygame.mixer.music.stop()
        pygame.quit()

def main():
    # Hardcode the paths to use sample/waveform.json and sample/audio.mp3
    waveform_path = "sample/waveform.json"
    audio_path = "sample/audio.mp3"
    
    if not os.path.exists(waveform_path):
        print(f"Error: Waveform file '{waveform_path}' not found")
        sys.exit(1)
    
    if not os.path.exists(audio_path):
        print(f"Error: Audio file '{audio_path}' not found")
        sys.exit(1)
    
    # Create and run visualizer
    visualizer = WaveformVisualizer(waveform_path, audio_path)
    visualizer.run()

if __name__ == "__main__":
    main()