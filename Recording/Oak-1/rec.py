#!/usr/bin/env python3
from multiprocessing.sharedctypes import Value
import depthai as dai
import contextlib
import time
from pathlib import Path
import signal
import threading

# DepthAI Record library
from depthai_sdk import Record
from depthai_sdk.managers import ArgsManager
import argparse

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-p', '--path', default="recordings", type=str, help="Path where to store the captured data")
args = ArgsManager.parseArgs(parser)

save_path = Path.cwd() / args.path

# Host side sequence number syncing
def checkSync(queues, sequenceNum: int):
    matching_frames = []
    for q in queues:
        for i, msg in enumerate(q['msgs']):
            if msg.getSequenceNum() == sequenceNum:
                matching_frames.append(i)
                break

    if len(matching_frames) == len(queues):
        # We have all frames synced. Remove the excess ones
        for i, q in enumerate(queues):
            q['msgs'] = q['msgs'][matching_frames[i]:]
        return True
    else:
        return False

def run():
    with contextlib.ExitStack() as stack:
        # Record from all available devices
        device_infos = dai.Device.getAllAvailableDevices()

        if len(device_infos) == 0:
            raise RuntimeError("No devices found!")
        else:
            print("Found", len(device_infos), "devices")

        devices = []
        # TODO: allow users to specify which available devices should record
        for device_info in device_infos:
            openvino_version = dai.OpenVINO.Version.VERSION_2021_4
            device = stack.enter_context(dai.Device(openvino_version, device_info, usb2Mode=False))

            # Create recording object for this device
            recording = Record(save_path, device, args)

            # Set recording configuration
            recording.setRecordStreams(["color", "left", "right"])
            recording.setQuality("HIGH")

            devices.append(recording)

        for recording in devices:
            recording.start() # Start recording

        # Terminate app handler
        quitEvent = threading.Event()
        signal.signal(signal.SIGTERM, lambda *_args: quitEvent.set())
        print("\nRecording started. Press 'Ctrl+C' to stop.")

        while not quitEvent.is_set():
            try:
                for recording in devices:
                    # Loop through device streams
                    for q in recording.queues:
                        new_msg = q['q'].tryGet()
                        if new_msg is not None:
                            q['msgs'].append(new_msg)
                            if checkSync(recording.queues, new_msg.getSequenceNum()):
                                # Wait for Auto focus/exposure/white-balance
                                recording.frameCntr += 1
                                
                                frames = dict()
                                for stream in recording.queues:
                                    frames[stream['name']] = stream['msgs'].pop(0)
                                recording.frame_q.put(frames)

                time.sleep(0.001) # 1ms, avoid lazy looping
            except KeyboardInterrupt:
                break

        print('') # For new line in terminal
        for recording in devices:
            recording.frame_q.put(None)
            recording.process.join()  # Terminate the process
        print("All recordings have stopped successfuly. Exiting the app.")

if __name__ == '__main__':
    run()
