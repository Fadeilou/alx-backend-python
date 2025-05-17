#!/usr/bin/python3
import sys
processing = __import__('1-batch_processing')

##### print processed users in a batch of 50
try:
    processing.batch_processing(50)
except BrokenPipeError:
    # This handles cases where the output pipe is closed early (e.g., by `| head`)
    # to prevent a BrokenPipeError from being printed to stderr.
    sys.stderr.close()
