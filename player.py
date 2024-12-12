import json
import numpy as np
import sounddevice as sd
#from serial import Serial
import time as code_time
from datetime import datetime, timedelta
import threading
import pygame
import sys

# Pygame constants
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
FIELD_SCALE = 4
FIELD_WIDTH = WINDOW_WIDTH // FIELD_SCALE
FIELD_HEIGHT = WINDOW_HEIGHT // FIELD_SCALE
THRESHOLD = 1.5
NUM_METABALLS = 150
RADIUS = 6
ATTRACTION_FORCE = 1
FRICTION = 0.98
MAX_SPEED = 5.0

# Global variables for energy levels
low_energy = None
mid_energy = None
high_energy = None
stft_times = None
last_serial_write_time = 0
startTime = None
attraction = False  # Initialize attraction state globally
screen = None
clock = None
meu_serial = None
srtTime = None
delta = None

# Pygame setup
def setup():
    global meu_serial
    #meu_serial = Serial(port='COM6', baudrate=9600)
    pygame.init()
    global screen
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Visualizacao")
    global clock
    clock = pygame.time.Clock()

metaballs = np.zeros((NUM_METABALLS, 4), dtype=float)
for i in range(NUM_METABALLS):
    metaballs[i, 0] = np.random.randint(1, FIELD_WIDTH - 2)
    metaballs[i, 1] = np.random.randint(1, FIELD_HEIGHT - 2)
    metaballs[i, 2] = 0.0
    metaballs[i, 3] = 0.0

x_vals = np.arange(FIELD_WIDTH)
y_vals = np.arange(FIELD_HEIGHT)
xx, yy = np.meshgrid(x_vals, y_vals)
field_surface = pygame.Surface((FIELD_WIDTH, FIELD_HEIGHT))
field_array = pygame.surfarray.pixels3d(field_surface)
field_array = np.transpose(field_array, (1, 0, 2))

def update_metaballs(attraction):
    global metaballs
    cx = FIELD_WIDTH / 2
    cy = FIELD_HEIGHT / 2
    if attraction:
        dx = cx - metaballs[:, 0]
        dy = cy - metaballs[:, 1]
        dist = np.sqrt(dx*dx + dy*dy) + 1e-9
        metaballs[:, 2] += (dx / dist) * ATTRACTION_FORCE
        metaballs[:, 3] += (dy / dist) * ATTRACTION_FORCE
    else:
        metaballs[:, 2] *= FRICTION
        metaballs[:, 3] *= FRICTION

    speeds_sq = metaballs[:, 2] ** 2 + metaballs[:, 3] ** 2
    too_fast = speeds_sq > (MAX_SPEED ** 2)
    if np.any(too_fast):
        speeds = np.sqrt(speeds_sq[too_fast])
        scale = MAX_SPEED / speeds
        metaballs[too_fast, 2] *= scale
        metaballs[too_fast, 3] *= scale

    metaballs[:, 0] += metaballs[:, 2]
    metaballs[:, 1] += metaballs[:, 3]
    metaballs[metaballs[:, 0] < 0, 2] = -metaballs[metaballs[:, 0] < 0, 2]
    metaballs[metaballs[:, 0] >= FIELD_WIDTH, 2] = -metaballs[metaballs[:, 0] >= FIELD_WIDTH, 2]
    metaballs[metaballs[:, 1] < 0, 3] = -metaballs[metaballs[:, 1] < 0, 3]
    metaballs[metaballs[:, 1] >= FIELD_HEIGHT, 3] = -metaballs[metaballs[:, 1] >= FIELD_HEIGHT, 3]

def compute_field():
    global field_array
    field_values = np.zeros((FIELD_HEIGHT, FIELD_WIDTH), dtype=float)
    for i in range(NUM_METABALLS):
        bx, by = metaballs[i, 0], metaballs[i, 1]
        dx = xx - bx
        dy = yy - by
        dist_sq = dx*dx + dy*dy
        dist_sq[dist_sq == 0] = 1e-9
        field_values += RADIUS / dist_sq
    mask = field_values > THRESHOLD
    field_array[:] = (255, 255, 255)
    field_array[mask, :] = (0, 0, 0)

def balls_simulation():
    global attraction, screen, clock  # Use the global attraction variable

    # Start Pygame's event loop in the main thread
    while True:
        clock.tick(60)  # Control the frame rate
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    attraction = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    attraction = False

        update_metaballs(attraction)
        compute_field()

        scaled_surface = pygame.transform.scale(field_surface, (WINDOW_WIDTH, WINDOW_HEIGHT))
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()

def callback(data, frames, time, status):

    global low_energy, mid_energy, high_energy, stft_times, startTime, attraction, ATTRACTION_FORCE, meu_serial, srtTime, delta

    current_time = (datetime.now() - delta).total_seconds()
    #print(current_time)
    idx = np.argmin(np.abs(stft_times - current_time))


    low_intensity = low_energy[idx]
    mid_intensity = mid_energy[idx]
    high_intensity = high_energy[idx]

    beat_threshold = 3.5 

    if low_intensity > beat_threshold:
        attraction = True
        ATTRACTION_FORCE = low_intensity * 0.04
    if high_intensity > beat_threshold:
        attraction = True
        ATTRACTION_FORCE = low_intensity * -0.05
    if high_intensity < beat_threshold and low_intensity < beat_threshold:
        attraction = True
        ATTRACTION_FORCE = 3

    visualization = (
        f"L: {'#' * 1 * int(low_intensity)}".ljust(50) +  
        f"M: {'*' * 1 * int(mid_intensity)}".ljust(50) +  
        f"H: {'-' * 1 * int(high_intensity)}".ljust(50)  
    )

    serial_string = "bass off\noff\n"
    if int(low_intensity) > 1:
        serial_string = serial_string.replace('bass off', f"bass {int(low_intensity*10)}")
    if int(high_intensity) > 1:
        serial_string = serial_string.replace('\noff', '\non')

    global last_serial_write_time
    if code_time.time() - last_serial_write_time >= 0.2:
        current_time += 0.2
        #print(serial_string)
        #meu_serial.write(serial_string.encode("UTF-8"))
        last_serial_write_time = code_time.time()  

    #print(visualization)

def player(tempoAtual):
    setup()
    global low_energy, mid_energy, high_energy, stft_times, srtTime
    srtTime = tempoAtual
    #print(srtTime)

    with open('data/processed/vibration_pattern.json', 'r') as fp:
        vibration_data = json.load(fp)

    low_energy = np.array(vibration_data['low'])
    mid_energy = np.array(vibration_data['mid'])
    high_energy = np.array(vibration_data['high'])
    stft_times = np.array(vibration_data['stft_times'])
    y = np.array(vibration_data['y'])
    sr = np.array(vibration_data['sr'])
    tempoAtual = tempoAtual*sr
    y = y[int(tempoAtual):]
    # Start audio processing in a background thread
    audio_thread = threading.Thread(target=player_audio, args=(y, sr), daemon=True)
    audio_thread.start()

    # Start the Pygame window in the main thread
    balls_simulation()

def player_audio(y, sr):
    global delta
    delta = datetime.now() - timedelta(seconds=srtTime)
    with sd.OutputStream(callback=callback, channels=1, samplerate=sr):
        sd.play(y, samplerate=sr)
        sd.wait()
