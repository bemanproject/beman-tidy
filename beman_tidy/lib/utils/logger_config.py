import logging
import sys

# an object that always redirects to the stdout stream
class DynamicStdoutStream:
    def write(self, data):
        sys.stdout.write(data)
    
    def flush(self):
        sys.stdout.flush()

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        force=True,
        stream=DynamicStdoutStream(),
    )
