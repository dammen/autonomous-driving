""" Module that tests multiple models at multiple tracks """
#pylint: disable=invalid-name
import os
import argparse
from autonomous_driver import game_loop

# Which model architecture to use
#model_type = "Spatial"
model_type = "Spatiotemporal"
#model_type = "Temporal"
models_path = "Training/" + model_type + "/Stored_models/"

# Which models to test
all_models = False
chosen_folders = [14]

# Which checkpoints to test
train_loss = False
val_loss = True
best_checkpoint_only = True
threshold_epoch = 2 # Only applicable if best_checkpoint_only is false

# Define which tracks to test
# Town 1 has 4 possible tracks
# Town 2 has 3 possible tracks
town = 1
tracks_town_1 = [0]
tracks_town_2 = [0, 1, 2]


def get_paths(dir_path, split_on, sort_idx):
    """ Returns a sorted list of paths to the folders located in dir_path"""
    paths = []
    for f in os.listdir(dir_path):
        if f == ".DS_Store" or f == "store.h5":
            continue
        paths.append(dir_path + "/" + f)
    paths.sort(key=lambda a: int(a.split(split_on)[sort_idx]))
    return paths


# Fetch the models to test
if all_models:
    data_paths = get_paths(models_path, "/", -1)
else:
    data_paths = []
    for folder in chosen_folders:
        data_paths.append(models_path + str(folder))

best_loss_models = []
best_val_models = []

for path in data_paths:
    checkpoints = get_paths(path + "/Checkpoints", "-", 1)
    checkpoints.reverse()
    best_val_checkpoints = [c for c in checkpoints if "val_loss" in c]
    best_train_checkpoints = [c for c in checkpoints if "train_loss" in c]
    if train_loss:
        for checkpoint in best_train_checkpoints:
            if best_checkpoint_only:
                best_val_models.append(checkpoint)
                break
            else:
                if int(checkpoint.split("-")[1]) > threshold_epoch:
                    best_val_models.append(checkpoint)
    if val_loss:
        for checkpoint in best_val_checkpoints:
            if best_checkpoint_only:
                best_val_models.append(checkpoint)
                break
            else:
                if int(checkpoint.split("-")[1]) > threshold_epoch:
                    best_val_models.append(checkpoint)

# Define arguments for the carla client

argparser = argparse.ArgumentParser(
    description='CARLA Manual Control Client')
argparser.add_argument(
    '--path',
    default='Test_recordings',
    help='Where to store data')
argparser.add_argument(
    '-v', '--verbose',
    action='store_true',
    dest='debug',
    help='print debug information')
argparser.add_argument(
    '--host',
    metavar='H',
    default='127.0.0.1',
    help='IP of the host server (default: 127.0.0.1)')
argparser.add_argument(
    '-p', '--port',
    metavar='P',
    default=2000,
    type=int,
    help='TCP port to listen to (default: 2000)')

# Test the models

waypoints_town_1 = [
    #[181, 24],
    [150, 24],
    [200, 70],
    [49, 209],
    [60, 27],
]
waypoints_town_2 = [
    [30, 81],
    [12, 6],
    [46, 45]
]
if town == 1:
    for model in best_val_models:
        for track in tracks_town_1:
            args = argparser.parse_args()
            args.model = model
            args.model_type = model_type
            args.waypoints = waypoints_town_1[track]
            game_loop(args)

if town == 2:
    for model in best_val_models:
        for track in tracks_town_2:
            args = argparser.parse_args()
            args.model = model
            args.waypoints = waypoints_town_2[track]
            game_loop(args)