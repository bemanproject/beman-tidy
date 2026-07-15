import logging
import sys

# an object that always redirects to the stdout stream
class DynamicStdoutStream:
    @staticmethod
    def write(data):
        sys.stdout.write(data)
    
    @staticmethod
    def flush():
        sys.stdout.flush()

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        force=True,
        stream=DynamicStdoutStream(),
    )
