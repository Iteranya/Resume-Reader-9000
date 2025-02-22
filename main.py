from pipeline  import MainPipeline
import time


if __name__ == "__main__":

    # Instantiate the pipeline with the path to your TinyDB JSON file.
    pipeline = MainPipeline(5)
    pipeline.start()

    try:
        # Keep the main thread alive while the background thread runs.
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pipeline.stop()
        print("Pipeline stopped.")